import os
import numpy
import pandas
import joblib
import yaml
import hashlib
from typing import Sequence, Callable
# local code
from .config import __PACKAGE_DIR__, modelsdir
from .repositories import registered_repositories
from .calibration_models import CallableModel, CalibrationModel, SklearnModel, CalibrationModelGrouped


def _read_configuration(fname: str = None) -> dict:
    """ read/load the configuration for the collector """
    if fname is None:
        fname = os.path.join(__PACKAGE_DIR__, 'configuration.yaml')
    with open(fname, 'r', encoding='utf8') as conf:
        config = conf.read()
    return yaml.load(config, Loader=yaml.SafeLoader)


def checksum_of_file(file_name: str, original: str = None) -> bool:
    """ Verify the Checksum of a given file against reference
    Running without reference will return False, but print the computed hash sum
    """
    hashinst = hashlib.sha256()
    with open(file_name, 'rb') as file_to_check:
        for chunk in iter(lambda: file_to_check.read(hashinst.block_size * 128), b''):
            hashinst.update(chunk)
    returned = hashinst.hexdigest()

    if original is None:
        print(f"{file_name:s}: {returned:s}")
        return returned
    #compare original MD5 with freshly calculated
    return (original == returned)


def _check_model_files(name:str , modelfile:str , modelmd5sum: str):
    """ TODO: make sure we download the files and check their version number """
    # print(modelfile, modelmd5sum)
    try:
        if not checksum_of_file(modelfile, modelmd5sum):
            md5returned = checksum_of_file(modelfile)
            raise RuntimeError(f"Model {name:s} ({modelfile:s}) input file does not match the configuration."
                               f"Expecting {modelmd5sum:s}, got {md5returned:s}")
    except FileNotFoundError:
        # No file, hence download it
        conf = _read_configuration()
        model_repository = conf['models']['repository']['url']
        type_repository = conf['models']['repository']['type']
        repo = registered_repositories[type_repository](model_repository)
        repo.download_file(modelfile.split('/')[-1], modelsdir)
    except RuntimeError as e:
        # BUG: SKIP On windows the checksum does not work.
        print(e)
    except Exception as e:
        raise e


def _load_model_from_configuration(name:str , config: dict) -> CalibrationModel:
    """ Load a model form the configuration file
    Decides which type of model to use given the model description
    """
    model_config = config[name]

    def model_type(model_config: dict) -> object:
        """ Find the adapted class for the model definition """
        callable_model = model_config.get('callable', False)
        if callable_model:
            return CallableModel
        else:
            return SklearnModel

    # check file integrity against configuration checksum
    if os.path.exists(model_config['filename']):
        modelfile = model_config['filename']
    else:
        modelfile = os.path.join(modelsdir, model_config['filename'])

    try:
        if model_config.get('callable', False):
            import importlib
            modulename = "gdr3apcal.models.{0:s}".format(model_config['filename'].replace('.py', ''))
            model = importlib.import_module(modulename).models
        else:
            model = joblib.load(modelfile)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find the source of model {name:s}\n Expected: {modelfile:s}"
        )

    modelmd5sum = model_config['md5sum']
    _check_model_files(name, modelfile, modelmd5sum)

    features = model_config['features']
    label = model_config['label']
    groupby = model_config.get('groupby', False)
    mclass = model_type(model_config)

    if not groupby:
        model = {name: mclass(name, fn, features, label) for name, fn in model.items()}
        calib = CalibrationModel(name, model, features, label)
    else:   # Multi library
        model = {name: mclass(name, fn, features, label) for name, fn in model.items()}
        calib = CalibrationModelGrouped(name, model, features, label, groupby)
    return calib



class GaiaDR3_GSPPhot_cal:
    """ Collection of calibration models for different GSP-Phot parameters. """
    def __init__(self, configuration_file: str = None):
        """ constructor """
        self._configuration = _read_configuration(configuration_file)

        # Private models are only loaded when first called.
        self._models = {}

    def _load_model(self, name:str):
        """ Load a model from disk """
        self._models[name] = _load_model_from_configuration(name, self._configuration)

    def __getitem__(self, name) -> CalibrationModel:
        """ Get a model or load it from disk if not in RAM yet """
        if name not in self._models:
            self._load_model(name)
        return self._models[name]

    def calibrateMetallicity(self, pandas_data_frame: pandas.DataFrame):
        """ apply model mh to the 'mh_gspphot' field """
        return self['mh'](pandas_data_frame)

    def __repr__(self) -> str:
        """ How it shows on the command line """
        return "Calibration Models\n    {0}".format('\n    '.join([str(m) for m in self._models]))

    def printModelVersions(self):
        """Prints model versions"""
        print('[M/H] calibration model version: ', self._configuration['mh']['version'])
        print('Teff calibration model version: ', self._configuration['teff']['version'])
