from .changes import *


def diff(new, old):
    if isinstance(new, (list, tuple)):
        assert isinstance(old, list, tuple)
        assert len(new) == len(old)
        diffs = []
        for n, o in zip(new, old):
            diffs += diff(n, o)
        return diffs
    old_type = old['type']
    new_type = new['type']
    assert old_type == new_type, 'Can not diff {} against {}.'.format(new_type, old_type)
    typ = old_type
    if typ == 'method':
        return _diff_method(new, old)
    elif typ == 'class':
        return _diff_class(new, old)
    elif typ == 'module':
        return _diff_module(new, old)


def _list_to_dict(lst):
    d = {}
    for x in lst:
        d[x['name']] = x
    return d


def _sign_to_dict(sign):
    d = {}
    vars = sign['variables']
    for k in vars:
        d[k] = 'variable', vars[k]
    for k in sign['methods']:
        d[k['name']] = 'method', k
    for k in sign['classes']:
        d[k['name']] = 'class', k
    '''
    for k in sign.get('classmethods', []):
        d[k['name']] = 'classmethod', k
    for k in sign.get('staticmethods', []):
        d[k['name']] = 'staticmethod', k
    for k in sign.get('properties', []):
        d[k['name']] = 'property', k
    '''
    for k in sign.get('modules', []):
        d[k['name']] = 'module', k
    return d


def _diff_method(new, old):
    diffs = []
    name = new['name']
    assert name == old['name']
    old_args = old['args']
    new_args = new['args']
    old_defs = old['defaults']
    new_defs = new['defaults']
    if old_defs is None:
        old_defs = tuple()
    if new_defs is None:
        new_defs = tuple()
    old_args_set = set(old_args)
    new_args_set = set(new_args)
    if old_args_set < new_args_set:
        for i, arg in enumerate(new_args):
            if arg not in old_args_set:
                has_def = i >= len(new_args) - len(new_defs)
                if has_def:
                    diffs.append((ADDED_ARG_WITH_DEFAULT_IN_METHOD, name, arg))
                else:
                    diffs.append((ADDED_ARG_WTHOUT_DEFAULT_IN_METHOD, name, arg))
    elif new_args_set < old_args_set:
        for i, arg in enumerate(old_args):
            if arg not in new_args_set:
                diffs.append((REMOVED_ARG_IN_METHOD, name, arg))
    elif old_args_set == new_args_set:
        if old_args == new_args:
            common_defs_len = min([len(old_defs), len(new_defs)])
            for i in range(len(old_args) - 1, len(old_args) - common_defs_len, -1):
                j = len(old_args) - i
                try:
                    if old_defs[j] != new_defs[j]:
                        diffs.append((CHANGED_DEFAULT_IN_METHOD, name, old_args[i], old_defs[j], new_defs[j]))
                except:
                    pass
            if len(old_defs) < len(new_defs):
                for i in range(0, len(new_defs) - len(old_defs)):
                    j = len(old_args) - len(new_defs) + i
                    diffs.append((ADDED_DEFAULT_IN_METHOD, name, old_args[j], new_defs[i]))
            elif len(new_defs) < len(old_defs):
                for i in range(0, len(old_defs) - len(new_defs)):
                    j = len(old_args) - len(old_defs) + i
                    diffs.append((REMOVED_DEFAULT_IN_METHOD, name, old_args[j], old_defs[i]))
        else:
            diffs.append((CHANGED_ARG_ORDER_IN_METHOD, name, old_args, new_args))
    else:
        diffs.append((CHANGED_ARGS_IN_METHOD, name, old_args, new_args))
    return diffs


def _diff_class(new, old):
    name = new['name']
    assert name == old['name']
    diffs = []
    old_bases = {}
    for ob in old['bases']:
        old_bases[ob['name']] = ob
    new_bases = {}
    for nb in new['bases']:
        new_bases[nb['name']] = nb
    for k in old_bases:
        if k not in new_bases:
            diffs.append((REMOVED_BASE_CLASS, name, k))
    for k in new_bases:
        if k not in old_bases:
            diffs.append((ADDED_BASE_CLASS, name, k))
    for k in old_bases:
        if k in new_bases:
            old_cls = old_bases[k]
            new_cls = new_bases[k]
            diffs += _diff_class(new_cls, old_cls)
    old_methods = {}
    new_methods = {}
    for method in old['methods']:
        method_name = method['name']
        old_methods[method_name] = ('method', method)
    for method in old['staticmethods']:
        method_name = method['name']
        old_methods[method_name] = ('staticmethod', method)
    for method in old['classmethods']:
        method_name = method['name']
        old_methods[method_name] = ('classmethod', method)
    for method in old['properties']:
        method_name = method
        old_methods[method_name] = ('property', method)
    for method in new['methods']:
        method_name = method['name']
        new_methods[method_name] = ('method', method)
    for method in new['staticmethods']:
        method_name = method['name']
        new_methods[method_name] = ('staticmethod', method)
    for method in new['classmethods']:
        method_name = method['name']
        new_methods[method_name] = ('classmethod', method)
    for method in new['properties']:
        method_name = method
        new_methods[method_name] = ('property', method)
    for k in old_methods:
        old_type = old_methods[k][0]
        if k in new_methods:
            new_type = new_methods[k][0]
            if old_type != new_type:
                diffs.append((CHANGED_TYPE_IN_CLASS, name, old_type, new_type))
            elif old_type != 'property':
                diffs += _diff_method(new_methods[k][1], old_methods[k][1])
        elif k in new['variables']:
            diffs.append((CHANGED_TYPE_IN_CLASS, name, old_type, new['variables'][k]))
        else:
            if old_type == 'staticmethod':
                change = MISSING_STATIC_METHOD_IN_CLASS
            elif old_type == 'classmethod':
                change = MISSING_CLASS_METHOD_IN_CLASS
            elif old_type == 'property':
                change = MISSING_PROPERTY_IN_CLASS
            diffs.append((change, name, k))
    for k in new_methods:
        new_type = new_methods[k][0]
        if k not in old_methods:
            if new_type == 'staticmethod':
                change = MISSING_STATIC_METHOD_IN_CLASS
            elif new_type == 'classmethod':
                change = MISSING_CLASS_METHOD_IN_CLASS
            elif new_type == 'property':
                change = MISSING_PROPERTY_IN_CLASS
            diffs.append((change, name, k))
    return diffs


def _diff_module(new, old):
    diffs = []
    name = new['name']
    assert name == old['name']
    old_vars = old['variables']
    new_vars = new['variables']
    old_methods = _list_to_dict(old['methods'])
    new_methods = _list_to_dict(new['methods'])
    old_cls = _list_to_dict(old['classes'])
    new_cls = _list_to_dict(new['classes'])
    old_d = _sign_to_dict(old)
    new_d = _sign_to_dict(new)
    for k, v in old_d.items():
        old_type = v[0]
        if k in new_d:
            v2 = new_d[k]
            new_type = v2[0]
            if old_type != new_type:
                diffs.append((CHANGED_TYPE_IN_MODULE, name, k, old_type, new_type))
            else:
                if old_type == 'class':
                    old_cls = v[1]
                    new_cls = v2[1]
                    diffs += _diff_class(new_cls, old_cls)
                elif old_type == 'module':
                    old_module = v[1]
                    new_module = v2[1]
                    diffs += _diff_module(new_module, old_module)
                elif old_type == 'method':
                    old_method = v[1]
                    new_method = v2[1]
                    diffs += _diff_method(new_method, old_method)
                elif old_type == 'variable':
                    old_var_type = v[1]
                    new_var_type = v[1]
                    if old_var_type != new_var_type:
                        diffs.append((CHANGED_TYPE_IN_MODULE, name, k, old_var_type, new_var_type))
        else:
            if old_type == 'variable':
                change = MISSING_VARIABLE_IN_MODULE
            elif old_type == 'method':
                change = MISSING_METHOD_IN_MODULE
            elif old_type == 'class':
                change = MISSING_CLASS_IN_MODULE
            elif old_type == 'module':
                change = MISSING_MODULE_IN_MODULE
            diffs.append((change, name, k))
    for k in new_d:
        if k not in old_d:
            new_type = new_d[k][0]
            if new_type == 'variable':
                change = NEW_VARIABLE_IN_MODULE
            elif new_type == 'method':
                change = NEW_METHOD_IN_MODULE
            elif new_type == 'class':
                change = NEW_CLASS_IN_MODULE
            elif new_type == 'module':
                change = NEW_MODULE_IN_MODULE
            diffs.append((change, name, k))      
    return diffs
