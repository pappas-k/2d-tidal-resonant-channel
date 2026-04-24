"""
Plotting script for resonant channel
Written by Konstantinos Pappas, Edited by Thanasis Angeloudis.
#------------------How to run the script-------------
#1) change the number of detectors depending on the length of channel
#2) choose the range number bellow dir, depending on how many iterations based on manning coefficients conducted
#3) change q to get results after a certain period
#4) run the script, the results are extracted in minMax.csv file
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import csv

rc('text', usetex=True)
plt.rc('text', usetex=True)
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
    t = np.array(df['time'][:, 0])[q:]    # t is the time
    eta = df[names[index]][:, 0][q:]      # eta is the elevation here
    u = df[names[index]][:, 1][q:]        # u  is the horizontal velocity component here
    v = df[names[index]][:, 2][q:]        # v is the transverse velocity component here

    print('x-coordinate, max , min :', "{:.1f}".format(xcoord), "{:.3f}".format(eta.max()), "{:.3f}".format(eta.min()))

    """
    Maxima and minima - outputing these to a csv file for further plotting
    """
    with open("min_max.csv", "a") as file:
        file1 = csv.writer(file)
        file1.writerow([index, xcoord, eta.max(), eta.min()])

    """
    Plot
    """
    if j == N_detectors-1:
        # Plot initialisation
        linewidth = 0.2
        f, axarr = plt.subplots(5, sharex="all", sharey="none", figsize=(8, 6), dpi=200)
        fangle = np.angle(u + v * 1j, deg=True)
        axarr[0].plot(t, eta, lw=linewidth, label=label, c=color)
        axarr[0].set_ylabel('$\eta$ (m)')
        axarr[1].plot(t, u, lw=linewidth, label=label,c=color)
        axarr[1].set_ylabel('$u$ (m/s)')
        axarr[2].plot(t, v, lw=linewidth, label=label, c=color)
        axarr[2].set_ylabel('$v$ (m/s)')
        axarr[3].plot(t, np.sqrt(u ** 2 + v ** 2), lw=linewidth, c=color,label=label)
        axarr[3].set_ylabel('$|U|$ (m/s)')
        axarr[4].plot(t, fangle, lw=linewidth, c=color,label=label)
        axarr[4].set_ylabel('$\\alpha$ $^o$')
        axarr[4].set_ylim([-200, 200])

        plt.xticks(rotation=45)
        plt.xlabel('Time (s)')
        plt.tight_layout()
        f.subplots_adjust(hspace=0)
        plt.show(block=True)


if __name__ == '__main__':
    q = int(5e1)      # consider results after q timesteps,
    L = 180000        # channel length

    # Reads the outputs of simulations
    dataframes = []                           #Consider several dataframes (from different simulations)
    n_cases = [0.02, 0.03]                    #Manning coefficient n cases to be considered
    H_cases = [45,47.5,48.5,49.5,50,52.5,55]  #Depth H cases to be considered

    n=0.02
    for H in H_cases:
        dataframes.append(h5py.File('outputs' + "-" + "n-" + str(n) + "-" + "H-" + str(H) + '/diagnostic_detectors.hdf5', 'r'))

    # Create a list of detector names (follows on the notation used in the simulation)
    names=[]
    N_detectors = len(list(dataframes[0].keys()))-1
    print("Number of Detectors:", N_detectors)
    for k in range(0, N_detectors):
        names.append('detector_'+str(k))

    for df in dataframes:
        # change the index of the names to produce the plot that you like:
        for j in range(0, N_detectors):
            xcoord = float(j/N_detectors) * L # 1e4
            process_results(df, names, xcoord, j, color='blue', )

