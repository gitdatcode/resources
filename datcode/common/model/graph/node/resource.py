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

        query.RETURN('DISTINCT(resource)', 'user')
        query.ORDERBY('resource.date_created', __.DESC)
        query.SKIP(skip).LIMIT(limit)
        results = self.mapper.query(pypher=query)
        result_data = []
        all_tags = []
        all_tag_ids = []

        for res in results:
            tags = self(res['resource'])['Tags']()
            username = res['user']['username']

            if ensure_privacy:
                username = 'DATCODE-USER'

            result_data.append({
                'resource': self.data(res['resource']),
                'user': {
                    'username': username,
                },
                'tags': self.data(tags),
            })

            for tag in tags:
                if tag.id not in all_tag_ids:
                    all_tags.append(tag.data)
                    all_tag_ids.append(tag.id)

        return {
            'total': total_results,
            'results': result_data,
            'all_tags': all_tags,
        }
 