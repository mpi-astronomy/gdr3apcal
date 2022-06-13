.. gdr3apcal documentation master file, created by
   sphinx-quickstart on Wed Oct  5 11:25:47 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gdr3apcal -  Tool for Gaia DR3 AP re-calibration
======================================================

This is a Python package providing the user with empirical calibrations models
of the stellar parameters from GSP-Phot (Andrae et al. 2022).

Currently, we only provide a calibration for the metallicity [M/H] from GSP-Phot.

The empirical [M/H] calibration is trained on LAMOST DR6 data. We considered various literature catalogues as possible training samples and eventually opted for LAMOST DR6 because it provides a broad range of metallicity values but does not probe too deeply into high-extinction regions in the Galactic disk.

Given the LAMOST DR6 training sample, we use a multivariate adtaptive regression spline (MARS) in order to learn a mapping from GSP-Phot's biased [M/H] to LAMOST's metallicity estimates. Since LAMOST provides [Fe/H] estimates, the MARS model not only needs to remove the systematics from GSP-Phot's [M/H] but also translate from [M/H] to [Fe/H]. Furthermore, because the metallicity bias in GSP-Phot also depends on stellar parameters, the input features of the MARS model include the effective temperature, surface gravity, the biased [M/H] value itself and the extinction and reddening (see below). It also includes Galactic latitude, which helps with the translation from [M/H] to [Fe/H].

Two separate MARS calibration models for [M/H] are trained, one for GSP-Phot results from MARCS and one for PHOENIX. The main reason for this distinction is that different libraries can produce very different model spectra (see Fig 1 in Andrae et al 2022) and thus different results. In principle, there could also be calibrations for GSP-Phot results from the A-star and OB libraries, but unfortunately we did not find a sufficient number of stars with literature values to train on. The tool requires the library name to automatically identify which MARS model to apply to each source. Results from A and OB libraries remain uncalibrated.

The tool uses `pandas.DataFrame` functionalities, and requires column names in accordance to the column names in GACS. Specifically, columns required for the calibration are:

* `teff_gspphot`
* `logg_gspphot`
* `mh_gspphot`
* `azero_gspphot`
* `ebpminrp_gspphot`
* `ag_gspphot`
* `mg_gspphot`
* source sky positions; either as (`ra`, `dec`) or (`l`, `b`)
* `libname_gspphot`


Quick start
------------

.. code-block:: python

        import gdr3apcal
        import numpy
        import pandas

        # some pandas data frame with your data from GACS using GACS column names
        df = pandas.read_csv("result-1.csv")
        # Instantiate calibration object
        calib = gdr3apcal.GaiaDR3_GSPPhot_cal()
        # Apply calibrations to [M/H] and/or Teff, returning a numpy array of calibrated values.
        metal_calib = calib.calibrateMetallicity(df)
        teff_calib = calib.calibrateTeff(df)


Note that when you apply a calibration for the first time (or after an update),
the code will first download the corresponding model file.

We do not provide the files directly to avoid large transfers and because not
every user may need all calibration models (e.g. users only interested in
metallicity calibrations). Some of the calibration models can also be very large
(~1GB), so this download can take a few minutes. (We will aim for less
voluminous calibration models in the future.)

Limitations
------------

Obviously, the metallicity calibration tool is not perfect. Its task is to improve the (otherwise hardly usable) [M/H] estimates from GSP-Phot. The community is explicitely invited to develop better calibration tools. Here, we list several limitations:
* Calibrations are only given for the MARCS library (Teff from 2500K to 8000K) and the PHOENIX library (Teff from 3000K to 10000K) but, due to a lack of training data, not for the A and OB libraries.
* The metallicity calibration works very well on low-extinction stars but not so well on high-extinction stars. For example, the metallicity differences to GALAH DR3 values (low-extinction sample) are reduced by ~30% for MARCS and ~50% for PHOENIX. Conversely, for APOGEE DR16 (high-extinction sample), the metallicity differences are reduced by only ~10% for PHOENIX and actually slightly increased for MARCS.
* The calibration should not be used outside the training sample range of LAMOST DR6 (Teff from ~3800K to ~8500K, [Fe/H] from -2.5 to +1).
* Since we train on LAMOST DR6 estimates of [Fe/H], any systematic errors in LAMOST DR6 are inherited.

## How to install

You can install this package directly from git using `pip`

.. code-block::

        pip install git+https://github.com/mpi-astronomy/gdr3apcal


Authors/Contributors
--------------------

* Rene Andrae
* Morgan Fouesneau


Citation guideline
-------------------

This tool is presented in Andrae et al. 2022 (the GSP-Phot paper), one of the CU8 papers accompanying GDR3.
Please cite this paper and the repository.




Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
