"""
Auto-generated class for ImportVM
"""

from . import client_support


class ImportVM(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(blockStoragecluster, url, backupStoragecluster=None, objectStoragecluster=None):
        """
        :type backupStoragecluster: str
        :type blockStoragecluster: str
        :type objectStoragecluster: str
        :type url: str
        :rtype: ImportVM
        """

        return ImportVM(
            backupStoragecluster=backupStoragecluster,
            blockStoragecluster=blockStoragecluster,
            objectStoragecluster=objectStoragecluster,
            url=url,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ImportVM'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'backupStoragecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.backupStoragecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'blockStoragecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.blockStoragecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'objectStoragecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.objectStoragecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'url'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.url = client_support.val_factory(val, datatypes)
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
