from moesha.property import String, Boolean

from pypher.builder import __

from . import BaseNode, BaseNodeMapper
from datcode.common.utils import normalize

class Tag(BaseNode):
    pass


class TagMapper(BaseNodeMapper):
    entity = Tag
    __PROPERTIES__ = {
        'tag': String(ensure_unique=True),
        'tag_normalized': String(),
    }

    def get_or_create_by_tags(self, *tags):
        if len(tags) == 0:
            raise Exception('Must pass in at least one tag')

        work = self.get_work()

        for t in tags:
            props = {
                'tag': t,
                'tag_normalized': normalize(t),
            }
            tag = self.create(properties=props)
            work = self.save(tag, work=work)
        return work.send()

    def get_tags_by_tags(self, *tags):
        if len(tags) == 0:
            raise Exception('Must pass in at least one tag')

        normalized_tags = map(normalize, tags)
        wheres = []

        for nt in normalized_tags:
            wheres.append(__().__tag_normalized__ == nt)

        pypher = self.builder()
        pypher.WHERE.COR(*wheres)
        pypher.RETURN(pypher.entity)

        return self.mapper.query(pypher=pypher)
