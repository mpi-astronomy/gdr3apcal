""" Package important locations """
import os
import inspect

#directories (set old-school path)
__PACKAGE_DIR__ = '/'.join(os.path.abspath(inspect.getfile(inspect.currentframe())).split('/')[:-1])

try:
  from importlib import resources
  modelsdir = resources.files('gdr3apcal') / 'models'
  __PACKAGE_DIR__ = resources.files('gdr3apcal')
except (ImportError, AttributeError):  # older importlib version
  from pkg_resources import resource_filename
  modelsdir = resource_filename('gdr3apcal', 'models')
  __PACKAGE_DIR__ = resource_filename('gdr3apcal', '')
