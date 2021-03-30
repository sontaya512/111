"""
The functions in this package convert between formats of faults/ slip distributions

* Format 1: json format for Slippy
* Format 2: slip distribution format for Slippy
* Format 3: .intxt, Kathryn Materna's format for Elastic_stresses_py.  USE ELASTIC_STRESSES_PY TO READ THAT FORMAT.
* Format 4: static1d, Fred Pollitz's STATIC1D code. USE ELASTIC_STRESSES_PY TO READ THAT FORMAT.
* ANY OTHER FORMATS: make sure you build a conversion function into the internal format.

The internal format here is a dictionary containing:
Utility_Dict:
{
    strike(deg),
    dip(deg),
    length(km),
    width(km),
    lon(back top corner),
    lat(back top corner),
    depth(top, km),
    rake(deg),
    slip(m)
}
If the fault is a receiver fault, we put slip = 0
"""

from .io_pycoulomb import fault_dict_to_coulomb_fault
from Tectonic_Utils.geodesy import fault_vector_functions
from Elastic_stresses_py.PyCoulomb import conversion_math


def get_four_corners_lon_lat(fault_dict_object):
    """Return the lon/lat of all 4 corners of a fault_dict_object"""
    [source] = fault_dict_to_coulomb_fault([fault_dict_object]);
    [x_total, y_total, _, _] = conversion_math.get_fault_four_corners(source);
    lons, lats = fault_vector_functions.xy2lonlat(x_total, y_total, source.zerolon, source.zerolat);
    return lons, lats;