# Tool for Gaia DR3 AP re-calibration

This is a Python package providing the user with empirical
calibrations models of the stellar parameters from GSP-Phot.

We provide currently a metallicity [M/H] and an effective temperature Teff model.

We trained these calibration models on literature catalogs (e.g, LAMOST DR6)
based upon machine-learning algorithms (extremely randomised trees at the moment).
These models are not simple equations and therefore, we provide a wrapper for
the users so any update in the models will be transparently propagated.

*This tool is not public*. 

While you can install it using `pip` (see below), the tool is hosted by the DPAC
SVN, i.e., currently accessible only to DPAC members! However, it will
eventually be hosted on GitHub from GDR3 onwards.

The tool uses `pandas.DataFrame` functionalities, and requires column names in
accordance to the column names in GACS. Typical columns required for the
calibration are:

* `teff_gspphot`
* `logg_gspphot`
* `mh_gspphot`
* `azero_gspphot`
* `ebpminrp_gspphot`
* `ag_gspphot`
* `mg_gspphot`
* source sky positions; either as (`ra`, `dec`) or (`l`, `b`)


## Quick start

```python 
import gdr3calib
import numpy
import pandas

# some pandas data frame with your data from GACS using GACS column names
df = pandas.read_csv("result-1.csv")  
# Instantiate calibration object
calib = gdr3calib.GaiaDR3_GSPPhot_cal()
# Apply calibrations to [M/H] and/or Teff, returning a numpy array of calibrated values.
metal_calib = calib.calibrateMetallicity(df)
teff_calib = calib.calibrateTeff(df)
```

Note that when you apply a calibration for the first time (or after an update),
the code will first download the corresponding model file. 

We do not provide the files directly to avoid large transfers and because not
every user may need all calibration models (e.g. users only interested in
metallicity calibrations). Some of the calibration models can also be very large
(~1GB), so this download can take a few minutes. (We will aim for less
voluminous calibration models in the future.)


## How to install 

You can install this package directly from SVN using `pip`

```
pip install svn+https://gaia.esac.esa.int/dpacsvn/DPAC/CU8/MPIA/software/gdr3calib
```

As it is currently on the DPAC SVN, if you may need to provide a username

```
pip install svn+https://<username>@gaia.esac.esa.int/dpacsvn/DPAC/CU8/MPIA/software/gdr3calib
```
(if needed you will be prompted to enter your password)

## Authors/Contributors
* Rene Andrae
* Morgan Fouesneau

## Citation guideline
 
This tool will probably be presented in one of the CU8 papers or within the GSP-Phot paper accompanying GDR3.
