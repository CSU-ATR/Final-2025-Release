import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
from pathlib import Path


def _safe_int_idx(idx, n):
    """Return int(idx) if it is a valid 0..n-1 index, else None"""
    if idx is None:
        return None
    try:
        i = int(idx)
    except (TypeError, ValueError):
        return None
    if 0 <= i < n:
        return i
    return None


def plot_s11(freq, s11_db, peaks, design_min_idx, design_pt_idx, outpath: Path, antname: str, design_freq_ghz=None):
    """Generate S11 magnitude plot with peak annotations"""
    freq = np.asarray(freq)
    s11_db = np.asarray(s11_db)

    n = len(freq)
    if n == 0 or len(s11_db) != n:
        raise ValueError(f"[{antname}] freq/s11_db arrays are empty or mismatched sizes.")

    # --- Debug prints ---
    print(f"\n[{antname}] plot_s11()")
    print(f"  freq range: {freq.min():.6f} .. {freq.max():.6f} GHz")

    # Clean peaks
    peaks_clean = []
    if peaks is not None:
        try:
            for p in np.asarray(peaks).tolist():
                pi = _safe_int_idx(p, n)
                if pi is not None:
                    peaks_clean.append(pi)
        except Exception:
            peaks_clean = []

    print(f"  peaks (valid): {peaks_clean}")

    di = _safe_int_idx(design_min_idx, n)
    dpi = _safe_int_idx(design_pt_idx, n)

    print(f"  design_min_idx (valid): {di}")
    print(f"  design_pt_idx (valid):  {dpi}")

    if di is not None:
        print(f"  design_min point: f={freq[di]:.6f} GHz, S11={s11_db[di]:.2f} dB")
    if dpi is not None:
        print(f"  design_pt point:  f={freq[dpi]:.6f} GHz, S11={s11_db[dpi]:.2f} dB")

    # --- Plot ---
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(freq, s11_db, label="S11 (dB)", color=(0.85, 0.85, 0.3))

    marker_size = 36
    colors_m = ["cyan", "magenta", "lime", "red", "white"]

    # Plot minima peaks
    for i, idx in enumerate(peaks_clean, start=1):
        ax.scatter(
            freq[idx], s11_db[idx],
            marker="o", s=marker_size,
            c=colors_m[(i - 1) % len(colors_m)],
            zorder=5,
            label=f"Min {i}: {s11_db[idx]:.2f} dB @ {freq[idx]:.3f} GHz"
        )

    # Best min near design (filled, always visible)
    if di is not None:
        ax.scatter(
            freq[di], s11_db[di],
            marker="o", s=marker_size,
            c="white",
            zorder=50, clip_on=False,
            label="Min near design"
        )

    # S11 at design frequency (nearest bin) - hollow so it doesn't hide the other
    if dpi is not None:
        ax.scatter(
            freq[dpi], s11_db[dpi],
            marker="D", s=marker_size,
            c="green", edgecolors="black",
            zorder=60, clip_on=False,
            label=f"S11 @ design f: {s11_db[dpi]:.2f} dB"
        )

    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.minorticks_on()
    ax.grid(which="major", alpha=0.35)
    ax.grid(which="minor", alpha=0.15)
    ax.legend(loc="upper right")
    ax.margins(x=0)
    ax.set_xlim(freq[0], freq[-1])
    ax.set_title(f"{antname} S11")

    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        outpath,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.20,
        transparent=False
    )
    plt.close(fig)
    return outpath


def plot_smith(ntwk, peaks, outpath: Path):
    """Generate Smith chart with peak annotations"""
    fig_s, ax_s = plt.subplots(figsize=(6, 6))
    ntwk.plot_s_smith(m=0, n=0, ax=ax_s)

    colors_m = ["cyan", "magenta", "lime", "red"]

    # Robust peaks handling
    peaks_clean = []
    if peaks is not None:
        try:
            peaks_clean = [int(p) for p in np.asarray(peaks).tolist()]
        except Exception:
            peaks_clean = []

    for i, idx in enumerate(peaks_clean, start=1):
        try:
            gamma = ntwk.s[idx, 0, 0]
        except Exception:
            continue
        ax_s.plot(
            np.real(gamma), np.imag(gamma),
            marker="o", markersize=8,
            markeredgecolor=colors_m[(i - 1) % len(colors_m)],
            markerfacecolor="none",
            linewidth=0,
            label=f"Min {i}"
        )

    ax_s.legend(loc="upper right", fontsize=8)
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig_s.savefig(
        outpath,
        dpi=300,
        facecolor=fig_s.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.20,
        transparent=False
    )
    plt.close(fig_s)
    return outpath
