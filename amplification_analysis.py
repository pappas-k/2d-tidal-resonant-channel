"""
Tidal amplification analysis for the resonant channel model.

Reads the min_max.csv file produced by detector_interpreter_min_max.py and plots
the tidal envelope (maximum and minimum water surface elevation) along the channel
for multiple water depth cases. This allows visual comparison of how depth affects
resonance amplification.

Usage:
    1. Run resonant_channel.py for each depth case to generate simulation outputs.
    2. Run detector_interpreter_min_max.py to produce min_max.csv.
    3. Run this script to generate the amplification plot.

Input:
    min_max.csv  - CSV file with columns: index, xcoord, eta_max, eta_min
                   Each depth case contributes 21 rows (one per detector).

Output:
    Matplotlib plot of eta_max and eta_min vs normalised channel position (x/lx)
    for each depth case.

Written by Konstantinos Pappas. Edited by Thanasis Angeloudis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc


rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica'], 'size': 18})
rc('text', usetex=True)



file= "min_max.csv"    #read the min_max.csv with the maximum and minimum values of elevation eta
df=pd.read_csv(file, names=['index', 'xcoord', 'eta_max', 'eta_min'] )   #convert it to a dataframe
print(df)

lx=180000
H_cases = [45,47.5,48.5,49.5,50,52.5,55]
H_labels = ['H=45 m','H=47.5 m','H=48.5 m','H=49.5 m','H=50 m','H=52.5 m','H=55 m']
print(df['eta_max'][0:10])
colors = ["red", "blue" , "green", "orange", "purple", "k", "lightseagreen"]
linewidth = 0.8

for j in np.arange(0,len(H_cases)):
    i=j*21
    plt.plot(df['xcoord'][0:21] / lx, df['eta_max'][i:i+21], label=H_labels[j], color=colors[j], lw=linewidth)
    plt.plot(df['xcoord'][0:21] / lx, df['eta_min'][i:i + 21], color=colors[j], lw=linewidth)

plt.legend()
plt.show()