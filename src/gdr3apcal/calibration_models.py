""" Interfaces to various flavors of models """
import numpy
import pandas
from typing import Sequence, Union, Callable
from astropy import units as u
from astropy.coordinates import SkyCoord
from sklearn.base import BaseEstimator


__all__ = ['CalibrationModel', 'SklearnModel', 'CallableModel', 'CalibrationModelGrouped']


class CalibrationModel:
    """ single generic model wrapper """

    def __init__(self, name: str, model: Union[Callable, BaseEstimator], 
                 features: Sequence[str], label:str):
        """ Constructor """
        self.name = name
        self.model = model
        self.features = features
        self.label = label

    @staticmethod
    def compute_cosb_from_dataframe(df: pandas.DataFrame) -> numpy.array:
        """ Infers from the data how to compute cos(b) 

        Checks if b is provided (test degrees or radians). 
        If not attempts from ra, dec with conversion to Galactic coordinates
        """
        # If b is available, compute it automatically but inform the user that units are assumed.
        if ('b' in df.columns):
            # If 'b' is in degrees, it could be larger than pi/2
            if (numpy.nanmax(numpy.abs(df['b'])) > numpy.pi / 2):
                # 'b' definitely comes in degrees.
                print('Automatically adding "cos(b)" from "b" [assuming degrees].')
                cosb = numpy.cos(df['b'] * numpy.pi / 180)
            else:
                # 'b' probably comes in radians.
                print('Automatically adding "cos(b)" from "b" [assuming radians].')
                cosb = numpy.cos(df['b'])   
        elif (('ra' in df.columns) and ('dec' in df.columns)):
            # Convert to Galactic coordinates
            print('Automatically adding cos(b) from given ra and dec assuming degrees.')
            ra = numpy.array(df['ra']) * u.degree
            dec = numpy.array(df['dec']) * u.degree
            c = SkyCoord(ra=ra, dec=dec, frame='icrs')
            cosb = numpy.cos(c.galactic.b.radian)
        else:
            # No positional information available. Throw an error.
            raise KeyError("Your data does not contain positions. Please provide either Galactic latitude b, cosb, or ra+dec.")
        return cosb

    @classmethod
    def _get_features(cls, df: pandas.DataFrame, names: Sequence[str]) -> numpy.array:
        """ Extract features from pandas array and return what we need """
        # if cosb is required but missing, add it.
        # store cosb in the data for further use.
        if (('cosb' in names) and ('cosb' not in df.columns)):
            # this insert operation is not relying on pandas
            df['cosb'] = cls.compute_cosb_from_dataframe(df)

        # Loop over required feature names and check if they are available in pandas data frame.
        # If not, add them to the list of missing names.
        missing = [name for name in names if name not in df.columns]
        
        if missing:
            # If any feature names are missing from pandas data frame, raise an error with a list of all missing names.
            raise KeyError("Missing features from input data: {0:s}".format(','.join(missing)))
        
        return numpy.array([df[k] for k in names]).T 
    
    def __call__(self, df: pandas.DataFrame) -> numpy.array:
        """ call the model like a function """
        # Build the feature vector as input for calibration model.
        # X = self._get_features(df, self.features)

        # Check for NaN features.
        #row_without_nan = numpy.isfinite(X).all(axis=1)

        # array with calibrated values. rows with nan values get nan calibration.
        #calibrated_values = numpy.zeros(len(X)) + numpy.nan
        
        # The calibration is trained on the differences value_gspphot - value_literature
        # Applying the calibration to GSPPhot values therefore works as:
        # value_calibrated = value_gspphot - calibration
        #calibrated_values[row_without_nan] = df[self.label].values[row_without_nan] - self.model.predict(X[row_without_nan])

        #return calibrated_values
        raise NotImplementedError("Use a derived class")
        
    def __repr__(self) -> str:
        """ How it shows on the command line """
        return "Calibration Model '{s.name}':\n    ({s.features}) -> {s.label}".format(s=self)


class SklearnModel(CalibrationModel):
    """ Using a BaseEstimator API (.predict) """
    
    def __init__(self, name: str, model: BaseEstimator, 
                 features: Sequence[str], label:str):
        """ Constructor """
        self.name = name
        self.model = model
        self.features = features
        self.label = label

    def __call__(self, df: pandas.DataFrame) -> numpy.array:
        """ call the model like a function """
        # Build the feature vector as input for calibration model.
        X = self._get_features(df, self.features)

        # Check for NaN features.
        row_without_nan = numpy.isfinite(X).all(axis=1)

        # array with calibrated values. rows with nan values get nan calibration.
        calibrated_values = numpy.zeros(len(X)) + numpy.nan
        
        # The calibration is trained on the differences value_gspphot - value_literature
        # Applying the calibration to GSPPhot values therefore works as:
        # value_calibrated = value_gspphot - calibration
        calibrated_values[row_without_nan] = df[self.label].values[row_without_nan] - self.model.predict(X[row_without_nan])

        return calibrated_values


class CallableModel(CalibrationModel):
    """ Use a single function/callable object as calibration model """

    def __init__(self, name: str, model: Callable, 
                 features: Sequence[str], label:str):
        """ Constructor """
        self.name = name
        self.model = model
        self.features = features
        self.label = label
    
    def __call__(self, df:pandas.DataFrame):
        # Build the feature vector as input for calibration model.
        X = self._get_features(df, self.features)

        # Check for NaN features.
        row_without_nan = numpy.isfinite(X).all(axis=1)

        # array with calibrated values. rows with nan values get nan calibration.
        calibrated_values = numpy.zeros(len(X)) + numpy.nan
        
        # The calibration is trained on the differences value_gspphot - value_literature
        # Applying the calibration to GSPPhot values therefore works as:
        # value_calibrated = value_gspphot - calibration
        pred = numpy.array(list(self.model(X[row_without_nan])))
        calibrated_values[row_without_nan] = df[self.label].values[row_without_nan] - pred

        return calibrated_values


class CalibrationModelGrouped(CalibrationModel):
    """ A convenient collection of models that apply on grouped data 
    This is used to handle the individual calibrations of the spectral libraries of GSP-Phot.
    """
    def __init__(self, name:str, 
                 models: dict, 
                 features: Sequence[str], 
                 label:str, groupby: str):
        """ Constructor """
        self.name = name
        self.features = [k for k in features if k != groupby]
        self.label = label
        self.groupby = groupby
        self.model = models
        for model in models.values():
            model.features = [k for k in model.features if k != groupby]
    
    def __call__(self, df: pandas.DataFrame) -> numpy.array:
        predictions = numpy.empty(len(df))
        predictions.fill(float('nan'))

        for name, data in df.groupby(self.groupby):
            r = self.model[self.name + '_' + name.lower()](data)
            predictions[data.index.values] = r
        return predictions