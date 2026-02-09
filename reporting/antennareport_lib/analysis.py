import numpy as np
from typing import Optional, Tuple


def min_s11_in_window(freq_ghz, s11_db, design_freq_ghz, window_ghz=0.05) -> Optional[int]:
    """Find index of minimum S11 within frequency window around design frequency"""
    if design_freq_ghz is None:
        return None

    freq_ghz = np.asarray(freq_ghz)
    s11_db = np.asarray(s11_db)

    lo = design_freq_ghz - window_ghz
    hi = design_freq_ghz + window_ghz

    mask = (freq_ghz >= lo) & (freq_ghz <= hi)
    if not np.any(mask):
        return None

    idxs = np.where(mask)[0]
    best_local = idxs[np.argmin(s11_db[idxs])]
    return int(best_local)


def s11_at_design(freq_ghz, s11_db, design_freq_ghz) -> Tuple[Optional[int], Optional[float], Optional[float]]:
    """Returns (idx, f_at_idx, s11_at_idx) for the sample nearest to design_freq_ghz"""
    if design_freq_ghz is None:
        return None, None, None

    freq_ghz = np.asarray(freq_ghz)
    s11_db = np.asarray(s11_db)

    idx = int(np.argmin(np.abs(freq_ghz - design_freq_ghz)))
    return idx, float(freq_ghz[idx]), float(s11_db[idx])
