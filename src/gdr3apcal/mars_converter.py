""" Tools to convert pyearth.Earth models to python source code 

The method to remove pyearth depencency is a little bit convoluted. 
We basically extract the equations of the models and write them into a 
python script.

One could imagine making a dump of the function call. However, this
does not work in python. Python will look for the original module of 
the function. (regardless of using `joblib`, or `dill`) We did not find
a way to deep dump the functions.
"""
import sys
from typing import Sequence, Tuple, Union
from joblib import load
from pyearth import export, Earth
import hashlib


def dump_pyearth_models(mlist: Sequence[Earth], 
                        model_names: Sequence[str], 
                        output: str) -> Tuple[str]:
    """ extract pyEarth model function into a python source file. 

    Parameters
    ----------
    mlist: Sequence[Earth]
        sequence of Earth model objects
    model_names: Sequence[str]
        names associated with each of the models
    output: str
        name of the file that will contain the resulting source code
    
    returns
    -------
    output: str
        file containing the source code
    md5sum: str
        the checksum of the source code for reference
    """
    if not mlist:
        return 

    if output[-3:] != '.py':
        output = output + '.py'

    with open(output, 'w') as fout:    
        for model_name, model in zip(model_names, mlist):
            txt = export.export_python_string(model)
            fout.write(txt.replace('model', model_name))
            fout.write('\n\n')
        
        fout.write('models = {' + 
                   ', '.join(['"{0:s}": {0:s}'.format(model_name) for model_name in model_names]) +
                   '}\n')

    with open(output, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()    
        # pipe contents of the file through
        md5_returned = hashlib.md5(data).hexdigest()
    
    return output, md5_returned


def convert_pyearth_models_from_dumps(
    flist: Sequence[str], 
    output: str, modelname='mh') -> Tuple[str]:
    """ convert dumped models 

    Parameters
    ----------
    flist: Sequence[str]
        sequence of filenames to load Earth model objects from
        the names of the models are taken from the filenames 
        using the last part after a '-' (removing the extension)
        (`fn_noext.split('-')[-1]`)
    output: str
        name of the file that will contain the resulting source code
    
    returns
    -------
    output: str
        file containing the source code
    md5sum: str
        the checksum of the source code for reference
    """
    model_list = []
    if modelname:
        if modelname[-1] != '_':
            modelname = modelname + '_'

    models = []
    model_names = []
    for fname in flist:
            model_name = '{0:s}{1:s}'.format(modelname, 
                                             fname.split('-')[-1]).replace('.joblib', '')
            model = load(fname)
            models.append(model)
            model_names.append(model_name)
    return dump_pyearth_models(models, model_names, output)