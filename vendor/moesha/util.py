import re
import time


__normal = re.compile('[\W_]+')


MOESHA_ENTITY_TYPE = '___MOE$H@_3NTITY_TYP3___'


def normalize(string):
    return __normal.sub('', string.lower())


def entity_to_labels(entity):
    if isinstance(entity, type):
        name = entity.__name__
    else:
        name = entity.__class__.__name__

    parts = name.strip('_').split('_')

    return normalize_labels(*parts)


def normalize_labels(*labels):
    if not labels:
        return ''

    labels = list(labels)
    labels.sort()

    return ':'.join(labels)


def entity_name(entity):
    if isinstance(entity, type):
        return '{}.{}'.format(entity.__module__, entity.__name__)
    else:
        return '{}.{}'.format(entity.__class__.__module__,
            entity.__class__.__name__)


def _query_debug(query, params):
    from string import Template

    if not params:
        return query

    temp = Template(query)
    fixed = {}

    for k, v in params.items():
        if isinstance(v, str):
            v = "'{}'".format(v) if v else ''

        fixed[k] = v or "''"

    try:
        return temp.substitute(**fixed)
    except Exception as e:
        return '{} -- {}'.format(query, params)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__qualname__, (te - ts) * 1000))
        return result
    return timed