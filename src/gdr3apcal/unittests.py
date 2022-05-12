import unittest
import numpy
import pytest
import pandas
from .calibration import GaiaDR3_GSPPhot_cal


def generate_random_data(n_rows: int = 2) -> pandas.DataFrame:
    """ Convenient data generator for tests """
    # Create pandas data frame with random data.
    numpy.random.seed(1)
    columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
               'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'cosb']
    table = numpy.random.uniform(0.0, 1.0, [n_rows, len(columns)])
    df = pandas.DataFrame(table, columns=columns)
    return df


def test_result_with_all_columns_available():
    """ Test the proper behavior of the code """
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert(calib is not None)

    N  = 2
    df = generate_random_data(N)

    teff_calib = calib.calibrateTeff(df)

    assert len(teff_calib) == N
    assert numpy.abs(teff_calib[0] - 6.761191404702745)<1.0e-9
    assert numpy.abs(teff_calib[1] + 47.58757127815032)<1.0e-9

def test_result_missing_columns_in_DataFrame():
    """ Test the behavior when missing feature columns """
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib is not None

    df = generate_random_data()
    df.drop(columns=['azero_gspphot', 'ag_gspphot'], inplace=True)
    
    try:
        teff_calib = calib.calibrateTeff(df)
        assert False
    except KeyError as ke:
        missing_columns = str(ke).split(': ')[1].split('\'')[0].split(',')
        assert len(missing_columns)==2
        assert missing_columns[0]=='azero_gspphot'
        assert missing_columns[1]=='ag_gspphot'

def test_with_some_features_NaN():
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib!=None

    # Create pandas data frame with random data.
    numpy.random.seed(1)
    N     = 2
    table = numpy.random.uniform(0.0, 1.0, [N,8])
    # Set some features to NaN.
    table[0,2] = numpy.nan
    columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
               'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'cosb']
    df = pandas.DataFrame(table, columns=columns)
    
    teff_calib = calib.calibrateTeff(df)
    assert calib!=None
    assert len(teff_calib)==N
    assert numpy.isnan(teff_calib[0])
    assert numpy.abs(teff_calib[1] + 47.58757127815032)<1.0e-9

def test_automatic_addtion_of_cosb_from_b():
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib!=None

    # Create pandas data frame with random data.
    numpy.random.seed(1)
    N     = 2
    table = numpy.random.uniform(0.0, 1.0, [N,8])
    # Create the pandas DataFrame
    df = pandas.DataFrame(table, columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
                                            'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'b'])

    teff_calib = calib.calibrateMetallicity(df)

    # Overwrite b by range corresponding to degrees.
    table[:,7] = numpy.random.uniform(-89.0, 89.0, N)
    # Create the pandas DataFrame
    df = pandas.DataFrame(table, columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
                                            'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'b'])

    teff_calib = calib.calibrateMetallicity(df)
    
    assert calib!=None
    assert len(teff_calib)==N
    assert len(df['cosb'])==N
    assert numpy.isnan(teff_calib[0])==False

def test_automatic_addtion_of_cosb_from_ra_dec():
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib!=None

    # Create pandas data frame with random data.
    numpy.random.seed(1)
    N     = 2
    table = numpy.random.uniform(0.0, 1.0, [N,9])
    # Create the pandas DataFrame
    df = pandas.DataFrame(table, columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
                                            'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'ra', 'dec'])

    teff_calib = calib.calibrateMetallicity(df)
    
    assert calib!=None
    assert len(teff_calib)==N
    assert len(df['cosb'])==N
    assert numpy.isnan(teff_calib[0])==False