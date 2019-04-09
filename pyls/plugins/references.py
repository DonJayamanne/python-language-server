# Copyright 2017 Palantir Technologies, Inc.
import logging
import os.path
from pyls import hookimpl, uris
from pyls.extension.step_definitions import get_step_definitions_at_position, get_step_definitions, get_steps
log = logging.getLogger(__name__)


@hookimpl
def pyls_references(workspace, document, position, exclude_declaration=False):
    if document.language_id != 'python':
        return []
    step_definitions = get_step_definitions_at_position(workspace, document, position['line'], position['character'])
    all_steps = get_steps(workspace)

    matched_steps = []
    for step in all_steps:
        step_type = step.step_type
        definitions = step_definitions[step_type]
        for definition in definitions:
            if definition.match(step.name) is not None:
                matched_steps.append(step)

    # Filter out builtin modules
    # usages = [d for d in usages if not d.in_builtin_module()]

    return [{
        'uri': uris.from_fs_path(os.path.join(workspace.root_path, d.filename)),
        'range': {
            'start': {'line': d.line - 1, 'character': 0},
            'end': {'line': d.line - 1, 'character': 0}
            # 'end': {'line': d.line - 1, 'character': len("{0}{1}".format(d.step_type, d.name))}
        }
    } for d in matched_steps]

    return []
    # # Are we in a method.
    # current_line = document.lines[position['line'] - 1]
    # stripped_current_line = current_line.strip()
    # if not stripped_current_line.startswith('def') and not stripped_current_line.startswith('async def'):
    # 	return []

    # # Find a step definition just above us
    # for i in range(position['line'] - 1, 1, -1):
    # 	stripped_line = document.lines[i - 1].strip()
    # 	if stripped_line.length == 0:
    # 		return []
    # 	if stripped_line

    # # Note that usages is not that great in a lot of cases: https://github.com/davidhalter/jedi/issues/744
    # usages = document.jedi_script(position).usages()

    # if exclude_declaration:
    #     # Filter out if the usage is the actual declaration of the thing
    #     usages = [d for d in usages if not d.is_definition()]

    # return [{
    #     'uri': uris.uri_with(document.uri, path=d.module_path) if d.module_path else document.uri,
    #     'range': {
    #         'start': {'line': d.line - 1, 'character': d.column},
    #         'end': {'line': d.line - 1, 'character': d.column + len(d.name)}
    #     }
    # } for d in usages]
