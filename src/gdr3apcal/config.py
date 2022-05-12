import os
import inspect

from pkg_resources import resource_filename

__VERSION__ = "0.3"

#directories
__PACKAGE_DIR__ = '/'.join(os.path.abspath(inspect.getfile(inspect.currentframe())).split('/')[:-1])
modelsdir = resource_filename('gdr3apcal', 'models')