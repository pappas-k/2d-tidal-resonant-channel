import math
import numpy as np
from thetis import *


def sinusoidal_tidal_elevation(amplitude=1, period=12.42 * 3600):
    """
    Sinusoidal outer elevation based on time in h.
    :param amplitude: amplitude of tidal wave
    :param period: period of tidal wave, assuming M2 period of approximately 12.42 h
    :return: elevation function for boundary
    """
    omega = 2 * math.pi / period

    def elevation(t):
        return amplitude * math.sin(omega * t)

    return elevation


def output_field_h5(output_directory, field, name):
    """
    Simply outputs a field for further processing
    :param output_directory: output directory
    :param field: Firedrake function field
    :param name: Name of Function to be used in the output file
    :return: none - just outputs file
    """
    checkpoint_file = checkpointing.DumbCheckpoint(f'{output_directory}/{name}')
    checkpoint_file.store(field)
    checkpoint_file.close()


def get_equidistant_points(p1, p2, parts):
    """
    Creates equidistant points between 2 coordinates
    :param p1: (x1,y1) point coordinates
    :param p2: (x2,y2) point coordinates
    :param parts: number of points in the end.
    :return: list of coordinates that can be used in the detectors callback
    """
    return np.array(list(zip(np.linspace(p1[0], p2[0], parts + 1),
                             np.linspace(p1[1], p2[1], parts + 1)))).tolist()
