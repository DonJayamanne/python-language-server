# Copyright 2017 Palantir Technologies, Inc.
import logging
import os
from behave import i18n
from pyls import hookimpl, lsp, _utils
from pyls.extension.step_definitions import get_step_definitions
from pyls.lsp import SymbolKind
log = logging.getLogger(__name__)

@hookimpl
def pyls_completions(config, workspace, document, position):
    line_index = position['line']
    line = document.lines[line_index]
    if line.strip() == 'Th' or line.strip() == 'T':
        x = 1
    keywords = get_completion_keywords(workspace, document, line_index)
    if len(line.strip()) == 0:
        return [{
                'label': keyword,
                'kind': SymbolKind.Field,
                'detail': 'details',
                'documentation': 'documentation',
                'sortText': keyword,
                'insertText': keyword
            } for keyword in keywords]


    language_keywords = i18n.languages['en']
    line_details = get_line_step_type_and_text(document, line_index)
    if line_details is None:
        # Check if we're in the middle of typing a key word
        text = line.strip()
        steps = [keyword for keyword in keywords if keyword.startswith(text)]
        start_character = position['character']
        completions = []
        for step in steps:
            completion = {
                'label': step,
                'kind': SymbolKind.Field,
                'detail': 'details',
                'documentation': 'documentation',
                'sortText': step,
                'insertText': step
                # 'textEdit': {
                #     'newText': step[len(text):],
                #     'range': {
                #         'start': {'line': line_index, 'character': start_character},
                #         'end': {'line': line_index, 'character': position['character']}
                #     }
                # }
            }
            completions.append(completion)
        return completions

    steps = get_step_names(workspace, line_details[1])
    completions = []
    text_is_empty = len(line_details[2].strip()) == 0
    start_character = position['character'] if position['character'] else line.index(line_details[2].strip())
    prefix = ' ' if line.lstrip().strip('\r\n').strip('\n') in keywords else ''
    for step in steps:
        if text_is_empty and not step.strip().startswith(line_details[2].strip()):
            continue
        completion = {
            'label': step,
            'kind': SymbolKind.Field,
            'detail': 'details',
            'documentation': 'documentation',
            'sortText': step,
            'textEdit': {
                'newText': prefix + (step if text_is_empty else step.strip()[len(line_details[2].strip()):]),
                'range': {
                    # 'start': {'line': line_index, 'character': start_character + len(line_details[2])},
                    'start': {'line': line_index, 'character': start_character},
                    'end': {'line': line_index, 'character': position['character']}
                }
            }
        }
        completions.append(completion)
    return completions


def get_keywords_for_completion(workspace, item_type):
    keywords = []
    if item_type in ['when', 'then', 'given']:
        keywords.extend(get_keywords_for_completion(workspace, 'and'))
        keywords.extend(get_keywords_for_completion(workspace, 'but'))

    language_keywords = i18n.languages['en']
    keywords.extend([value for value in language_keywords[item_type] if value != '*'])

    if item_type in ['when', 'then', 'given']:
        keywords = list(set(keywords))
        texts = get_step_names(workspace, item_type)
        keywords = [keyword + ' ' + text for keyword in keywords for text in texts]
    return keywords

def get_completion_keywords(workspace, document, line_index):
    current_context = get_current_context(document, line_index)
    if current_context is None:
        return None

    language_keywords = i18n.languages['en']
    completions = []

    if current_context == 'feature':
        completions.extend(get_keywords_for_completion(workspace, 'background'))
        completions.extend(get_keywords_for_completion(workspace, 'scenario'))
        completions.extend(get_keywords_for_completion(workspace, 'scenario_outline'))
    if current_context in ['background', 'scenario', 'scenario_outline']:
        completions.extend(get_keywords_for_completion(workspace, 'given'))
        completions.extend(get_keywords_for_completion(workspace, 'when'))
        completions.extend(get_keywords_for_completion(workspace, 'then'))
    if current_context in ['given', 'when', 'then']:
        completions.extend(get_keywords_for_completion(workspace, current_context))

    return completions

def get_current_context(document, line_index):
    language_keywords = i18n.languages['en']
    for index in range(line_index, 0, -1):
        line_text = document.lines[index].strip()
        for item in ['background', 'examples', 'feature', 'scenario', 'scenario_outline', 'given', 'when', 'then']:
            for keyword in language_keywords[item]:
                if line_text.startswith(keyword) and keyword != '*':
                    return item
    return None


def get_step_names(workspace, step_type):
    steps = get_step_definitions(workspace)
    return [step.string for step in steps[step_type]]

def get_line_step_type_and_text(document, line_index):
    """
    Gets the step type and the text typed.
        :param document: document
        :param line: line number
        :return: (keyword, step type and the step text)
    """
    line = document.lines[line_index].strip()
    stripped_line = document.lines[line_index].strip()
    language_keywords = i18n.languages['en']
    get_previous_step = False
    text = None
    for step_type in ['given', 'when', 'then', 'and', 'but']:
        for keyword in language_keywords[step_type]:
            if stripped_line.startswith(keyword):
                text = line[line.index(keyword) + len(keyword):].lstrip()
                if keyword == '*' or step_type == 'and' or step_type == 'but':
                    get_previous_step = True
                    break

                return (keyword, step_type, text)

    if not get_previous_step:
        return None

    for index in range(line_index, 0, -1):
        line_text = document.lines[index].strip()
        for step_type in ['given', 'when', 'then']:
            for keyword in language_keywords[step_type]:
                if line_text.startswith(keyword) and keyword != '*':
                    return (keyword, step_type, text)

    return None
