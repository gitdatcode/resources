from pypher.builder import Pypher, __

from moesha.entity import Node, Relationship
from moesha.property import String, Boolean, RelatedEntity
from moesha.util import _query_debug

from . import BaseNode, BaseNodeMapper
from ..relationship import HasTag
from datcode.common.model.graph.mixin import HasOwnership
from datcode.common.utils import parse_search_string, normalize
from datcode.config import options


class Resource(BaseNode):
    pass


class ResourceMapper(BaseNodeMapper, HasOwnership):
    entity = Resource
    __PROPERTIES__ = {
        'title': String(),
        'description': String(),
        'uri': String(),
    }
    __RELATIONSHIPS__ = {
        'Tags': RelatedEntity(relationship_entity=HasTag, ensure_unique=False)
    }

    def save_resource(self, resource, *tags, work=None):
        work = work or self.mapper.get_work()
        work = self.save(resource, work=work)
        work = self(resource)['Tags'].replace(tags, work=work)

        work.send()

    def get_by_uri(self, uri):
        pypher = self.builder()
        pypher.WHERE.CAND(pypher.entity.__uri__ == uri)
        pypher.RETURN(pypher.entity)

        resource = self.mapper.query(pypher=pypher)

        return resource.first()

    def get_by_search_string_old(self, search_string, ensure_privacy=True,
                             limit=options.pagination, skip=0):
        """based on a search string of:
            pyhon #code @mark
        build a query with the foundation of:

        MATCH (tag_resource:`Resource`)-[:`HasTag`]->(tag:`Tag`)
        WHERE tag.tag_normalized = 'code' 
        WITH tag_resource 
        MATCH (user_resource:`Resource`)<-[:`AddedResource`]-(user:`User`) 
        WHERE id(user_resource) = id(tag_resource) 
        WITH user_resource, user 
        MATCH (resource:`Resource`)-[:`HasTag`]->(tag:`Tag`) 
        id(resource) = id(user_resource)
        RETURN resource, user, collect(tag)
        """
        from datcode.common.model.graph.node import User


        search = parse_search_string(search_string)
        user_mapper = self.get_mapper(User)
        user_mapper.ensure_privacy = ensure_privacy

        p = Pypher()
        p.node('resource', labels='Resource')
        p.rel_in(labels='AddedResource').node('user', labels='User')

        p2 = Pypher()
        p2.node('resource').rel_out(labels='HasTag').node('tag', labels='Tag')

        p2 = Pypher()
        p2.node('resource').rel_out(labels='HasTag').node('tag', labels='Tag')

        p3 = Pypher()
        p3.node('resource').rel_out(labels='HasTag').node('tags', labels='Tag')

        query = Pypher()
        query.MATCH(p, p2, p3)

        wheres = []
        search_ors = []
        user_ors = []
        tag_ors = []

        # filter the resource title and descripiton by search string powersets
        for contains in search['search']['contains']:
            term = ".*{}.*".format(contains)
            d = Pypher()
            t = Pypher()
            d.resource.__description__.re(term)
            t.resource.__title__.re(term)
            search_ors.append(d)
            search_ors.append(t)

        if search_ors:
            ors = Pypher()
            ors.COR(*search_ors)
            wheres.append(ors)

        # filter by users
        for user in search['users']:
            u = Pypher()
            u.user.__username__ == user
            user_ors.append(u)

        if user_ors:
            ors = Pypher()
            ors.COR(*user_ors)
            wheres.append(ors)

        # filter by tags
        for tag in search['tags']:
            u = Pypher()
            u.tag.__tag_normalized__ == normalize(tag)
            tag_ors.append(u)

        if tag_ors:
            ors = Pypher()
            ors.COR(*tag_ors)
            wheres.append(ors)

        if wheres:
            query.WHERE.CAND(*wheres)

        # paginate and get a total count
        total = query.clone()
        total.RETURN('COUNT(DISTINCT(resource)) AS total')

        total_res = self.mapper.query(pypher=total)

        try:
            total_results = total_res.first()['result']
        except:
            total_results = 0

        query.RETURN('DISTINCT(resource)', 'user', 'COLLECT(tags) as tags')
        query.SKIP(skip).LIMIT(limit)
        results = self.mapper.query(pypher=query)

        return {
            'total': total_results,
            'results': results.entity_data,
        }
 

    def get_by_search_string(self, search_string, ensure_privacy=True,
                             limit=options.pagination, skip=0):
        """based on a search string of:
            pyhon #code @mark
        build a query with the foundation of:

        MATCH (tag_resource:`Resource`)-[:`HasTag`]->(tag:`Tag`)
        WHERE tag.tag_normalized = 'code' 
        WITH tag_resource 
        MATCH (user_resource:`Resource`)<-[:`AddedResource`]-(user:`User`) 
        WHERE id(user_resource) = id(tag_resource) 
        WITH user_resource, user 
        MATCH (resource:`Resource`)-[:`HasTag`]->(tag:`Tag`) 
        id(resource) = id(user_resource)
        RETURN resource, user, collect(tag)
        """
        from datcode.common.model.graph.node import User


        search = parse_search_string(search_string)
        user_mapper = self.get_mapper(User)
        user_mapper.ensure_privacy = ensure_privacy

        # build the tag portion of the search query
        tag_ors = []
        tag_q = Pypher()
        tag_q.MATCH.node('tag_resource', 'Resource').rel_out(labels='HasTag')
        tag_q.node('tag', 'Tag')

        for tag in search['tags']:
            u = Pypher()
            u.tag.__tag_normalized__ == normalize(tag)
            tag_ors.append(u)

        if tag_ors:
            tag_q.WHERE(__.COR(*tag_ors))

        tag_q.WITH('tag_resource')

        # build the user portion of the search query
        user_ors = []
        user_q = Pypher()
        user_q.MATCH.node('user', 'User')
        user_q.rel_out(labels='AddedResource')
        user_q.node('user_resource', 'Resource')

        for user in search['users']:
            u = Pypher()
            u.user.__username__ == user
            user_ors.append(u)

        from_tags = __.ID('tag_resource') == __.ID('user_resource')

        if user_ors:
            user_ors = __.COR(*user_ors)
            user_q.WHERE(__.CAND(from_tags, user_ors))
        else:
            user_q.WHERE(from_tags)

        user_q.WITH('user_resource', 'user')

        # build the final search query
        search_ors = []
        wheres = []
        query = Pypher()
        query.append(tag_q).append(user_q)
        query.MATCH.node('resource', 'Resource').rel_out(labels='HasTag')
        query.node('tags', 'Tag')

        for contains in search['search']['contains']:
            term = ".*{}.*".format(contains)
            d = Pypher()
            t = Pypher()
            d.resource.__description__.re(term)
            t.resource.__title__.re(term)
            search_ors.append(d)
            search_ors.append(t)

        wheres.append(__.ID('user_resource') == __.ID('resource'))

        if search_ors:
            ors = Pypher()
            ors.COR(*search_ors)
            wheres.append(ors)

        query.WHERE(*wheres)

        # paginate and get a total count
        total = query.clone()
        total.RETURN('COUNT(DISTINCT(resource)) AS total')

        total_res = self.mapper.query(pypher=total)

        try:
            total_results = total_res.first()['result']
        except:
            total_results = 0

        if ensure_privacy:
            user_ret = 'user{username:"DATCODE-USER"} as user'
        else:
            user_ret = 'user{.username} as user'

        query.RETURN('DISTINCT(resource)', user_ret,
            'COLLECT(tags) as tags')
        query.SKIP(skip).LIMIT(limit)
        results = self.mapper.query(pypher=query)

        return {
            'total': total_results,
            'results': results.entity_data,
        }
 