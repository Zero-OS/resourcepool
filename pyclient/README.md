# Python Client

0-rest-api is the Python client used to talk to [G8OS 0 Rest API](https://github.com/zero-os/0-rest-api)

## Install

```bash
pip install 0-rest-api
```

## How to use

```python
In [9]: from zeroos.restapi import  client

In [10]: c = client.Client('http://192.168.193.212:8080')

In [11]: c.api.nodes.ListNodes().json()
Out[11]:
[{'hostname': '', 'id': '2c600cbc2545', 'status': 'running'},
 {'hostname': '', 'id': '2c600ccd2ae9', 'status': 'running'},
 {'hostname': '', 'id': '0cc47a3b3d6a', 'status': 'running'},
 {'hostname': '', 'id': '2c600ccd2ad1', 'status': 'running'},
 {'hostname': '', 'id': '2c600cbc23bc', 'status': 'running'}]
```

## To update the client from the RAML file

```shell
go-raml client -l python --ramlfile raml/api.raml --dir pyclient/zeroos/restapi/client
```
