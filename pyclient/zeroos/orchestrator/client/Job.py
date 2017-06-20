"""
Auto-generated class for Job
"""

from . import client_support


class Job(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(id, logLevels, maxRestart, maxTime, queue, recurringPeriod, statsInterval, tags):
        """
        :type id: str
        :type logLevels: list[int]
        :type maxRestart: int
        :type maxTime: int
        :type queue: str
        :type recurringPeriod: int
        :type statsInterval: int
        :type tags: str
        :rtype: Job
        """

        return Job(
            id=id,
            logLevels=logLevels,
            maxRestart=maxRestart,
            maxTime=maxTime,
            queue=queue,
            recurringPeriod=recurringPeriod,
            statsInterval=statsInterval,
            tags=tags,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Job'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'id'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.id = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'logLevels'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.logLevels = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'maxRestart'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.maxRestart = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'maxTime'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.maxTime = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'queue'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.queue = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'recurringPeriod'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.recurringPeriod = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'statsInterval'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.statsInterval = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'tags'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.tags = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
