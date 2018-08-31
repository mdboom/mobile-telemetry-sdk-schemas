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

for inpath in Path('examples').glob('*.yaml'):
    with open(inpath, 'r') as fp:
        instance = yaml.load(fp)

    schema_url = instance.get('$schema')
    if not schema_url:
        raise ValueError(f'No schema specified in {inpath}')

    if schema_url not in schemas:
        raise ValueError(f'Invalid schema {schema_url} specified in {inpath}')

    schema = schemas[schema_url]
    try:
        jsonschema.validate(instance, schema)
    except Exception as e:
        print(f'{inpath} is invalid')
        raise

print('✓ All schemas and examples are valid')
