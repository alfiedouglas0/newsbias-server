import numpy as np


def scale_2d_plot(values: [float], targetRange: [float] = [100, 100],
                  centerPoint: [float] = [0, 0]):
    v_range = np.ptp(values, axis=0)
    # Change 0s to 1s to prevent div by 0
    v_range = np.where(v_range == 0, 1, v_range)
    scale = v_range / np.array(targetRange)
    scaled_values = np.array(values) / scale
    return (scaled_values -
            (np.amin(scaled_values, axis=0) -
             ((np.array(centerPoint) - np.array(targetRange)) / 2.0)))
