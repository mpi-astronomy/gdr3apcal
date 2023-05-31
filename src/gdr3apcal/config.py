""" Package important locations """
import os
import inspect

# from pkg_resources import resource_filename
import importlib

__VERSION__ = "0.4"

#directories
__PACKAGE_DIR__ = '/'.join(os.path.abspath(inspect.getfile(inspect.currentframe())).split('/')[:-1])
# modelsdir = resource_filename('gdr3apcal', 'models')
modelsdir = importlib.resources.files('gdr3apcal') / 'models'
