from moesha.mapper import StructuredRelationshipMapper
from moesha.entity import Relationship

from datcode.common.model.graph import BaseMapper


class BaseRelationship(Relationship):
    pass


class BaseRelationshipMapper(BaseMapper, StructuredRelationshipMapper):
    pass


from .added_resource import AddedResource, AddedResourceMapper
from .has_post import HasPost, HasPostMapper
from .has_role import HasRole, HasRoleMapper
from .has_tag import HasTag, HasTagMapper
from .owns import Owns, OwnsMapper
from .requested_password_reset import (RequestedPasswordReset,
    RequestedPasswordResetMapper)
