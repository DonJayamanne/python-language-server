import parso
import ast

def get_step_definitions_at_position(document, line, column):
    parser = parso.parse(document.source)
    leaf = parser.get_leaf_for_position((line, column))
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

    decorators = [first_child] if first_child.type == 'decorator' else first_child.children
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

def do_something():
    contents = open('/Users/donjayamanne/Desktop/Development/PythonStuff/behaveSample/steps/sample.py', 'r').read()

    parser = parso.parse(contents)
    leaf = parser.get_leaf_for_position((10,14))
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

    decorators = [first_child] if first_child.type == 'decorator' else first_child.children
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

    print(parser)

do_something()
