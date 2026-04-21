"""
*Simulation of a resonant channel in Thetis
*This is a script put together by Konstantinos Pappas as part of his Meng thesis at UoE (2020)
*Notes on running a hydrodynamic model and conduct a sensitivity study based on the Manning number used
to represent bed friction

#1) Start by running the gmsh_generator.py to create a mesh of desired resolution and shape
#2) Choose the manning bellow to include manning coefficients for iteration
#3) Insert period T, depth H , channel length lx, amplitude
#4) Choose the total duration t_end
#5) Define bathymetry, same as H   (bathymetry_2d.assign(Constant(50.0))
#6) Define viscosity if the model becomes unstable close to the boundaries,
#7) Define timestep Dt, (options.timestep = 50.0)
#8) Define the side of the domain for inflow , (the side the open boundary is expected) (solver_obj.bnd_functions)
#8) Define the coordinates of detectors (below specified every 10000 m) based on lx
#9)  Run this script
#10) Run the detector_intepreter_minmax_sanz.py to extract the min, max values corresponding to detectors, or run
     detector_interpreter_one_detector to see the graph of relative detector
#11) run plotter to see results (for, length, friction, depth, etc.)

"""
import numpy as np
from thetis import *
from modules import support_functions
import matplotlib.pyplot as plt
import math


def tidal_simulation(mu_manning=0.02, amplitude=2.0):
    """
    Simulation setup for resonant channel
    :param mu_manning: Manning friction
    :return:
    """

    #T = 12.42 * 3600              # M2 tidal period
    T = 2 * 3600                  # hypothetical period — smaller domain, faster model
    H = 50                       # Bathymetry (m)
    L = T * math.sqrt(9.81 * H)  # Wavelength L (m) based on celerity math.sqrt(9.81 * H)
    print("Wavelength L = ", L)
    L_res = L / 4                # Resonant channel length (Merian's formula with 1 node)
    lx = 30000  # L/5.5          # Channel length; take approx lx=L/5.5
    W = 2000                     # Channel width (m)
    w = 2 * math.pi / T          # Angular frequency
    k = 2 * math.pi / L          # Wave number

    # TARGET AMPLITUDE = 4
    # Inlet amplitude will be based on theoretical expression (based on Ippen and Eagleston)
    eta = lambda t: 2 * amplitude * math.sin(w * t) * math.cos(k * (-lx))

    # IMPORTANT THE FORCING AT THE INLET NEEDS TO BE CALCULATED BY THE MAXIMUM OF the eta function
    forcing_amplitude = eta(T/4)  # calculate at pi/4
    print("forcing_amplitude=", forcing_amplitude)

    """
    Simulation parameters
    """
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

    """
    Bathymetry and viscosity fields
    """
    P1_2d = FunctionSpace(mesh2d, 'CG', 1)
    DG_2d = FunctionSpace(mesh2d, 'DG', 1)
    bathymetry_2d = Function(P1_2d, name='Bathymetry')
    viscosity_2d = Function(P1_2d, name='viscosity')

    x, y = SpatialCoordinate(mesh2d)
    #Define constant bathymetry:
    bathymetry_2d.assign(Constant(H))  # here we define a constant bathymetry of 50m

    #Define sloping bathymetry:
    depth_oce = 50.0
    depth_riv = 5.0
    #bathymetry_2d.interpolate(depth_oce + (depth_riv - depth_oce) * x / lx)

    #Viscocity sponge:
    viscosity_2d.interpolate(conditional(le(x, 2e3), 1e3 * (2e3 + 1 - x) / 2e3, 1)) #we define a viscosity sponge for x<=2000m, i.e. viscosity = 1e3 * (2e3+1 - x)/2e3, for x>2000m Viscosity=1

    # Uncomment to produce a plot for the bathymetry
    # plot(bathymetry_2d)
    # plt.show()



    """
    Create Thetis solver object
    """
    solver_obj = solver2d.FlowSolver2d(mesh2d, bathymetry_2d)
    options = solver_obj.options
    options.simulation_export_time = t_export
    options.simulation_end_time = t_end
    options.output_directory = outputdir
    options.check_volume_conservation_2d = True
    options.fields_to_export = ['uv_2d', 'elev_2d']
    options.fields_to_export_hdf5 = ['uv_2d', 'elev_2d']
    options.manning_drag_coefficient = Constant(mu_manning)
    #options.timestepper_type = 'CrankNicolson'
    options.swe_timestepper_type = 'CrankNicolson'
    options.timestep = 50.0
    options.use_wetting_and_drying = True
    options.horizontal_viscosity = viscosity_2d  # include viscosity to options
    # if not hasattr(options.timestepper_options, 'use_automatic_timestep'):
    #     options.timestep = 10.0


    """
    Boundary and initial conditions
    """
    tidal_elev = Constant(0)
    solver_obj.bnd_functions['shallow_water'] = {4: {'elev': tidal_elev}}

    # Initial conditions, piecewise linear function for elevation
    elev_init = Function(P1_2d)
    elev_init.assign(0.0)

    """
    Detectors
    """
    # Get equidistant points to monitor across the centreline
    detectors_coordinates = support_functions.get_equidistant_points((0,W), (lx-1e-3,W),20)

    det_names = []  # give detector names : det_names = ['detector_1','detector_2', etc..]
    for i in range(len(detectors_coordinates)):
        det_names.append('detector_' + str(i))
    print(det_names,detectors_coordinates)


    """
    Create a tidal elevation function to be used for the open boundary during the run
    """
    tidal_elevation = support_functions.sinusoidal_tidal_elevation(amplitude=forcing_amplitude)


    """
    Assign initial conditions
    """
    solver_obj.assign_initial_conditions(elev=elev_init, uv=as_vector((1e-3, 0.0))) # Small velocity value (1e-3) is used to avoid division by 0 if friction term is included


    """
    Adding detectors:  (Detectors are monitor points for elevations and velocities)
    """
    cb = DetectorsCallback(solver_obj, detectors_coordinates, ['elev_2d', 'uv_2d'],
                           name='detectors',
                           detector_names=det_names)
    solver_obj.add_callback(cb, 'timestep')
    uv, elev = solver_obj.timestepper.solution.split()


    """
    Output the maximum values at the end of the run
    """
    maximum_elevation = Function(DG_2d, name='Maximum_elevation_'+str(mu_manning)).assign(0.0)
    minimum_elevation = Function(DG_2d, name='Minimum_elevation_'+str(mu_manning)).assign(0.0)

    """
    Update_forcings: function called between timesteps to update boundary conditions and as route for intermediate
    calculations and operations
    """
    def update_forcings(t_new):
        ramp = tanh(t_new / 10000.)
        tidal_elev.assign(Constant(tidal_elevation(t_new) * ramp))

        """
        Monitor maximum and minimum elevations after a certain time 
        """
        if t_new >= t_end/4.:
            maximum_elevation.interpolate(conditional(ge(elev,maximum_elevation),elev,maximum_elevation))
            minimum_elevation.interpolate(conditional(le(elev,minimum_elevation),elev,minimum_elevation))

        if t_new == int(t_end/options.timestep) * options.timestep:
            support_functions.output_field_h5(outputdir,maximum_elevation,'Maximum_Elevation')
            support_functions.output_field_h5(outputdir,minimum_elevation,'Minimum_Elevation')
            File(outputdir+'/max_min.pvd').write(maximum_elevation,minimum_elevation)

    solver_obj.iterate(update_forcings=update_forcings)


"""
Manning sensitivity script
"""
#run the model for different Manning coefficients:
# man = np.arange(0.02, 0.03, 0.01)
# for mu_manning in man:
#     tidal_simulation(mu_manning=mu_manning)

mu_manning=0.02
tidal_simulation(mu_manning=mu_manning)
