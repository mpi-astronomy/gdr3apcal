""" Unit tests for gdr3apcal """
import numpy
import pandas
from gdr3apcal.calibration import GaiaDR3_GSPPhot_cal

numpy.random.seed(1)

def test_import() -> None:
    """ Simple import check """
    
    calib = GaiaDR3_GSPPhot_cal()
    assert(calib is not None)
    assert(calib.calibrateMetallicity is not None)


def generate_random_data(n_rows: int = 2) -> pandas.DataFrame:
    """ Convenient data generator for tests """
    # Create pandas data frame with random data.
    columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'azero_gspphot', 
               'ebpminrp_gspphot', 'ag_gspphot', 'mg_gspphot', 'cosb']
    table = numpy.random.uniform(0.0, 1.0, [n_rows, len(columns)])
    df = pandas.DataFrame(table, columns=columns)
    # add lib_name
    lib_values = ['phoenix', 'marcs']
    df['libname_gspphot'] = numpy.random.choice(lib_values, n_rows)
    return df


def test_metallicity_with_all_columns_available() -> None:
    """ Test the proper behavior of the code """
    
    # Instantiate calibration object
    df_raw = generate_random_data(2)

    df_cal = GaiaDR3_GSPPhot_cal().calibrateMetallicity(df_raw)
    expected_values = (-1.28753895, -1.4720828)  # set by seed

    assert len(df_cal) == len(df_raw)
    for val, ref in zip(df_cal, expected_values):
        assert numpy.abs(val - ref) < 1.0e-8


def test_metallicity_missing_columns():
    """ Test the behavior when missing feature columns """

    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib is not None

    df_raw = generate_random_data()
    # remove some features
    df_raw.drop(columns=['azero_gspphot', 'ag_gspphot'], inplace=True)
    
    try:
        calib['mh'](df_raw)
        assert False
    except KeyError as key_error:
        missing_columns = str(key_error).split(': ')[1].split('\'')[0].split(',')
        assert len(missing_columns) == 2
        assert missing_columns[0] == 'azero_gspphot'
        assert missing_columns[1] == 'ag_gspphot'

def test_metallicity_nan():
    """ Test the behavior when nan values """

    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib is not None

    df_raw = generate_random_data()
    df_raw.at[0, 'teff_gspphot'] = float('nan')
    df_cal = calib['mh'](df_raw)
    assert(
        numpy.isnan(df_cal[0]) & numpy.isfinite(df_cal[1])
        )
    
def test_automatic_conversion_b_to_cosb():
    """ test the automatic conversion of b to cos(b) field"""
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib is not None

    df_raw = generate_random_data()
    df_raw.drop(columns='cosb')
    df_raw['b'] = numpy.random.uniform(-89.0, 89.0, len(df_raw))

    assert len(df_raw['cosb']) > 0
    df_cal = calib['mh'](df_raw)
    assert(numpy.all(numpy.isfinite(df_cal)))

def test_automatic_conversion_radec_to_cosb():
    """ test the automatic conversion of b to cos(b) field"""
    # Instantiate calibration object
    calib = GaiaDR3_GSPPhot_cal()
    assert calib is not None

    df_raw = generate_random_data()
    df_raw.drop(columns='cosb')
    df_raw['ra'] = numpy.random.uniform(-179., 179.0, len(df_raw))
    df_raw['dec'] = numpy.random.uniform(-89, 80.0, len(df_raw))

    assert len(df_raw['cosb']) > 0

    df_cal = calib['mh'](df_raw)
    assert(numpy.all(numpy.isfinite(df_cal)))

