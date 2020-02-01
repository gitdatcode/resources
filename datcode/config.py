import os
import sys

from tornado.options import (options, define, parse_config_file,
    parse_command_line)


HERE = os.path.dirname(__file__)
CONFIGS_DIR = os.path.join(HERE, 'configs')
CLIENT_DIR = os.path.abspath(os.path.join(HERE, '..', 'client'))
HOUR = 60 * 60
DAY = 24 * HOUR


# check the local environment file to see which environment we're in
try:
    ENVIRONMENT = os.environ.get('datcode_environment', None)

    if not ENVIRONMENT:
        raise Exception()
except Exception:
    try:
        with open('{}/environment'.format(HERE), 'r') as f:
            ENVIRONMENT = f.readline().lower().strip()
    except Exception:
        ENVIRONMENT = 'development'


# App configurations
define('environment', ENVIRONMENT)
define('debug', True if ENVIRONMENT in ['development', 'testing'] else False)
define('autoreload', True if ENVIRONMENT in ['development', 'testing'] else False)
define('pagination', 20, help='the number of results to return per page')
define('password_reset_timeout', 60 * 60 * 24)
define('client_dir', CLIENT_DIR)
define('upload_dir', os.path.join(CLIENT_DIR, 'assets', 'upload'))
define('default_lang', 'en_gb')
define('ports', [9292], help='ports that the app will run on', multiple=True)
define('user_cookie_name', 'u')
define('template_path', os.path.join(HERE, 'common', 'view', 'template'))


# moesha neo4j settings
define('moesha_host', '127.0.0.1')
define('moesha_port', 7687)
define('moesha_user', 'neo4j')
define('moesha_password', 'datcode_app')


# error and other notifications
define('notify_errors', True)
define('error_email', ['emehrkay@gmail.com',], multiple=True)
define('feedback_email', ['emehrkay@gmail.com',], multiple=True)


# Email AWS SES
define('from_email', 'mark@invee.io')
define('aws_access_key_id', '')
define('aws_secret_access_key', '')
define('aws_region', 'us-east-1')


# load the local override config
local_override = os.path.join(CONFIGS_DIR, '{}.config.py'.format(ENVIRONMENT))

if os.path.isfile(local_override):
    parse_config_file(local_override, final=False)


# load the cli flags to override pre-defined config settings
# remove app.py if it is the first arg. This is done because starting the sever
# by running python app.py start_server --arg=value is not parsable by
# tornado's parse_command_line function
args = sys.argv[:]

if args[0] == 'app.py':
    args = args[1:]

parse_command_line(args=args)
