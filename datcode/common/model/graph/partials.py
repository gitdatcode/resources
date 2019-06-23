from pypher.builder import __
from pypher.partial import Partial

from moesha.entity import Node
from moesha.mapper import EQV


class GetRelationshipBetween(Partial):

    def __init__(self, start, end, relationships=None, direction='out'):
        super(GetRelationshipBetween, self).__init__()

        self.start = start
        self.end = end
        self.relationships = relationships
        self.direction = direction

    def build(self):
        pypher = self.pypher.MATCH
        rel_var = 'rel_var'
        wheres = []

        def entity(node):
            if isinstance(node, (list, set, tuple, str)):
                pypher.node(lables=node)
            elif isinstance(node, Node):
                var = EQV.define(node)
                pypher.node(var, labels=node.labels)

        def entity_where(entity):
            if entity.id:
                wheres.append(__.ID(entity.query_variable) == entity.id)

        entity(self.start)

        if self.direction == 'out':
            pypher.rel_out(rel_var, labels=self.relationships)
        elif self.direction == 'in':
            pypher.rel_in(rel_var, labels=self.relationships)
        else:
            pypher.rel(rel_var, labels=self.relationships)

        entity(self.end)

        entity_where(self.start)
        entity_where(self.end)

        if len(wheres):
            pypher.WHERE.CAND(*wheres)

        pypher.RETURN(rel_var)
