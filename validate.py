#!/usr/bin/env python

from pathlib import Path

import jsonschema
import yaml

schemas = {}

for inpath in Path('schemas').glob('*.yaml'):
    with open(inpath, 'r') as fp:
        schema = yaml.load(fp)

    validator = jsonschema.validators.validator_for(schema)
    try:
        validator.check_schema(schema)
    except Exception as e:
        print(f'{inpath} is not valid')
        raise

    if schema.get('$id'):
        schemas[schema['$id']] = schema


class NullResolver(jsonschema.RefResolver):
    def resolve_remote(self, uri):
        if uri in self.store:
            return self.store[uri]
        if uri == '':
            return self.referrer


for inpath in Path('examples').glob('*.yaml'):
    with open(inpath, 'r') as fp:
        instance = yaml.load(fp)

    schema_url = instance.get('$schema')
    if not schema_url:
        raise ValueError(f'No schema specified in {inpath}')

    if schema_url not in schemas:
        raise ValueError(f'Invalid schema {schema_url} specified in {inpath}')

    schema = schemas[schema_url]
    resolver = NullResolver.from_schema(schema)
    try:
        jsonschema.validate(instance, schema, resolver=resolver)
    except Exception as e:
        print(f'{inpath} is invalid')
        raise

print('✓ All schemas and examples are valid')
