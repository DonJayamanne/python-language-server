# Copyright 2017 Palantir Technologies, Inc.
import logging
import os.path
from pyls import hookimpl, uris
from behave import parser
from pyls.extension.step_definitions import get_step_definitions
log = logging.getLogger(__name__)

@hookimpl
def pyls_code_lens(config, workspace, document):
    if document.language_id != 'feature':
        return []
    return get_features_and_scenarios(workspace, document)


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
                'arguments': [item.name]
            }
        }, {
            'range': range,
            'command': {
                'title': 'Debug',
                'command': 'behave.debug' + item.type,
                'arguments': [item.name]
            }
        }]
    except Exception:
        return []
