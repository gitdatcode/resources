from moesha.mapper import MapperConstraintError


class ApiException(Exception):

    def __init__(self, message=None, errors=None, status_code=403):
        self.message = message or ''

        if errors:
            if not isinstance(errors, (list, set, tuple)):
                errors = [errors,]
        else:
            errors = []

        self.errors = errors
        self.status_code = status_code


class ApiEntityException(ApiException):
    pass


class ApiModelGraphMixinException(ApiException):
    pass


def convert_exeception(exception):

    if isinstance(exception, MapperConstraintError):
        data = exception.data
        errors = ('The field {field} is not available'.format(
            field=data['field']))
        exe = ApiException(errors=errors, status_code=422)

        return exe

    return exception
