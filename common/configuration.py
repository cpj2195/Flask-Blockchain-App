import os, regex, yaml
#{package_root}/common/configuration.py
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(PACKAGE_ROOT)
CONFIG_PATH = os.path.join(PACKAGE_ROOT, "config")
# print(CONFIG_PATH)

__CONFIG_LOADED = False
configuration_globals = ['system', 'passwords', 'state']
EVAL_EXECUTION_LOCALS = {}

def load_configuration(config_name='default_config'):
    for file_nm in os.listdir(CONFIG_PATH):
        if file_nm.endswith('.yaml') and (file_nm[:-5] not in configuration_globals): configuration_globals.append(file_nm[:-5])
    globals()['config_name'] = config_name
    #load configuration
    for config in configuration_globals:
        config_file_path = os.path.join(CONFIG_PATH,config+".yaml")
        # print(config_file_path)
        config_file = open(config_file_path)
        # print(config_file)
        configuration = yaml.load(config_file)
        config_file.close()
        globals()[config] = configuration[config_name]
        # print(globals())
        EVAL_EXECUTION_LOCALS[config] = configuration[config_name]
        # print(EVAL_EXECUTION_LOCALS)
    #remapping twice to work with unordered mapping
    for config in configuration_globals:
        remap_configuration_strings(EVAL_EXECUTION_LOCALS[config])
    for config in configuration_globals:
        remap_configuration_strings(EVAL_EXECUTION_LOCALS[config], escape_characters=True)
    __CONFIG_LOADED = True

def remap(value_string):
    #remap a string and resolve all variables
    #remap any string in the paranthesis like %{str} or %{str}%
    for variable_match in regex.finditer("%{[\w\[\]\(\)\{\}\.\'\"\:\+\\\/\ \,\=@]+}%?", value_string):
        var = variable_match.string[variable_match.start():variable_match.end()]
        replaced_value = eval(var.strip('%{}'), EVAL_EXECUTION_LOCALS)
        if isinstance(replaced_value, dict):
            value_string = replaced_value
        else:
            value_string = value_string.replace(var, str(replaced_value))
    return value_string

def remap_configuration_strings(root, escape_characters=False):
    if isinstance(root, dict):
        enumerator = root.iteritems()
    if isinstance(root, list):
        enumerator = enumerate(root)
    for key, value in enumerator:
        if isinstance(value, dict) or isinstance(value, list):
            remap_configuration_strings(value, escape_characters)
        if isinstance(value, str) and ("%{" in value):
            root[key] = remap(value)
        if isinstance(value, str) and ("%x{" in value) and escape_characters:
            root[key] = value.replace("%x{", "%{")

if not __CONFIG_LOADED:
    load_configuration()