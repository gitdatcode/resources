"""
defines all of the api routes
"""
from .controller.api import ApiController
from .controller.auth.login import LoginController
from .controller.auth.logout import LogoutController
from .controller.auth.password import (AuthPasswordForgotController,
    AuthPasswordResetController)
from .controller.resource.resource import (InternalSlackResourceController,
    ResourceSearchController)

from datcode.common.utils import UUID_RE


ROUTES = (
    (r'/api', ApiController),

    # auth
    (r'/api/login', LoginController),
    (r'/api/logout', LogoutController),
    (r'/api/password/forgot', AuthPasswordForgotController),
    (r'/api/password/reset/('+ UUID_RE +')', AuthPasswordResetController),

    # resources
    (r'/api/resource/search', ResourceSearchController),

    # internal slack api calls
    # (r'/api/slack/resource', InternalSlackResourceController),
)
