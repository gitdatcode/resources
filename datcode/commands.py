"""this file holds all of the commands that will help create a cli interface
into the datcode api"""

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


def update_user(slack_id, params):
    """This will update or create a user by its slack_id. The params
    should be a json string `{"username": "mark"}`
    The only fields that can be updated are: username, email_address, private<bool>
    """
    import json

    from datcode.bootstrap import MAPPER
    from datcode.common.model.graph.node import User


    allowed_update_params = ['username', 'email_address', 'private']
    user_mapper = MAPPER.get_mapper(User)
    user_mapper.ensure_privacy = False

    try:
        params = json.loads(params)
    except Exception as e:
        print(('There was an error with loading the json: {}').format(e))
        return

    # filter out unallowed params
    new_params = {k:v for k, v in params.items() if k in allowed_update_params}

    try:
        user = user_mapper.get_by_slack_id(slack_id)
    except:
        user = user_mapper.create()

    new_params['slack_id'] = slack_id
    user.hydrate(new_params)

    try:
        work = user_mapper.save(user)
        work.send()
    except Exception as e:
        print(('There was an error with loading the json: {}').format(e))
        return

    data =  user_mapper.data(user)

    print(data)
