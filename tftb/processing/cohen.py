#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 jaidev <jaidev@newton>
#
# Distributed under terms of the MIT license.

"""
Bilinear Time-Frequency Processing in the Cohen’s Class.
"""

import warnings
import numpy as np

from tftb.utils import nextpow2


def pseudo_wigner_ville(signal, time_samples=None, freq_bins=None, window=None):
    """Compute the Pseudo Wigner Ville time frequency distribution.

    :param signal: Signal to analyze.
    :param time_samples: time instants
    :param freq_bins: Number of frequency bins.
    :param window: Frequency smoothing window (Default: Hamming of length
    signal-length / 4)
    :type signal: array-like.
    :type time_samples: array-like
    :type freq_bins: int
    :type window: array-like
    :return: Pseudo Wigner Ville time frequency distribution.
    :rtype: array-like
    """
    if time_samples is None:
        time_samples = np.arange(signal.shape[0])

    if freq_bins is None:
        freq_bins = signal.shape[0]

    if 2 ** nextpow2(freq_bins) != freq_bins:
        msg = "For faster computation, the frequency bins should be a power of 2."
        warnings.warn(msg, UserWarning)

    if window is None:
        winlength = np.floor(signal.shape[0] / 4.0)
        winlength = winlength + 1 - np.remainder(winlength, 2)
        from scipy.signal import hamming
        window = hamming(int(winlength))
    elif window.shape[0] % 2 == 0:
        raise ValueError('The smoothing window must have an odd length.')

    tfr = np.zeros((freq_bins, time_samples.shape[0]), dtype=complex)
    lh = (window.shape[0] - 1) / 2
    for icol in xrange(time_samples.shape[0]):
        ti = time_samples[icol]
        taumaxvals = (ti, signal.shape[0] - ti - 1,
                      np.round(signal.shape[0] / 2.0), lh)
        taumax = np.min(taumaxvals)
        tau = np.arange(-taumax, taumax + 1).astype(int)
        indices = np.remainder(freq_bins + tau, freq_bins).astype(int)
        tfr[indices, icol] = window[lh + tau] * signal[ti + tau - 1] * \
            np.conj(signal[ti - tau - 1])
        tau = np.round(freq_bins / 2.0)
        if (ti <= signal.shape[0] - tau) and (ti >= tau + 1) and (tau <= lh):
            tfr[int(tau), icol] = 0.5 * (window[lh + tau] * signal[ti + tau - 1] *
                    np.conj(signal[ti - tau - 1]) + window[lh - tau] *
                    signal[ti - tau - 1] * np.conj(signal[ti + tau - 1]))

    tfr = np.fft.fft(tfr)
    return np.real(tfr)


def wigner_ville(signal, time_samples=None, freq_bins=None):
    """Compute the Wigner Ville time frequency distribution.

    :param signal: Signal to analyze.
    :param time_samples: time instants
    :param freq_bins: Number of frequency bins.
    :type signal: array-like.
    :type time_samples: array-like
    :type freq_bins: int
    :return: Wigner Ville time frequency distribution.
    :rtype: array-like
    """
    if time_samples is None:
        time_samples = np.arange(signal.shape[0])

    if freq_bins is None:
        freq_bins = signal.shape[0]

    if 2 ** nextpow2(freq_bins) != freq_bins:
        msg = "For faster computation, the frequency bins should be a power of 2."
        warnings.warn(msg, UserWarning)

    tfr = np.zeros((freq_bins, time_samples.shape[0]), dtype=complex)

    for icol in xrange(time_samples.shape[0]):
        ti = time_samples[icol]
        taumax = np.min((ti, signal.shape[0] - ti - 1,
                         np.round(freq_bins / 2.0) - 1))
        tau = np.arange(-taumax, taumax + 1).astype(int)
        indices = np.remainder(freq_bins + tau, freq_bins).astype(int)
        tfr[indices, icol] = signal[ti + tau] * np.conj(signal[ti - tau])
        tau = np.round(freq_bins / 2.0)
        if (ti <= signal.shape[0] - tau) and (ti >= tau + 1):
            tfr[tau, icol] = 0.5 * (signal[ti + tau, 0] * np.conj(signal[ti - tau, 0])) + \
                                   (signal[ti - tau, 0] * np.conj(signal[ti + tau, 0]))

    tfr = np.fft.fft(tfr, axis=0)
    tfr = np.real(tfr)
    return tfr


if __name__ == '__main__':
    from tftb.generators.api import fmsin
    signal, _ = fmsin(128)
    tfr = wigner_ville(signal)
    from matplotlib.pyplot import imshow, show
    imshow(tfr)
    show()
