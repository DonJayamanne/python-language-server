import ast
import os
import functools
import collections
import parso
from behave import parser
# from pyls.extension.utils import memoize
from behave import step_registry
from behave import runner_util
from behave.runner import Runner
from behave.configuration import Configuration, ConfigError
from behave.step_registry import registry
from behave.runner_util import collect_feature_locations, parse_features
from behave.runner_util import PathManager

def clear_steps_cache():
    get_step_definitions.cache.clear()

step_definitions = None
# @memoize
def get_step_definitions(workspace_folder):
	curdir = os.getcwd()
	try:
		os.chdir(workspace_folder.root_path)
		def exec_file(filename, globals_=None, locals_=None):
			if globals_ is None:
				globals_ = {}
			if locals_ is None:
				locals_ = globals_
			locals_["__file__"] = filename
			with open(filename, "rb") as f:
				# pylint: disable=exec-used
				filename2 = os.path.relpath(filename, os.getcwd())
				code = compile(f.read(), filename2, "exec", dont_inherit=True)
				exec(code, globals_, locals_)


		def load_step_modules(step_paths):
			"""Load step modules with step definitions from step_paths directories."""
			from behave import matchers
			from behave.step_registry import setup_step_decorators
			step_globals = {
				"use_step_matcher": matchers.use_step_matcher,
				"step_matcher":     matchers.step_matcher, # -- DEPRECATING
			}
			setup_step_decorators(step_globals)

			# -- Allow steps to import other stuff from the steps dir
			# NOTE: Default matcher can be overridden in "environment.py" hook.
			with PathManager(step_paths):
				default_matcher = matchers.current_matcher
				for path in step_paths:
					for name in sorted(os.listdir(path)):
						if name.endswith(".py"):
							# -- LOAD STEP DEFINITION:
							# Reset to default matcher after each step-definition.
							# A step-definition may change the matcher 0..N times.
							# ENSURE: Each step definition has clean globals.
							# try:
							step_module_globals = step_globals.copy()
							exec_file(os.path.join(path, name), step_module_globals)
							matchers.current_matcher = default_matcher

		class MyRunner(Runner):
			def __init__(self, config):
				super(MyRunner, self).__init__(config)

			def setup_paths(self):
				Runner.setup_paths(self)
				if self.path_manager.initial_paths[-1] == os.getcwd():
					self.path_manager.initial_paths.pop()

			def load_step_definitions(self, extra_step_paths=None):
				if extra_step_paths is None:
					extra_step_paths = []
				# -- Allow steps to import other stuff from the steps dir
				# NOTE: Default matcher can be overridden in "environment.py" hook.
				steps_dir = os.path.join(self.base_dir, self.config.steps_dir)
				step_paths = [steps_dir] + list(extra_step_paths)
				load_step_modules(step_paths)

		config = Configuration(None)
		config.paths = [workspace_folder.root_path]
		runner = MyRunner(config)
		runner.setup_paths()
		runner.load_step_definitions()

		feature_locations = [filename for filename in runner.feature_locations()
								if not runner.config.exclude(filename)]
		features = parse_features(feature_locations, language=runner.config.lang)
		runner.features.extend(features)

		step_definitions = step_registry.registry.steps
	except Exception:
		x = ''
		pass
	os.chdir(curdir)
	return step_definitions

def get_features(workspace_folder):
	curdir = os.getcwd()
	try:
		os.chdir(workspace_folder.root_path)
		def exec_file(filename, globals_=None, locals_=None):
			if globals_ is None:
				globals_ = {}
			if locals_ is None:
				locals_ = globals_
			locals_["__file__"] = filename
			with open(filename, "rb") as f:
				# pylint: disable=exec-used
				filename2 = os.path.relpath(filename, os.getcwd())
				code = compile(f.read(), filename2, "exec", dont_inherit=True)
				exec(code, globals_, locals_)


		def load_step_modules(step_paths):
			"""Load step modules with step definitions from step_paths directories."""
			from behave import matchers
			from behave.step_registry import setup_step_decorators
			step_globals = {
				"use_step_matcher": matchers.use_step_matcher,
				"step_matcher":     matchers.step_matcher, # -- DEPRECATING
			}
			setup_step_decorators(step_globals)

			# -- Allow steps to import other stuff from the steps dir
			# NOTE: Default matcher can be overridden in "environment.py" hook.
			with PathManager(step_paths):
				default_matcher = matchers.current_matcher
				for path in step_paths:
					for name in sorted(os.listdir(path)):
						if name.endswith(".py"):
							# -- LOAD STEP DEFINITION:
							# Reset to default matcher after each step-definition.
							# A step-definition may change the matcher 0..N times.
							# ENSURE: Each step definition has clean globals.
							# try:
							step_module_globals = step_globals.copy()
							exec_file(os.path.join(path, name), step_module_globals)
							matchers.current_matcher = default_matcher

		class MyRunner(Runner):
			def __init__(self, config):
				super(MyRunner, self).__init__(config)

			def setup_paths(self):
				Runner.setup_paths(self)
				if self.path_manager.initial_paths[-1] == os.getcwd():
					self.path_manager.initial_paths.pop()

			def load_step_definitions(self, extra_step_paths=None):
				if extra_step_paths is None:
					extra_step_paths = []
				# -- Allow steps to import other stuff from the steps dir
				# NOTE: Default matcher can be overridden in "environment.py" hook.
				steps_dir = os.path.join(self.base_dir, self.config.steps_dir)
				step_paths = [steps_dir] + list(extra_step_paths)
				load_step_modules(step_paths)

		config = Configuration(None)
		config.paths = [workspace_folder.root_path]
		runner = MyRunner(config)
		runner.setup_paths()
		runner.load_step_definitions()

		feature_locations = [filename for filename in runner.feature_locations()
								if not runner.config.exclude(filename)]
		features = parse_features(feature_locations, language=runner.config.lang)
	except Exception:
		x = ''
		pass
	os.chdir(curdir)
	return features

def get_steps(workspace_folder):
    features = get_features(workspace_folder)
    steps = []
    for feature in features:
        steps.extend(getattr(getattr(feature, 'background', None), 'steps', []))
        for scenario in feature.scenarios:
            steps.extend(getattr(scenario, 'steps', []))
    return steps

def _get_decorators_at_position(document, line, column):
    parser = parso.parse(document.source)
    leaf = parser.get_leaf_for_position((line + 1, column))
    if leaf.type != 'name':
        return None

    if leaf.parent.type == 'funcdef':
        leaf = leaf.parent
    if leaf.parent.type == 'async_funcdef':
        leaf = leaf.parent
    if leaf.parent.type == 'decorated':
        leaf = leaf.parent
    if leaf.type != 'decorated':
        return None

    first_child = leaf.children[0]
    if first_child.type != 'decorators' and  first_child.type != 'decorator':
        return None

    return [first_child] if first_child.type == 'decorator' else first_child.children


def _get_step_definitions_at_position(document, line, column):
    decorators = _get_decorators_at_position(document, line, column)
    steps = []

    for decorator in decorators:
        if len(decorator.children) < 5:
            continue
        if decorator.children[0].value != '@':
            continue
        if decorator.children[2].value != '(':
            continue
        step_type = decorator.children[1].value
        if step_type not in ['given', 'when', 'then']:
            continue
        name = ast.literal_eval(decorator.children[3].value)
        print(name)
        steps.append({
            'step_type': step_type,
            'name': name,
            'position': decorator.start_pos
        })

    return steps

def get_step_definitions_at_position(workspace_folder, document, line, column):
    try:
        steps = _get_step_definitions_at_position(document, line, column)
        step_definitions = get_step_definitions(workspace_folder)

        items = {'given':[], 'when': [], 'then':[]}
        for item in steps:
            step_type = item['step_type']
            definitions = [step for step in step_definitions[step_type] if step.string == item['name']]
            items[step_type].extend(definitions)

        return items
    except Exception:
        return None

def find_item_at_line(workspace, document, line):
    feature = parser.parse_feature(document.source, 'en', document.path)
    if feature.line - 1 == line:
        return feature
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
