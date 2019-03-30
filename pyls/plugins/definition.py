# Copyright 2017 Palantir Technologies, Inc.
import logging
import os.path
from pyls import hookimpl, uris
from behave import parser
from pyls.extension.step_definitions import get_step_definitions
log = logging.getLogger(__name__)
from pyls.plugins.code_lens import pyls_code_lens
from pyls.plugins.completion import pyls_completions
# @hookimpl
# def pyls_code_lens(config, workspace, document):
#     if document.language_id != 'feature':
#         return []
#     return get_features_and_scenarios(workspace, document)

@hookimpl
def pyls_definitions(config, workspace, document, position):
    if document.language_id != 'feature':
        return []
    item = find_item_at_line(workspace, document, position['line'])
    return get_definition(workspace, document, item)
    settings = config.plugin_settings('jedi_definition')
    definitions = document.jedi_script(position).goto_assignments(
        follow_imports=settings.get('follow_imports', True),
        follow_builtin_imports=settings.get('follow_builtin_imports', True))

    definitions = [
        d for d in definitions
        if d.is_definition() and d.line is not None and d.column is not None and d.module_path is not None
    ]

    return [{
        'uri': uris.uri_with(document.uri, path=d.module_path),
        'range': {
            'start': {'line': d.line - 1, 'character': d.column},
            'end': {'line': d.line - 1, 'character': d.column + len(d.name)}
        }
    } for d in definitions]


def get_definition(workspace, document, item):
    try:
        if item.step_type not in ['given', 'when', 'then']:
            return []
        steps = get_step_definitions(workspace)
        for step in steps[item.step_type]:
            match = step.match(item.name)
            if match is None:
                continue
            return [{
                'uri': uris.from_fs_path(os.path.join(workspace.root_path, match.location.filename)),
                'range': {
                    'start': {'line': match.location.line - 1, 'character': 0},
                    'end': {'line': match.location.line - 1, 'character': 0}
                }
            }]
    except Exception:
        return []


def find_item_at_line(workspace, document, line):
    feature = parser.parse_feature(document.source, 'en', document.path)
    if feature.line - 1 == line:
        return None
    background = getattr(feature, 'background', None)
    if background is not None:
        if background.line - 1 == line:
            return background
        for step in getattr(background, 'steps', []):
            if step.line - 1 == line:
                return step
    for scenario in getattr(feature, 'scenarios', []):
        if scenario.line - 1 == line:
            return scenario
        for step in getattr(scenario, 'steps', []):
            if step.line - 1 == line:
                return step
        for example in getattr(scenario, 'examples', []):
            if example.line - 1 == line:
                return example
    return None


def get_features_and_scenarios(workspace, document):
    feature = parser.parse_feature(document.source, 'en', document.path)
    items = get_code_lens(document, feature)
    for code_lens in (get_code_lens(document, scenario) for scenario in getattr(feature, 'scenarios', [])):
        items.extend(code_lens)
    # items.extend(scenarios)
    return items

def get_code_lens(document, item):
    try:
        line = document.lines[item.line - 1]
        start_column = line.index(item.keyword)
        range = {
            'start': {'line': item.line - 1, 'character': 0 if start_column < 0 else start_column},
            'end': {'line': item.line - 1, 'character': len(line)}
        }
        return [{
            'range': range,
            'command': {
                'title': 'Run',
                'command': 'behave.run' + item.type,
                'arguments': item.name
            }
        }, {
            'range': range,
            'command': {
                'title': 'Debug',
                'command': 'behave.debug' + item.type,
                'arguments': item.name
            }
        }]
    except Exception:
        return []
