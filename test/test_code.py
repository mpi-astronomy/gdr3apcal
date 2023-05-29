""" Unit tests for gdr3apcal """

def test_import() -> None:
    """ Simple import check """
    from gdr3apcal.calibration import GaiaDR3_GSPPhot_cal
    assert (GaiaDR3_GSPPhot_cal() is not None)