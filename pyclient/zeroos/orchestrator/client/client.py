import requests

from .nodes_service import  NodesService 
from .storageclusters_service import  StorageclustersService 
from .vdisks_service import  VdisksService 


class Client:
    def __init__(self, base_uri = ""):
        self.base_url = base_uri
        self.session = requests.Session()
        
        self.nodes = NodesService(self)
        self.storageclusters = StorageclustersService(self)
        self.vdisks = VdisksService(self)

    def is_goraml_class(self, data):
        # check if a data is go-raml generated class
        # we currently only check the existence
        # of as_json method
        op = getattr(data, "as_json", None)
        if callable(op):
            return True
        return False

    def set_auth_header(self, val):
        ''' set authorization header value'''
        self.session.headers.update({"Authorization":val})

    def get(self, uri, headers, params, content_type):
        self.session.headers.update({"Content-Type": content_type})
        res = self.session.get(uri, headers=headers, params=params)
        res.raise_for_status()
        return res

    def post(self, uri, data, headers, params, content_type):
        self.session.headers.update({"Content-Type": content_type})
        if self.is_goraml_class(data):
            data=data.as_json()

        if content_type == "multipart/form-data":
            res = self.session.post(uri, files=data, headers=headers, params=params)
        elif type(data) is str:
            res = self.session.post(uri, data=data, headers=headers, params=params)
        else:
            res = self.session.post(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res

    def put(self, uri, data, headers, params, content_type):
        self.session.headers.update({"Content-Type": content_type})
        if self.is_goraml_class(data):
            data=data.as_json()

        if content_type == "multipart/form-data":
            res = self.session.put(uri, files=data, headers=headers, params=params)
        elif type(data) is str:
            res = self.session.put(uri, data=data, headers=headers, params=params)
        else:
            res = self.session.put(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res

    def patch(self, uri, data, headers, params, content_type):
        self.session.headers.update({"Content-Type": content_type})
        if self.is_goraml_class(data):
            data=data.as_json()

        if content_type == "multipart/form-data":
            res = self.session.patch(uri, files=data, headers=headers, params=params)
        elif type(data) is str:
            res = self.session.patch(uri, data=data, headers=headers, params=params)
        else:
            res = self.session.patch(uri, json=data, headers=headers, params=params)
        res.raise_for_status()
        return res