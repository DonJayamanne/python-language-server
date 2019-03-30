# Copyright 2017 Palantir Technologies, Inc.
import logging
from pyls import hookimpl
from pyls import uris
from pyls.lsp import SymbolKind

log = logging.getLogger(__name__)


@hookimpl
def pyls_document_symbols(config, document):
    if document.language_id != 'feature':
        return []
    return getFeatureSymbols(document)
    # symbols = getFeatureSymbols(document)
    all_scopes = config.plugin_settings('jedi_symbols').get('all_scopes', True)
    definitions = document.jedi_names(all_scopes=all_scopes)
    return [{
        'name': d.name,
        'containerName': _container(d),
        'location': {
            'uri': document.uri,
            'range': _range(d),
        },
        'kind': _kind(d),
    } for d in definitions if _include_def(d)]


def _include_def(definition):
    return (
        # Don't tend to include parameters as symbols
        definition.type != 'param' and
        # Unused vars should also be skipped
        definition.name != '_' and
        _kind(definition) is not None
    )


def _container(definition):
    try:
        # Jedi sometimes fails here.
        parent = definition.parent()
        # Here we check that a grand-parent exists to avoid declaring symbols
        # as children of the module.
        if parent.parent():
            return parent.name
    except:  # pylint: disable=bare-except
        return None

    return None


def _range(definition):
    # This gets us more accurate end position
    definition = definition._name.tree_name.get_definition()
    (start_line, start_column) = definition.start_pos
    (end_line, end_column) = definition.end_pos
    return {
        'start': {'line': start_line - 1, 'character': start_column},
        'end': {'line': end_line - 1, 'character': end_column}
    }


_SYMBOL_KIND_MAP = {
    'none': SymbolKind.Variable,
    'type': SymbolKind.Class,
    'tuple': SymbolKind.Class,
    'dict': SymbolKind.Class,
    'dictionary': SymbolKind.Class,
    'function': SymbolKind.Function,
    'lambda': SymbolKind.Function,
    'generator': SymbolKind.Function,
    'class': SymbolKind.Class,
    'instance': SymbolKind.Class,
    'method': SymbolKind.Method,
    'builtin': SymbolKind.Class,
    'builtinfunction': SymbolKind.Function,
    'module': SymbolKind.Module,
    'file': SymbolKind.File,
    'xrange': SymbolKind.Array,
    'slice': SymbolKind.Class,
    'traceback': SymbolKind.Class,
    'frame': SymbolKind.Class,
    'buffer': SymbolKind.Array,
    'dictproxy': SymbolKind.Class,
    'funcdef': SymbolKind.Function,
    'property': SymbolKind.Property,
    'import': SymbolKind.Module,
    'keyword': SymbolKind.Variable,
    'constant': SymbolKind.Constant,
    'variable': SymbolKind.Variable,
    'value': SymbolKind.Variable,
    'param': SymbolKind.Variable,
    'statement': SymbolKind.Variable,
    'boolean': SymbolKind.Boolean,
    'int': SymbolKind.Number,
    'longlean': SymbolKind.Number,
    'float': SymbolKind.Number,
    'complex': SymbolKind.Number,
    'string': SymbolKind.String,
    'unicode': SymbolKind.String,
    'list': SymbolKind.Array,
}


def _kind(d):
    """ Return the VSCode Symbol Type """
    return _SYMBOL_KIND_MAP.get(d.type)


_STEP_KIND = {
    'given': SymbolKind.Method,
    'when': SymbolKind.Method,
    'then': SymbolKind.Method,
    'and': SymbolKind.Field,
    'but': SymbolKind.Field
}

def _step_kind(step_type):
    if step_type in _STEP_KIND:
        return _STEP_KIND[step_type]
    return SymbolKind.Variable

# def parse_file(filename, language=None):
#     with open(filename, "rb") as f:
#         # file encoding is assumed to be utf8. Oh, yes.
#         data = f.read().decode("utf8")
#     return parse_feature(data, language, filename)

def getFeatureSymbols(document):
    try:
        from behave import parser
        feature = parser.parse_feature(document.source, 'en', document.path)
        feature_symbol = get_feature_symnbol(document, feature)
        backgrounds = get_background(document, feature)
        scenarios = get_scenarios(document, feature)
        scenarios.append(feature_symbol)
        scenarios.extend(backgrounds)
        return scenarios
        return [{
            'name': "{0}: {1}".format(feature.keyword, feature.name),
            'containerName': None,
            'location': {
                'uri': document.uri,
                'range': get_range(document, feature),
            },
            'kind': SymbolKind.Namespace
        }]
    except:
        return []

def get_feature_symnbol(document, feature):
    return {
        'name': "{0}: {1}".format(feature.keyword, feature.name),
        'containerName': None,
        'location': {
            'uri': document.uri,
            'range': get_feature_range(document, feature),
        },
        'kind': SymbolKind.Namespace
    }

def get_background(document, feature):
    background = getattr(feature, 'background', None)
    if background is None:
        return []
    items = []
    symbol = {
        'name': "{0}: {1}".format(background.keyword, background.name),
        'containerName': feature.name,
        'location': {
            'uri': document.uri,
            'range': get_scenario_range(document, background),
        },
        'kind': SymbolKind.Class
    }
    steps = get_step_definitions(document, background)
    # examples = get_examples(document, background)
    items.append(symbol)
    items.extend(steps)
    # items.extend(examples)
    return items

def get_scenarios(document, feature):
    scenarios = []
    for scenario in feature.scenarios:
        symbol = {
            'name': "{0}: {1}".format(scenario.keyword, scenario.name),
            'containerName': feature.name,
            'location': {
                'uri': document.uri,
                'range': get_scenario_range(document, scenario),
            },
            'kind': SymbolKind.Class
        }
        steps = get_step_definitions(document, scenario)
        examples = get_examples(document, scenario)
        scenarios.append(symbol)
        scenarios.extend(steps)
        scenarios.extend(examples)
    return scenarios

def get_step_definitions(document, scenario):
    steps = []
    for step in scenario.steps:
        symbol ={
            'name': "{0} {1}".format(step.keyword, step.name),
            'containerName': scenario.name,
            'location': {
                'uri': document.uri,
                'range': get_step_range(document, step),
            },
            'kind': _step_kind(step.step_type)
        }
        steps.append(symbol)
    return steps


def get_examples(document, scenario):
    examples = []
    for example in getattr(scenario, 'examples', []):
        table_rows = get_table_rows(document, example)
        end_line = example.line - 1
        end_character = None
        if len(table_rows) > 0:
            end_line = table_rows[-1]['location']['range']['end']['line']
            end_character = table_rows[-1]['location']['range']['end']['character']
        symbol = {
            'name': "{0}: {1}".format(example.keyword, example.name),
            'containerName': scenario.name,
            'location': {
                'uri': document.uri,
                'range': get_range(document, example.line - 1, end_line, end_column=end_character),
            },
            'kind': SymbolKind.Interface
        }
        examples.append(symbol)
        examples.extend(table_rows)
    return examples

def get_table_rows(document, example):
    items = []
    table = getattr(example, 'table', None)
    if table is None:
        return items
    end_line = table.line - 1
    for row in getattr(table, 'rows', []):
        end_line = row.line - 1
        items.append({
            'name': ' | '.join(row.cells),
            'containerName': example.name,
            'location': {
                'uri': document.uri,
                'range': get_range(document, row.line - 1, row.line - 1),
            },
            'kind': SymbolKind.Array
        })

    items.insert(0, {
            'name': ' | '.join(table.headings),
            'containerName': example.name,
            'location': {
                'uri': document.uri,
                'range': get_range(document, table.line - 1, end_line),
            },
            'kind': SymbolKind.String
        })
    return items

def get_feature_range(document, feature):
    end_line = len(document.lines)
    end_column = 1
    if len(feature.scenarios) > 0:
        end_line = feature.scenarios[-1].line
        end_column = len(document.lines[feature.scenarios[-1].line-1].strip('\r\n'))
        if len(feature.scenarios[-1].steps) > 0:
            end_line = feature.scenarios[-1].steps[-1].line
            end_column = len(document.lines[feature.scenarios[-1].steps[-1].line-1].strip('\r\n'))

    return {
        'start': {'line': feature.line - 1, 'character': 1},
        'end': {'line': end_line - 1, 'character': end_column}
    }

def get_range(document, start_line = None, end_line = None, start_column = 1, end_column = None):
    end_line = end_line if end_line is not None else len(document.lines)
    end_column = end_column if end_column is not None else len(document.lines[end_line-1].strip('\r\n'))

    return {
        'start': {'line': start_line, 'character': start_column},
        'end': {'line': end_line, 'character': end_column}
    }

def get_scenario_range(document, scenario):
    start_column = 1
    end_column = len(document.lines[-1].strip('\r\n'))
    end_line = len(document.lines)
    if len(scenario.steps) > 0:
        end_line = scenario.steps[-1].line
        end_column = len(document.lines[end_line-1].strip('\r\n'))

    return {
        'start': {'line': scenario.line - 1, 'character': 1},
        'end': {'line': end_line - 1, 'character': end_column}
    }

def get_step_range(document, step):
    start_column = 1
    end_column = len(document.lines[step.line -1].strip('\r\n'))
    end_line = step.line
    start_line = step.line - 1
    end_line = start_line
    return {
        'start': {'line': start_line, 'character': 1},
        'end': {'line': end_line, 'character': end_column}
    }
