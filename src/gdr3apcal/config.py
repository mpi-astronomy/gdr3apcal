""" Package important locations """
import os
import inspect


__VERSION__ = "0.4"

#directories
__PACKAGE_DIR__ = '/'.join(os.path.abspath(inspect.getfile(inspect.currentframe())).split('/')[:-1])

try:
  from importlib import resources
  modelsdir = resources.files('gdr3apcal') / 'models'
except (ImportError, AttributeError):  # older importlib version
  from pkg_resources import resource_filename
  modelsdir = resource_filename('gdr3apcal', 'models')
