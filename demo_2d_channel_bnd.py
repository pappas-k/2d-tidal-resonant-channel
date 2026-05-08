# 2D channel with time-dependent boundary conditions
# ===================================================
#
# .. highlight:: python
#
# This demo extends the :doc:`2D channel example <demo_2d_channel.py>` by
# introducing both constant and time-dependent boundary conditions to simulate
# tidal forcing at the channel entrance.
#
# We begin by defining the domain and solver as before::

from thetis import *

# Domain: 40 km x 2 km rectangular channel
lx = 40e3  # length [m]
ly = 2e3   # width [m]
nx = 25    # elements along x
ny = 2     # elements along y
mesh2d = RectangleMesh(nx, ny, lx, ly)

# Constant bathymetry
P1_2d = FunctionSpace(mesh2d, 'CG', 1)
bathymetry_2d = Function(P1_2d, name='Bathymetry')
depth = 20.0  # [m]
bathymetry_2d.assign(depth)

# Simulation time parameters
t_end = 12 * 3600   # total duration [s] — one tidal period
t_export = 300.0    # output interval [s]

solver_obj = solver2d.FlowSolver2d(mesh2d, bathymetry_2d)
options = solver_obj.options
options.simulation_export_time = t_export
options.simulation_end_time = t_end
options.swe_timestepper_type = 'CrankNicolson'
options.timestep = 50.0  # [s]

# The model is forced with a constant volume flux at the right boundary
# (x = 40 km) and a tidal volume flux on the left boundary (x = 0 km).
#
# Boundary conditions are defined for each external boundary using its integer ID.
# :py:func:`~.firedrake.utility_meshes.RectangleMesh` assigns IDs 1–4 to the
# four sides (left, right, bottom, top)::

left_bnd_id = 1   # x = 0 km  (tidal inlet)
right_bnd_id = 2  # x = 40 km (open sea)

# At each boundary, specify the external values of the prognostic variables
# (elevation and/or velocity). Values must be Firedrake
# :py:class:`~.firedrake.constant.Constant` or
# :py:class:`~.firedrake.function.Function` objects.
#
# Boundary conditions are stored in a dictionary keyed by boundary ID::

swe_bnd = {}
in_flux = 1e3  # background volume flux [m³/s]
swe_bnd[right_bnd_id] = {'elev': Constant(0.0),
                         'flux': Constant(-in_flux)}

# The right boundary has zero elevation and a constant inward volume flux.
# Fluxes follow the outward-normal convention: negative means flow into the domain.
# Other supported keys are ``'un'`` (normal velocity) and ``'uv'`` (2D velocity
# vector); see :py:mod:`~.shallowwater_eq` for the full list.
#
# For time-dependent boundary conditions, define a Python function that returns
# the boundary value at any given simulation time::


def timedep_flux(simulation_time):
    """Return the tidal volume flux [m³/s] at the left boundary.

    The flux is a sinusoidal tidal signal superimposed on a background inflow.
    """
    tide_amp = -2e3  # tidal amplitude [m³/s]
    tide_t = 12 * 3600.  # tidal period [s]
    flux = tide_amp * sin(2 * pi * simulation_time / tide_t) + in_flux
    return flux


# Wrap the initial value in a ``Constant`` so it can be updated in place,
# then assign it to the left boundary and register all conditions::

tide_flux_const = Constant(timedep_flux(0))
swe_bnd[left_bnd_id] = {'flux': tide_flux_const}

solver_obj.bnd_functions['shallow_water'] = swe_bnd

# Boundaries without explicit conditions (lateral walls 3 and 4) default to
# impermeable (no-normal-flow) land boundaries in Thetis.
#
# To update the tidal flux each time step, pass an ``update_forcings`` callback
# to :py:meth:`~.FlowSolver2d.iterate`. This callback must reassign every time-
# dependent :py:class:`~.firedrake.constant.Constant` or
# :py:class:`~.firedrake.function.Function` used as forcing::


def update_forcings(t):
    """Reassign time-dependent boundary forcings to their value at time *t*."""
    tide_flux_const.assign(timedep_flux(t))


# Finally, run the simulation with the forcing callback::

solver_obj.iterate(update_forcings=update_forcings)

# This tutorial can be downloaded as a Python script `here <demo_2d_channel_bnd.py>`__.
