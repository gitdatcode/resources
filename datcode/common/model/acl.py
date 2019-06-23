"""this module is used to configure the Access Control Lists"""
from enum import Enum


class Roles(Enum):
    ADMIN = 1
    USER = 2

    @classmethod
    def total(cls):
        return sum([r.value for r in cls])

    @classmethod
    def is_role(cls, user_role, role):
        return user_role & role

    @classmethod
    def is_admin(cls, user_role):
        return cls.is_role(user_role, cls.ADMIN.value)

    @classmethod
    def is_user(cls, user_role):
        return cls.is_role(user_role, cls.USER.value)


class Permmission(Enum):
    READ = 1
    WRITE = 2
    EDIT = 4

    @classmethod
    def total(cls):
        return sum([r.value for r in cls])

    @classmethod
    def has(cls, user_permission, permission):
        return user_permission & permission

    @classmethod
    def can_read(cls, user_permission):
        return cls.has(user_permission, cls.READ.value)

    @classmethod
    def can_write(cls, user_permission):
        return cls.has(user_permission, cls.WRITE.value)

    @classmethod
    def can_edit(cls, user_permission):
        return cls.has(user_permission, cls.EDIT.value)
