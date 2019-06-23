from pypher.builder import __, Param

from tornado.options import options
from tornado.web import MissingArgumentError


class Paginator(object):
    """This class is used to add pagination, filtering, and ordering to a
    Cypher query built with Pypher.

    This class is used when returning a collection of Entities, ie, get all
    users via /users

    Two things need to happen in order to utilize the functionality:
    1. The controller must define an order_by and filter_by member that lists
       the fileds that this class can use.
       order_by = ['name', 'location']
       filter_by = ['name', 'location', 'age']
       The fields must exist in the Entity that is being queried.

    2. A query string must be added to the request

    Ordering the results work by adding an `order=field` value to the query
    string, multiple can be added. If an order_by_defaults member is defined
    on the controller, those fields will be added to the ordering, even if
    they are not passed in with the query string.
        /users?order=name -- this will order by name ascending
        /users?order=-name -- this will order by name descending
        /users?order=-name&order=location -- this will order by name
            descending and location ascending

    All filtering is a CONTAINS or NOT CONTAINS WHERE clause. Each clause
    is an AND statment:
        /user?name=mark -- This will check for names that have mark in them
        /user?name=!mark -- This will check for names that does not have mark
            in them

    To paginate you will pass a 1-based page in the query string. The result
    returned from the server will have the total number of records, including
    filtering, the current page, and the per_page count.
        /users?page=2 -- will get the second set of users 20 - 40

    All of the query string options can be combined and used together
    """

    def __init__(self, controller):
        self.controller = controller
        self.mapper = controller.mapper

    @property
    def pagination(self):
        page = int(self.controller.get_arg('page', 0))
        start = max(page - 1, 0) * options.pagination
        end = start + options.pagination
        self.controller.paginate_page = page

        return {
            'count': options.pagination,
            'page': page,
            'start': start,
            'end': end,
        }

    def get_mapped_query_variable(self, var):
        qvr = self.controller.relationship_query_variable_map

        return qvr.get(var, var)

    def filtering(self, query_variable):
        wheres = []
        fields = self.controller.filter_by

        for i, field in enumerate(fields):
            try:
                if '.' in field:
                    splits = field.split('.')
                    field = splits[-1]
                    query_variable = splits[0]

                value = self.controller.get_argument(field)
            except MissingArgumentError as e:
                # we will swallow these, but let the others proprogate
                continue

            if value:
                exclude = False
                clause = __()

                if value[0] == '!':
                    exclude = True
                    value = value[1:]

                if exclude:
                    clause = clause.NOT

                query_variable = self.get_mapped_query_variable(query_variable)
                name = '{}_{}'.format(field, i).replace('.', '_')
                value = Param(name, value)
                clause = getattr(clause, query_variable).property(field)
                clause = clause.CONTAINS(value)
                wheres.append(clause)

        return wheres

    def ordering(self, query_variable):
        orders = []
        defaults = self.controller.order_by_defaults
        values = self.controller.get_arguments('order')

        for default in defaults:
            # if '.' in default:
            #     default = default.split('.')[-1]

            fix_def = default.strip('-')
            neg_def = '-' + default

            if fix_def not in values and neg_def not in values:
                values.append(default)

        for val in values:
            desc = False

            if val[0] == '-':
                val = val[1:]
                desc = True

            if val not in self.controller.order_by:
                continue

            if '.' in val:
                parts = val.split('.')
                query_variable = self.get_mapped_query_variable(parts[0])
                val = parts[1]

            if val == 'id':
                clause = __.id(query_variable)
            else:
                clause = getattr(__, query_variable).property(val)

            if desc:
                clause = clause.DESC

            orders.append(clause)

        return orders

    def paginate(self, pypher, query_variable, allow_filtering=True,
                 alias='matched'):
        pagination = self.pagination

        if allow_filtering:
            wheres = self.filtering(query_variable)
        else:
            wheres = None

        # get the total count and add it to the current request to be used in
        # the response pagiantion
        count = pypher.clone()

        if wheres:
            count.WHERE.CAND(*wheres)

        count.WITH(query_variable)
        count.ALIAS(alias).RETURN.func_raw('COUNT', query_variable)
        resp = self.mapper.query(count).first()
        self.controller.paginate_total = resp['result']

        # add the filtering, ordering, and pagination to the original query
        # TODO: add filtering logic

        if wheres:
            pypher.WHERE.CAND(*wheres)

        pypher.RETURN(query_variable)

        ordering = self.ordering(query_variable)

        if ordering:
            pypher.ORDER.BY(*ordering)

        pypher.SKIP(pagination['start']).LIMIT(pagination['count'])

        return pypher
