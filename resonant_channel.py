"""
Simulation of a resonant channel in Thetis.

Script by Konstantinos Pappas (MEng thesis, UoE 2020). Runs a 2D shallow-water
model and conducts a sensitivity study based on the Manning bed-friction
coefficient.

How to run
----------
1. Run gmsh_generator.py to create a mesh of the desired resolution and shape.
2. Choose the Manning coefficients for iteration.
3. Set period T, depth H, channel length lx, and forcing amplitude.
4. Choose the total duration t_end.
5. Define bathymetry (bathymetry_2d.assign(Constant(H))).
6. Define viscosity if the model becomes unstable near the boundaries.
7. Define timestep Dt (options.timestep = 50.0).
8. Define the open-boundary side of the domain (solver_obj.bnd_functions).
9. Define detector coordinates (below: equidistant points along lx).
10. Run this script.
11. Run detector_interpreter_min_max.py to extract min/max detector values.
12. Run the plotter to view results (length, friction, depth, etc.).
"""
import math

import numpy as np
from thetis import *

from modules import support_functions


def tidal_simulation(mu_manning=0.02, amplitude=2.0):
    """
    Simulation setup for resonant channel
    :param mu_manning: Manning friction
    :return:
    """

    T = 2 * 3600  # hypothetical period — smaller domain, faster model
    H = 50  # bathymetry [m]
    L = T * math.sqrt(9.81 * H)  # wavelength [m]
    print("Wavelength L = ", L)
    lx = 30000  # channel length [m]; approx L/5.5
    W = 2000  # channel width [m]
    w = 2 * math.pi / T  # angular frequency [rad/s]
    k = 2 * math.pi / L  # wave number [rad/m]

    # Inlet amplitude from Ippen & Eagleston theoretical expression, evaluated at t = T/4
    forcing_amplitude = 2 * amplitude * math.sin(w * T / 4) * math.cos(k * (-lx))
    print("forcing_amplitude=", forcing_amplitude)

    # Simulation parameters
    # Output folder
    outputdir = 'outputs' + "-" + "n-" + str(mu_manning) + "-" + "H-" + str(H)
    # Mesh for simulation
    mesh2d = Mesh('mesh/mesh.msh')

    print_output('Loaded mesh ' + mesh2d.name)
    print_output('Exporting to ' + outputdir)

    # total duration in seconds
    t_end = T * 10 # initially was *20
    # export interval in seconds
    t_export = 1000.0

    # Bathymetry and viscosity fields
    P1_2d = FunctionSpace(mesh2d, 'CG', 1)
    DG_2d = FunctionSpace(mesh2d, 'DG', 1)
    bathymetry_2d = Function(P1_2d, name='Bathymetry')
    viscosity_2d = Function(P1_2d, name='viscosity')

    x, y = SpatialCoordinate(mesh2d)
    # Define constant bathymetry:
    bathymetry_2d.assign(Constant(H))

    # Viscosity sponge:
    viscosity_2d.interpolate(conditional(le(x, 2e3), 1e3 * (2e3 + 1 - x) / 2e3, 1)) #we define a viscosity sponge for x<=2000m, i.e. viscosity = 1e3 * (2e3+1 - x)/2e3, for x>2000m Viscosity=1

    # Create Thetis solver object
    solver_obj = solver2d.FlowSolver2d(mesh2d, bathymetry_2d)
    options = solver_obj.options
    options.simulation_export_time = t_export
    options.simulation_end_time = t_end
    options.output_directory = outputdir
    options.check_volume_conservation_2d = True
    options.fields_to_export = ['uv_2d', 'elev_2d']
    options.fields_to_export_hdf5 = ['uv_2d', 'elev_2d']
    options.manning_drag_coefficient = Constant(mu_manning)
    options.swe_timestepper_type = 'CrankNicolson'
    options.timestep = 50.0
    options.use_wetting_and_drying = True
    options.horizontal_viscosity = viscosity_2d

    # Boundary and initial conditions
    tidal_elev = Constant(0)
    solver_obj.bnd_functions['shallow_water'] = {4: {'elev': tidal_elev}}

    # Initial conditions, piecewise linear function for elevation
    elev_init = Function(P1_2d)
    elev_init.assign(0.0)

    # Detectors
    # Get equidistant points to monitor across the centreline
    detectors_coordinates = support_functions.get_equidistant_points((0,W), (lx-1e-3,W),20)

    det_names = []  # give detector names : det_names = ['detector_1','detector_2', etc..]
    for i in range(len(detectors_coordinates)):
        det_names.append('detector_' + str(i))
    print(det_names,detectors_coordinates)

    # Create a tidal elevation function for the open boundary
    tidal_elevation = support_functions.sinusoidal_tidal_elevation(amplitude=forcing_amplitude)

    # Assign initial conditions
    solver_obj.assign_initial_conditions(elev=elev_init, uv=as_vector((1e-3, 0.0))) # Small velocity value (1e-3) is used to avoid division by 0 if friction term is included

    # Add detector callbacks (monitor points for elevations and velocities)
    cb = DetectorsCallback(solver_obj, detectors_coordinates, ['elev_2d', 'uv_2d'],
                           name='detectors',
                           detector_names=det_names)
    solver_obj.add_callback(cb, 'timestep')
    uv, elev = solver_obj.timestepper.solution.split()

    # Track maximum and minimum field elevations
    maximum_elevation = Function(DG_2d, name='Maximum_elevation_'+str(mu_manning)).assign(0.0)
    minimum_elevation = Function(DG_2d, name='Minimum_elevation_'+str(mu_manning)).assign(0.0)

    def update_forcings(t_new):
        ramp = tanh(t_new / 10000.)
        tidal_elev.assign(Constant(tidal_elevation(t_new) * ramp))

        # Monitor maximum and minimum elevations after spin-up
        if t_new >= t_end/4.:
            maximum_elevation.interpolate(conditional(ge(elev,maximum_elevation),elev,maximum_elevation))
            minimum_elevation.interpolate(conditional(le(elev,minimum_elevation),elev,minimum_elevation))

        if t_new == int(t_end/options.timestep) * options.timestep:
            support_functions.output_field_h5(outputdir,maximum_elevation,'Maximum_Elevation')
            support_functions.output_field_h5(outputdir,minimum_elevation,'Minimum_Elevation')
            File(outputdir+'/max_min.pvd').write(maximum_elevation,minimum_elevation)

    solver_obj.iterate(update_forcings=update_forcings)


mu_manning = 0.02
tidal_simulation(mu_manning=mu_manning)
