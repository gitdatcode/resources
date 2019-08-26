from datcode.bootstrap import options
from datcode.api.controller import BaseAPIController
from datcode.common.model.graph.node.resource import Resource
from datcode.common.controller.decorator import request_fields
from datcode.commands import add_resource


class ResourceController(BaseAPIController):
    request_entity = Resource


class ResourceSearchController(ResourceController):

    def get(self):
        search = self.get_argument('search', '')
        page = int(self.get_argument('page', 0))

        # import pudb; pu.db
        self.paginate_page = page
        if page > 1:
            page = max(page - 1, 0)

        limit = options.pagination
        skip = page * limit

        # @TODO: fix the ensure_privacy flag
        results = self.request_mapper.get_by_search_string(search, skip=skip,
            limit=limit, ensure_privacy=False)

        # convert results to final response pagination
        self.paginate_total = results['total']
        data = results['results']

        return self.json(data=data)


class InternalSlackResourceController(ResourceController):

    @request_fields({
        'required': ['slack_id', 'username', 'uri', 'tags:str',
            'date_created'],
        'optional': ['title', 'description',],
    })
    def post(self, resource_id=None):
        try:
            resource = add_resource(print_resource=False, **self.request_data)
        except Exception as e:
            pass

        return self.json(data=resource)
