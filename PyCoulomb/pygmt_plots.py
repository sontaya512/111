# output_manager

import numpy as np
import pygmt
from subprocess import call
from . import conversion_math
from . import io_additionals
from Tectonic_Utils.geodesy import fault_vector_functions


def map_stress_plot(params, inputs, out_object, stress_component):
    """
    Using PyGMT
    Filling in fault patches with colors corresponding to their stress changes
    """
    if stress_component == 'shear':
        plotting_stress = out_object.receiver_shear;
        label = 'Shear';
    elif stress_component == 'normal':
        plotting_stress = out_object.receiver_normal;
        label = 'Normal';
    else:
        plotting_stress = out_object.receiver_coulomb;  # The default option
        label = 'Coulomb';

    # Make stress bounds for map.
    stress_bounds = [abs(np.min(plotting_stress)), abs(np.max(plotting_stress))];
    stress_bound = np.max(stress_bounds);  # setting the scale to symmetric about zero
    # smallest_stress = -stress_bound;  # units: KPa
    # largest_stress = stress_bound;  # units: KPa
    smallest_stress = -1;  # units: KPa
    largest_stress = 1;  # units: KPa

    # Make cpt
    pygmt.makecpt(C="jet", T=str(smallest_stress - 0.1) + "/" + str(largest_stress + 0.1) + "/0.05", H="mycpt.cpt",
                  D=True);

    # Make Map
    region = [inputs.minlon, inputs.maxlon, inputs.minlat, inputs.maxlat];
    proj = "M7i"
    fig = pygmt.Figure()
    title = "+t\"" + stress_component + " stress\"";  # must put escaped quotations around the title.
    fig.basemap(region=region, projection=proj, B=title);
    fig.coast(shorelines="1.0p,black", region=region, N="1", projection=proj, B="1.0");  # the boundary.
    fig.coast(region=region, projection=proj, N='2', W='0.5p,black', S='white', L="g-125.5/39.6+c1.5+w50");

    # Draw each source
    eq_lon, eq_lat = [], [];
    for source in out_object.source_object:
        source_lon, source_lat = fault_vector_functions.xy2lonlat(source.xstart, source.ystart, inputs.zerolon,
                                                                  inputs.zerolat);
        eq_lon.append(source_lon);
        eq_lat.append(source_lat);
        [x_total, y_total, _, _] = conversion_math.get_fault_four_corners(source);
        lons, lats = fault_vector_functions.xy2lonlat(x_total, y_total, inputs.zerolon, inputs.zerolat);
        if not source.potency:
            fig.plot(x=lons, y=lats, pen="thick,black");  # in case of area sources, outline them.
        else:
            fig.plot(x=lons, y=lats, style='s0.3c', G="purple", pen="thin,black");  # in case of point sources
    # Annotate with earthquake location.
    fig.plot(eq_lon, eq_lat, style='s0.3c', G="purple", pen="thin,black");

    # Draw each receiver, with associated data
    for i in range(len(out_object.receiver_object)):
        rec = out_object.receiver_object[i];
        [x_total, y_total, _, _] = conversion_math.get_fault_four_corners(rec);
        lons, lats = fault_vector_functions.xy2lonlat(x_total, y_total, inputs.zerolon, inputs.zerolat);
        fig.plot(x=lons, y=lats, Z=str(plotting_stress[i]), pen="thick,black", G="+z", C="mycpt.cpt");  # color = stress

    # Colorbar annotation
    fig.coast(shorelines="1.0p,black", region=region, projection=proj);  # the boundary.
    fig.colorbar(D="jBr+w3.5i/0.2i+o2.5c/1.5c+h", C="mycpt.cpt", I="0.8",
                 G=str(smallest_stress) + "/" + str(largest_stress - 0.1), B=["x" + str(0.2), "y+L\"KPa\""]);

    # Annotate with aftershock locations
    if params.aftershocks:
        if 'ncsn' in params.aftershocks:
            [lon, lat, _, _, _] = io_additionals.read_aftershock_table_ncsn(params.aftershocks);
        else:
            [lon, lat, _, _, _] = io_additionals.read_aftershock_table(params.aftershocks);
        fig.plot(lon, lat, style='c0.1c', G='black', pen="thin,black");

    fig.savefig(params.outdir + label + '_map.png');
    return;


def map_vertical_def(params, inputs, filename, outfile):
    """Simple map of grdfile with subsampled vertical deformation.
    Currently mess, but a proof of concept!
    Takes a grd file created by gmt surface from the xyz file written in this software. """
    print("Mapping file %s " % filename);

    proj = 'M4i'
    region = [inputs.minlon, inputs.maxlon, inputs.minlat, inputs.maxlat];

    # First make surfaces of east/north/up deformation for later plotting
    outdir = params.outdir;
    inc = 0.0005;
    call(['gmt', 'surface', outdir + '/xyz_model.txt', '-G' + outdir + '/vert.grd',
          '-R' + str(region[0]) + '/' + str(region[1]) + '/' + str(region[2]) + '/' + str(region[3]), '-I'+str(inc),
          '-r'], shell=False);
    call(['gmt', 'surface', outdir + '/xyu_model.txt', '-G' + outdir + '/east.grd',
          '-R' + str(region[0]) + '/' + str(region[1]) + '/' + str(region[2]) + '/' + str(region[3]), '-I'+str(inc),
          '-r'], shell=False);
    call(['gmt', 'surface', outdir + '/xyv_model.txt', '-G' + outdir + '/north.grd',
          '-R' + str(region[0]) + '/' + str(region[1]) + '/' + str(region[2]) + '/' + str(region[3]), '-I'+str(inc),
         '-r'], shell=False);

    # Build a PyGMT plot
    fig = pygmt.Figure();
    pygmt.makecpt(C="roma", T="-0.045/0.045/0.001", D="o", H="mycpt.cpt");
    fig.basemap(region=region, projection=proj, B="+t\"Vertical Displacement\"");
    fig.grdimage(filename, region=region, C="mycpt.cpt");
    fig.coast(region=region, projection=proj, N='1', W='1.0p,black', S='lightblue',
              L="n0.23/0.06+c" + str(region[2]) + "+w20", B="1.0");
    # Annotate with aftershock locations
    if params.aftershocks:
        if 'ncsn' in params.aftershocks:
            [lon, lat, _, _, _] = io_additionals.read_aftershock_table_ncsn(params.aftershocks);
        else:
            [lon, lat, _, _, _] = io_additionals.read_aftershock_table(params.aftershocks);
        fig.plot(lon, lat, style='c0.1c', G='black', pen="thin,black");

    # Draw each source
    eq_lon, eq_lat = [], [];
    for source in inputs.source_object:
        source_lon, source_lat = fault_vector_functions.xy2lonlat(source.xstart, source.ystart, inputs.zerolon,
                                                                  inputs.zerolat);
        eq_lon.append(source_lon);
        eq_lat.append(source_lat);
        [x_total, y_total, _, _] = conversion_math.get_fault_four_corners(source);
        lons, lats = fault_vector_functions.xy2lonlat(x_total, y_total, inputs.zerolon, inputs.zerolat);
        if not source.potency:
            fig.plot(x=lons, y=lats, pen="thick,black");  # in case of area sources, outline them.
        else:
            fig.plot(x=lons, y=lats, style='s0.3c', G="purple", pen="thin,black");  # in case of point sources
    # Annotate with earthquake location.
    fig.plot(eq_lon, eq_lat, style='s0.3c', G="purple", pen="thin,black");
    fig.colorbar(D="JCR+w4.0i+v+o0.7i/0i", C="mycpt.cpt", G="-0.045/0.045", B=["x0.01", "y+L\"Disp(m)\""]);
    fig.savefig(outfile);
    return;