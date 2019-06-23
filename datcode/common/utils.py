# import bcrypt
import re
import pytz

from dateutil.parser import parse
from dateutil.tz import tzlocal


UUID_RE = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
USERNAME_RE = r'^[a-zA-Z\_0-9]{4,12}$'


def normalize(string):
    string = string.strip().replace(' ', '-').lower()

    return string


def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]

    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]


def parse_search_string(search):
    """function used to create a cheap-o search engine in sql(ite)"""
    user_re = r'(\@[\w\d-]+)'
    tag_re = r'(\#[\w\d-]+)'

    # get the list of users and tags
    users = re.findall(user_re, search, flags=re.IGNORECASE)
    users = [u[1:] for u in users]
    tags = re.findall(tag_re, search, flags=re.IGNORECASE)
    tags = [t[1:] for t in tags]

    # clean up the search by removing all of the users and all of the tags
    cleaned = re.sub(user_re, '', search)
    cleaned = re.sub(tag_re, '', cleaned)
    cleaned = re.sub(r'\W', ' ', cleaned)
    cleaned = re.sub(r'\s{1,}', ' ', cleaned).lower()
    cleaned = cleaned.strip()

    # add all of the parts as potential tags
    parts = cleaned.split(' ')
    parts = list(filter(None, parts))
    # tags += parts
    tags = list(filter(None, tags))
    ps = list(powerset(parts))
    ps = list(filter(None, ps))
    searches = [' '.join(p) for p in ps]
    searches = list(filter(None, searches))

    return {
        'users': users,
        'tags': tags,
        'search': {
            'original': search,
            'contains': searches,
        },
    }


def strip_tags(string):
    """lets remove html tags"""
    try:
        len(string)

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(string, 'html.parser')

        return soup.get_text()
    except:
        return string


def encrypt_password(password):
    import bcrypt
    return password
    # password = password.encode('utf-8')
    # pw = bcrypt.hashpw(password, bcrypt.gensalt())

    # return pw.decode('utf-8')


def check_password(password, user_password):
    import bcrypt
    return password == user_password
    # password = password.encode('utf-8')
    # user_password = user_password.encode('utf-8')

    # return bcrypt.checkpw(password, user_password)


def iso_date_to_utc(iso_date):
    date = parse(iso_date)
    
    return date.astimezone(pytz.utc)


def hased_name_path(name, split=3):
    """
    function used to get a current path based on a hash
    of the current time in milliseconds and filename
    """
    import hashlib
    import time
    import os
    import uuid

    hashed = str(uuid.uuid4()).replace('-', '')
    splits = [hashed[i:i + split] for i in range(0, len(hashed), split)]
    path = os.path.join(*splits)

    return path, hashed
