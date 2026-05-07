# 2D Tidal Resonant Channel

A 2D shallow water model for studying tidal resonance in a rectangular channel, built using the [Thetis](https://thetisproject.org/) coastal ocean modelling framework (Firedrake).

Developed by Konstantinos Pappas as part of an MEng thesis at the University of Edinburgh (2020).

---

## Overview

This project simulates tidal wave propagation in a closed-end rectangular channel and investigates resonance amplification. The channel length is set relative to the tidal wavelength, and the model is used to study how parameters such as Manning bed friction coefficient and water depth affect the amplification of tidal elevation.

Resonance occurs when the channel length approaches a quarter of the tidal wavelength:

$L_{\mathrm{res}} = \frac{L}{4}$,  $\qquad L = T \sqrt{gH}$

---

## Physics

- **Governing equations:** 2D Shallow Water Equations (SWE)
- **Timestepper:** Crank-Nicolson
- **Bed friction:** Manning formulation
- **Tidal forcing:** Sinusoidal elevation boundary condition with ramp-up
- **Wetting and drying:** Enabled
- **Viscosity sponge:** Applied near the open boundary to damp reflections

---

## Repository Structure

```
.
├── gmsh_generator.py            # Generates mesh geometry (.geo) and calls Gmsh
├── resonant_channel.py          # Main simulation script (Thetis solver)
├── detector_interpreter_min_max.py  # Post-processing: extracts min/max elevation at detectors
├── amplification_analysis.py    # Plots tidal amplification across depth cases
├── demo_2d_channel_bnd.py       # Minimal demo of 2D channel with boundary conditions
├── mesh/
│   ├── mesh.geo                 # Gmsh geometry file
│   └── mesh.msh                 # Generated mesh
└── modules/
    └── support_functions.py     # Shared utilities (detector setup, tidal elevation, HDF5 output)
```

---

## Workflow

**1. Generate the mesh**
```bash
python gmsh_generator.py
```
Generates `mesh/mesh.geo` and calls Gmsh to produce `mesh/mesh.msh`.

**2. Run the simulation**
```bash
python resonant_channel.py
```
Runs the tidal simulation for a given Manning coefficient and writes outputs to `outputs-n-<n>-H-<H>/`.

Key parameters (edit inside `resonant_channel.py`):

| Parameter    | Default  | Description                          |
|--------------|----------|--------------------------------------|
| `mu_manning` | 0.02     | Manning friction coefficient         |
| `amplitude`  | 2.0 m    | Tidal amplitude at the open boundary |
| `H`          | 50 m     | Water depth (bathymetry)             |
| `T`          | 7200 s   | Tidal period                         |
| `lx`         | 30000 m  | Channel length                       |
| `W`          | 2000 m   | Channel width                        |
| `t_end`      | 10 × T   | Total simulation duration            |

**3. Extract detector data**
```bash
python detector_interpreter_min_max.py
```
Reads the HDF5 detector output and writes min/max elevation at each detector location to `min_max.csv`.

**4. Plot amplification**
```bash
python amplification_analysis.py
```
Plots tidal envelope (max/min elevation) along the channel for multiple depth cases.

---

## Dependencies

- [Thetis](https://thetisproject.org/) (and its dependency [Firedrake](https://www.firedrakeproject.org/))
- [Gmsh](https://gmsh.info/)
- NumPy, SciPy, Matplotlib, pandas, h5py

---

## Output

Simulation results are written to `outputs-n-<n>-H-<H>/`:
- `hdf5/` — HDF5 snapshots of elevation and velocity fields
- `Elevation2d/`, `Velocity2d/` — VTU files for visualisation in ParaView
- `diagnostic_detectors.hdf5` — Time series at detector locations
- `Maximum_Elevation.h5`, `Minimum_Elevation.h5` — Spatial maps of tidal envelope
- `max_min.pvd` — ParaView file for max/min elevation fields
