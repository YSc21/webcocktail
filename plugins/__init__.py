from glob import glob
import importlib
import inspect
import os

all_plugins = dict()

# dynamically get all plugins class
for f in glob(os.path.join(os.path.dirname(__file__), '*.py')):
    module_name = os.path.splitext(os.path.basename(f))[0]
    if module_name == '__init__':
        continue
    # get module
    spec = importlib.util.spec_from_file_location(module_name, f)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # get class in the module
    for c in inspect.getmembers(module, inspect.isclass):
        # c = ('className', class), class_name should be __file__
        if c[1].__module__ == module_name:
            all_plugins.update([c])
