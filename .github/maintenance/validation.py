"""Read-only file, environment, and workflow validation helpers."""

import copy
import hashlib
import os
from pathlib import Path
import re
import subprocess

import yaml

class WorkflowLoader(yaml.SafeLoader):
    # YAML 1.2 core schema, not PyYAML's YAML 1.1 bool/octal/time rules.
    # https://yaml.org/spec/1.2.2/#103-core-schema
    yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)


CORE_INT = re.compile(r'^(?:[-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+)$')
CORE_FLOAT = re.compile(
    r'^(?:[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?|'
    r'[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$'
)
for first, resolvers in WorkflowLoader.yaml_implicit_resolvers.items():
    WorkflowLoader.yaml_implicit_resolvers[first] = [
        entry for entry in resolvers
        if entry[0] not in {
            'tag:yaml.org,2002:bool', 'tag:yaml.org,2002:int',
            'tag:yaml.org,2002:float', 'tag:yaml.org,2002:timestamp',
        }
    ]
WorkflowLoader.add_implicit_resolver(
    'tag:yaml.org,2002:bool', re.compile(r'^(?:true|false|True|False|TRUE|FALSE)$'), list('tTfF')
)
WorkflowLoader.add_implicit_resolver('tag:yaml.org,2002:int', CORE_INT, list('-+0123456789'))
WorkflowLoader.add_implicit_resolver('tag:yaml.org,2002:float', CORE_FLOAT, list('-+0123456789.'))


def core_integer(loader, node):
    value = loader.construct_scalar(node)
    if not CORE_INT.fullmatch(value):
        raise RuntimeError(f'Invalid YAML 1.2 integer: {value}')
    return int(value, 0 if value.startswith(('0o', '0x')) else 10)


class CoreFloat(str):
    # Preserve float lexemes conservatively: binary rounding must never make
    # two distinct YAML numeric values look identical to the safety guard.
    pass


def core_float(loader, node):
    value = loader.construct_scalar(node)
    if not CORE_FLOAT.fullmatch(value):
        raise RuntimeError(f'Invalid YAML 1.2 float: {value}')
    return CoreFloat(value)


class WorkflowDumper(yaml.SafeDumper):
    pass


WorkflowLoader.add_constructor('tag:yaml.org,2002:int', core_integer)
WorkflowLoader.add_constructor('tag:yaml.org,2002:float', core_float)
WorkflowDumper.add_representer(
    CoreFloat, lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:float', str(value))
)
# Explicit non-core scalar tags are not part of supported workflow formatting.
for tag in ('timestamp', 'binary', 'omap', 'pairs', 'set'):
    WorkflowLoader.add_constructor(f'tag:yaml.org,2002:{tag}', yaml.SafeLoader.construct_undefined)


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise RuntimeError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


WorkflowLoader.add_constructor('tag:yaml.org,2002:map', unique_mapping)


def workflow_data(text):
    # Serialization retains scalar types (True and 1 must not compare equal).
    return yaml.dump(yaml.load(text, Loader=WorkflowLoader), Dumper=WorkflowDumper, sort_keys=True)


def digest(path):
    p = Path(path)
    if p.is_symlink() or any(parent.is_symlink() for parent in p.parents) or not p.is_file():
        raise RuntimeError(f'Expected regular file: {path}')
    return hashlib.sha256(p.read_bytes()).hexdigest()


def child_environment():
    environment = os.environ.copy()
    for name in ('GH_TOKEN', 'GITHUB_TOKEN', 'OPENAI_API_KEY'):
        environment.pop(name, None)
    return environment


def run(*args, capture=False):
    options = {}
    if Path(args[0]).name in ('npm', 'prettier'):
        options['env'] = child_environment()
    return subprocess.run(args, check=True, text=True, capture_output=capture, **options).stdout


def tracked():
    return run('git', 'ls-files', '-z', capture=True).split('\0')[:-1]



def content(path):
    p = Path(path)
    if p.is_symlink() or any(parent.is_symlink() for parent in p.parents) or not p.is_file():
        raise RuntimeError(f'Expected regular file: {path}')
    return p.read_text()
