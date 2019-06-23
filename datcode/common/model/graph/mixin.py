from moesha.property import RelatedEntity

from pypher.builder import __

from datcode import LOG
from datcode.common.exception import ApiModelGraphMixinException
from datcode.common.model.graph.relationship import Owns
from datcode.common.model.graph.partials import GetRelationshipBetween


class HasOwnership(object):

    def add_ownership(self, owner, entity, properties=None, submit=True,
                      work=None):
        properties = properties or {}
        rel = self.mapper.create(entity=Owns, start=owner, end=entity,
            properties=properties)

        try:
            work = self.mapper.save(rel, ensure_unique=True, work=work)

            if submit:
                work.send()

        except Exception as e:
            LOG.error(e)

        return rel, work

    def is_owner(self, owner, entity, relationship='Owns'):
        return self.has_connection(owner=owner, entity=entity,
            relationship=relationship)
