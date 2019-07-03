# from tornado import httpserver, ioloop

# from datcode.config import options
# from datcode.bootstrap import create_application


# try:
#     for port in options.ports:
#         application = create_application()
#         http_server = httpserver.HTTPServer(application)

#         print('TENANT STARTED ON PORT: ', port)

#         http_server.listen(port)

#     ioloop.IOLoop.current().start()
# except Exception as e:
#     print(e)

# REMOVE
import os

# use the testing database
os.environ['datcode_environment'] = 'testing'
# END REMOVE

import inspect
import sys

from datcode.commands import (add_resource, search_resources, update_user,
    start_server)


COMMANDS = {
    'start_server': start_server,
    'add_resource': add_resource,
    'search_resources': search_resources,
    'update_user': update_user,
}

def resources_help():
    docs = []
    lb = '*' * 140

    for c, f in COMMANDS.items():
        doc = '\n{}:\n    {}\n\n{}\n'.format(c, inspect.getdoc(f), lb)
        docs.append(doc)

    docs = ''.join(docs)

    return docs


if __name__ == '__main__':
    args = sys.argv[1:]

    if not len(args):
        print(resources_help())
    elif args[0] in COMMANDS:
        COMMANDS[args[0]](*args[1:])
    else:
        print(resources_help())