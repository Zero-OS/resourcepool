echo "Validate python3 syntax"
for pyfile in $(find -name '*.py'); do
    python3 -m py_compile $pyfile
done

echo "Validate schemas"
for schema in $(find -name 'schema.capnp'); do
    echo "Validating $schema"
    capnp compile -o c++ $schema
done