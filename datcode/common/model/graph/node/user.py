from . import BaseNode, BaseNodeMapper

from moesha.entity import Collection
from moesha.property import (String, Integer, Float, Boolean, TimeStamp,
    DateTime, RelatedEntity)

from datcode.common.utils import (encrypt_password, check_password)
from datcode.common.model.graph.mixin import HasOwnership
from datcode.common.model.acl import Roles
from .login_log import LoginLog


class User(BaseNode):
    
    def check_password(self, password):
        return check_password(self['password'], password)

    def update_password(self, new_password1, new_password2):
        if new_password1 != new_password2:
            return False

        self['password'] = encrypt_password(new_password1)

        return self


class UserMapper(BaseNodeMapper, HasOwnership):
    from datcode.common.model.graph.relationship import (AddedResource,
        RequestedPasswordReset)

    # Flag for user models that says to mask the username
    ensure_privacy = True

    entity = User
    __PROPERTIES__ = {
        'username': String(),
        'password': String(),
        'bio': String(),
        'slack_id': String(),
        'email_address': String(),
        'verified': Boolean(default=False),
        'private': Boolean(default=True),
        'first_name': String(),
        'last_name': String(),
        'middle_name': String(),
        'access_level': Integer(default=Roles.USER.value),
        'registration_step': Integer(),
    }
    __RELATIONSHIPS__ = {
        'PasswordResetRequest': RelatedEntity(
            relationship_entity=RequestedPasswordReset),
        'Resources': RelatedEntity(relationship_entity=AddedResource,
            ensure_unique=True),
    }

    def data(self, entity):
        if isinstance(entity, Collection):
            return [self.data(e) for e in entity]

        data = super().data(entity)

        if 'username' in data and self.ensure_privacy and entity['private']:
            data['username'] = 'SOME PRIVATE USER'

        if 'password' in data:
            del data['password']

        return data

    def update_password(self, user, password, password_check):
        if password != password_check:
            raise Exception('Determine correct exception')

        user['password'] = encrypt_password(password)

        self.mapper.save(user).send()

        return user

    def get_by_slack_id(self, slack_id):
        pypher = self.builder()
        pypher.WHERE.CAND(pypher.entity.__slack_id__ == slack_id)
        pypher.RETURN(pypher.entity)

        user = self.mapper.query(pypher=pypher)

        return user.first()

    def get_by_email(self, email_address):
        pypher = self.builder()
        pypher.WHERE.CAND(pypher.entity.__email_address__ == email_address)
        pypher.RETURN(pypher.entity)

        user = self.mapper.query(pypher=pypher)

        return user.first()

    def get_by_email_password(self, email_address, password):
        password = encrypt_password(password)
        pypher = self.builder()
        pypher.WHERE.CAND(pypher.entity.__email_address__ == email_address,
            pypher.entity.__password__ == password)
        pypher.RETURN(pypher.entity)

        user = self.mapper.query(pypher=pypher)

        return user.first()

    def auth_user(self, email_address, password):
        login = LoginLog(properties={'email_address': email_address})

        self.mapper.save(login).send()

        try:
            user = self.get_by_email_password(email_address, password)
            login['success'] = True

            self.mapper.save(login).send()

            return user
        except:
            return None

    def on_after_create(self, entity, response=None, **kwargs):
        # send out a registration email to the user
        email = entity['email_address']
        params = {}
        if email:
            self.email_html(to=email, key='new_user', **params)

    def request_password_change(self, user):
        from datcode.common.model.graph.node import PasswordReset

        code = self.mapper.create(entity=PasswordReset)
        _, work = self.mapper(user)['PasswordResetRequest'].add(code)
        _, work = self.add_ownership(user, code, work=work, submit=False)
        work.send()

        return code

    def on_password_property_changed(self, entity, field, value_from,
                                     value_to):
        """
        Send the user an email if their password has changed
        """
        email = entity['email_address']
        params = {}

        self.email_html(to=email, key='password_changed', **params)

    def on_relationship_passwordresetrequest_added(self, entity, response,
                                                   relationship_entity,
                                                   relationship_end, **kwargs):
        """
        This will send out an email once the password reset change has been
        added for a given user
        """
        email = entity['email_address']
        params = {
            'uri': 'some.url.com',
        }

        self.email_html(to=email, key='password_reset_request', **params)
