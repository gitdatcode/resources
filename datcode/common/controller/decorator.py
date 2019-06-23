import builtins
import functools

from datcode.common.model.messages import get_message
from datcode.common.exception import ApiEntityException, ApiException
from datcode.common.model.acl import Roles


def authorized(method):
    """
    simple decorator used to see if there is an authorized
    user for the request method
    """
    @functools.wraps(method)
    def _method(self, *args, **kwargs):
        try:
            self.get_current_user()
            res = method(self, *args, **kwargs)

            return res
        except ApiEntityException as e:
            return self.json(status=401, response='LOGIN_REQUIRED')
        except ApiException as e:
            raise e

    return _method


def owner_or_admin(method):
    """this decorator will check to see if the given resource is either owned
    by the user making the request or if the user making the request is
    an admin. If either are true, the user is granted access."""

    @functools.wraps(method)
    def _method(self, *args, **kwargs):

        def error(exception=None):
            return self.json(status=401, response='ACCESS_DENIED')

        def run():
            return method(self, *args, **kwargs)

        try:
            user = self.get_current_user()
        except Exception as e:
            return error(e)

        if not user:
            return error()

        if self.is_admin:
            return run()

        entity = self.get_entity_by_id(args[0])

        if entity == user:
            return run()

        if not entity:
            return error()

        if not self.is_owner(user, entity, 'Owns'):
            # @TODO: check here to see if the user has a connection to the entity or if the entity is a Relationship, check to see if the user is on the start end of it
            return error()

        return run()

    return _method


def is_admin(method):

    @functools.wraps(method)
    def _method(self, *args, **kwargs):
        if self.is_admin:
            return method(self, *args, **kwargs)

        return self.json(status=403, response='ACCESS_DENIED')

    return _method


def request_fields(fields=None):
    """this decorator serves three purposes:
        * it validates that the required fields are passed into the request
        * it will set the values of the required fields to a member of the
            controller as request_data
        * It will convert the field to a type if it is defined

        if all of the requirements are not met, it will return a 403 and a list
        of errors

    usage:
        @request_fields({
            'required': ['email', 'first_name', 'last_name:str',]
            'optional' : ['sex', 'age']
        })
        def get(self,...):
            ....
    """
    fields = fields or {}

    def get_field_type(field):
        parts = field.split(':')

        if len(parts) > 1:
            return parts[0], parts[1]

        return field, None


    def check(method):

        @functools.wraps(method)
        def inner(self, *args, **kwargs):
            data = {}
            errors = []
            required = fields.get('required', {})
            optional = fields.get('optional', {})

            def get_field_value(field, optional=False):
                field, field_type = get_field_type(field)
                value = self.get_arg(field, None)

                if not value and not optional:
                    msg = get_message('FIELD_REQURIED')
                    msg = (msg['message']).format(field=field)

                    errors.append(msg)

                    return field, None

                if value is None:
                    return field, value

                if field_type:
                    try:
                        if field_type in ['date', 'datetime']:
                            try:
                                # convert the value to be an ISO-8601 integer
                                date = iso_date_to_utc(value)
                                value = date.timestamp()
                            except:
                                msg = get_message('FIELD_TYPE_DATE_ERROR')
                                msg = (msg['message']).format(field=field,
                                    value=value)
                                errors.append(msg)
                                value = None
                        else:
                            value = getattr(builtins, field_type)(value)
                    except:
                        msg = get_message('FIELD_TYPE_MISMATCH')
                        msg = (msg['message']).format(field=field,
                            field_type=field_type)

                        errors.append(msg)
                        value = None

                return field, value

            for field in required:
                field, val = get_field_value(field)

                if val is not None:
                    data[field] = val

            for field in optional:
                field, val = get_field_value(field, True)

                if val is not None:
                    data[field] = val

            if len(errors):
                return self.json(status=422, errors=errors,
                    response='REQUIRED_FIELDS')
            else:
                self.request_data = data

                response = method(self, *args, **kwargs)

                return response
        return inner
    return check
