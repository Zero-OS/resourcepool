"""
Auto-generated class for ImageImport
"""

from . import client_support


class ImageImport(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(diskBlockSize, exportBlockSize, exportName, imageName, size, url, encryptionKey=None, exportSnapshot=None, overwrite=None):
        """
        :type diskBlockSize: int
        :type encryptionKey: str
        :type exportBlockSize: int
        :type exportName: str
        :type exportSnapshot: str
        :type imageName: str
        :type overwrite: bool
        :type size: int
        :type url: str
        :rtype: ImageImport
        """

        return ImageImport(
            diskBlockSize=diskBlockSize,
            encryptionKey=encryptionKey,
            exportBlockSize=exportBlockSize,
            exportName=exportName,
            exportSnapshot=exportSnapshot,
            imageName=imageName,
            overwrite=overwrite,
            size=size,
            url=url,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ImageImport'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'diskBlockSize'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.diskBlockSize = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'encryptionKey'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.encryptionKey = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'exportBlockSize'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.exportBlockSize = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'exportName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.exportName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'exportSnapshot'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.exportSnapshot = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'imageName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.imageName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'overwrite'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.overwrite = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'size'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.size = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

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
