"""
Detector interpreter for the 2D tidal resonant channel simulations.
Written by Konstantinos Pappas, Edited by Thanasis Angeloudis.

This script reads the HDF5 diagnostic detector output produced by Thetis for
a set of 2D shallow-water channel simulations and extracts, for each detector
location along the channel, the maximum and minimum water surface elevation
over a chosen time window.  The results are appended to a CSV file
(min_max.csv) for post-processing and further plotting.

For the detector at the closed end of the channel the script also generates
a five-panel time-series plot showing: surface elevation (eta), longitudinal
velocity (u), transverse velocity (v), flow speed (|U|), and flow direction
(alpha).

How to run
----------
1. Set N_detectors to match the number of detectors used in the simulation.
2. Set n_cases / H_cases to the Manning coefficient and depth values that
   were simulated.
3. Set q to skip the initial spin-up period (number of timesteps to discard).
4. Run the script; results are written to min_max.csv.
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import csv

rc('text', usetex=True)
plt.rc('font', family='serif')


def process_results(df, names, xcoord, index, color='k', label='$\\nu = 0.02$'):
    """
    Reads dataframe data, extracts maximum and minimum elevations, and plots
    elevations, velocities, flow direction at the closed end (as an example)

    :param df: detector callback dataframe
    :param names: detector names
    :param xcoord: x-coordinate of index
    :param index: detector index
    :param color: plot color
    :param label: plot label
    :return:
    """
    t = np.array(df['time'][:, 0])[q:]
    eta = df[names[index]][:, 0][q:]
    u = df[names[index]][:, 1][q:]
    v = df[names[index]][:, 2][q:]

    print(f'x-coordinate, max, min: {xcoord:.1f}  {eta.max():.3f}  {eta.min():.3f}')

    # Write maxima and minima to CSV for further plotting
    with open("min_max.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([index, xcoord, eta.max(), eta.min()])

    # Plot time series at the closed end
    if j == N_detectors - 1:
        # Plot initialisation
        linewidth = 0.2
        f, axarr = plt.subplots(5, sharex="all", sharey="none", figsize=(8, 6), dpi=200)
        fangle = np.angle(u + v * 1j, deg=True)
        axarr[0].plot(t, eta, lw=linewidth, label=label, c=color)
        axarr[0].set_ylabel('$\eta$ (m)')
        axarr[1].plot(t, u, lw=linewidth, label=label, c=color)
        axarr[1].set_ylabel('$u$ (m/s)')
        axarr[2].plot(t, v, lw=linewidth, label=label, c=color)
        axarr[2].set_ylabel('$v$ (m/s)')
        axarr[3].plot(t, np.sqrt(u ** 2 + v ** 2), lw=linewidth, c=color, label=label)
        axarr[3].set_ylabel('$|U|$ (m/s)')
        axarr[4].plot(t, fangle, lw=linewidth, c=color, label=label)
        axarr[4].set_ylabel('$\\alpha$ $^o$')
        axarr[4].set_ylim([-200, 200])

        plt.xticks(rotation=45)
        plt.xlabel('Time (s)')
        plt.tight_layout()
        f.subplots_adjust(hspace=0)
        plt.show(block=True)


if __name__ == '__main__':
    q = 50      # timesteps to skip (spin-up)
    L = 180000  # channel length [m]

    # Reads the outputs of simulations
    dataframes = []
    H_cases = [45, 47.5, 48.5, 49.5, 50, 52.5, 55]

    n = 0.02
    for H in H_cases:
        dataframes.append(h5py.File(f'outputs-n-{n}-H-{H}/diagnostic_detectors.hdf5', 'r'))

    # Create a list of detector names (follows on the notation used in the simulation)
    names = []
    N_detectors = len(dataframes[0].keys()) - 1
    print("Number of Detectors:", N_detectors)
    for k in range(N_detectors):
        names.append('detector_' + str(k))

    for df in dataframes:
        # change the index of the names to produce the plot that you like:
        for j in range(N_detectors):
            xcoord = float(j / N_detectors) * L
            process_results(df, names, xcoord, j, color='blue')

