

def add_resource(title, description, uri, tags, date_created, username,
                 slack_id):
    """method that will allow dobot to add resources directly to the database

    example:
        add_resource "cool js feature" "this shows you how to do feature" "website.com" "js,code, some tag" "2019-03-01" "mark" "3324"
    """
    from datcode.bootstrap import MAPPER
    from datcode.common.model.graph.node import Tag, Resource, User

    user_mapper = MAPPER.get_mapper(User)
    resource_mapper = MAPPER.get_mapper(Resource)
    tag_mapper = MAPPER.get_mapper(Tag)
    work = MAPPER.get_work()

    try:
        user = user_mapper.get_by_slack_id(slack_id)
    except:
        props = {
            'slack_id': slack_id,
        }
        user = user_mapper.create(properties=props)
    finally:
        user['username'] = username
        work = MAPPER.save(user, work=work)

    udpate_resource = True
    try:
        resource = resource_mapper.get_by_uri(uri)

        # check that the current user is the owner
        # if not return an error
        if not resource_mapper.is_owner(user, resource):
            print('resource already exists')
            udpate_resource = False
            return
    except:
        props = {
            'uri': uri,
        }
        resource = resource_mapper.create(properties=props)
    finally:
        if udpate_resource:
            resource['title'] = title
            resource['description'] = description
            work = MAPPER.save(resource, work=work)

    try:
        tags = tag_mapper.get_or_create_by_tags(*tags.split(','))
    except Exception as e:
        print(e)
        return

    _, work = user_mapper.add_ownership(user, resource, work=work)
    _, work = user_mapper(user)['Resources'].add(resource, work=work)
    work = resource_mapper(resource)['Tags'].replace(tags, work=work)

    work.send()


def search_resources(search_string):
    """This will return resources based on a querystring-based search

    example:
        search_resources "python #js shows @username"
    """
    from datcode.bootstrap import MAPPER
    from datcode.common.model.graph.node import Resource

    resource_mapper = MAPPER.get_mapper(Resource)
    res = resource_mapper.get_by_search_string(search_string)
    print(res)
