#!/bin/bash
set -e
go get -u github.com/jteeuwen/go-bindata/...
pushd api
    echo "Build API"
    go generate
    go build
popd
echo "Generate docs"
pushd raml
    raml2html api.raml > api.html
popd
echo "Install go-raml"
pushd $GOPATH/src/github.com/Jumpscale/go-raml
    bash install.sh
popd
echo "Generate client"
go-raml server -l go --api-file-per-method --dir servertmp --ramlfile raml/api.raml
go-raml client -l python --ramlfile raml/api.raml --dir clienttmp
echo "Validate schemas"
for schema in $(find -name 'schema.capnp'); do
    echo "Validating $schema"
    capnp compile -o c++ $schema
done
echo "Validate python3 syntax"
for pyfile in $(find -name '*.py'); do
    python3 -m py_compile $pyfile
done
