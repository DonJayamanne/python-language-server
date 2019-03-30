# # Copyright 2017 Palantir Technologies, Inc.
# import logging
# import os.path
# from pyls import hookimpl, uris
# from behave import parser
# from pyls.extension.step_definitions import get_step_definitions
# log = logging.getLogger(__name__)

# # @hookimpl
# # def pyls_code_lens(config, workspace, document):
# #     if document.language_id != 'feature':
# #         return []
# #     return get_features_and_scenarios(workspace, document)

# @hookimpl
# def pyls_definitions(config, workspace, document, position):
#     if document.language_id != 'feature':
#         return []
# 	return []
