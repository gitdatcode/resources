from moesha.entity import Collection
from moesha.property import TimeStamp

from .partials import GetRelationshipBetween
from datcode.config import options
from datcode import LOG


class BaseMapper(object):
    PROPERTIES = {
        'date_created': TimeStamp(),
    }

    def data(self, entity):
        if isinstance(entity, Collection):
            return [self.data(e) for e in entity]

        data = entity.data
        data['id'] = entity.id
        data['labels'] = entity.labels

        return data

    def has_connection(self, owner, entity, relationship):
        between = GetRelationshipBetween(start=owner, end=entity,
            relationships=relationship)

        return self.mapper.query(pypher=between)

    def email_html(self, to, key, **kwargs):
        """
        Method used to send an email based on a key defined in the
        api.model.email.mapping.MAPPINGS dict. The subject will be
        automatically set and the content rendered with the **kwargs passed in
        This will also add an EmailLog entry to the datbase
        """
        from datcode.common.model.graph.node.email_log import EmailLog
        from datcode.common.model.email.mapping import MAPPINGS


        if not isinstance(to, (list, set, tuple)):
            to = [to,]

        source = options.from_email

        try:
            success = True
            resp = self.mapper.email.email_mapping(to=to, key=key,
                source=source, **kwargs)
            subject = MAPPINGS[key]['subject']
        except Exception as e:
            LOG.error(e)
            subject = ''
            success = False
            resp = ''

        for t in to:
            data = {
                'content': resp,
                'email': t,
                'success': success,
                'subject': subject,
                'to': to,
            }
            email_log = self.mapper.create(entity=EmailLog, properties=data)
            self.mapper.save(email_log).send()
