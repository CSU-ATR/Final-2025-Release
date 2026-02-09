from pathlib import Path
from typing import List, Optional, Tuple

def read_meta_txt(meta_path: Path) -> dict:
    """Read metadata from .meta.txt file"""
    meta = {}
    if not meta_path.exists():
        return meta
    for line in meta_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta


def find_first_image_by_stem(dirs: List[Path], stem: str) -> Optional[Path]:
    """Find first image file matching stem in list of directories"""
    exts = {".png", ".jpg", ".jpeg"}
    for d in dirs:
        if not d:
            continue
        pdir = Path(d)
        if not pdir.exists():
            continue
        for ext in exts:
            p = pdir / f"{stem}{ext}"
            if p.exists():
                return p
    return None


def collect_assets(antname: str, dirs_to_search: List[Path]) -> List[Tuple[str, Path]]:
    """Collect antenna assets (images) for report assembly"""
    ordered_suffixes = [
        ("3D Pattern", f"{antname}_3D"),
        ("Phi Cut", f"{antname}_phi"),
        ("Theta Cut", f"{antname}_theta"),
        ("Antenna Front", f"{antname}_front"),
        ("Antenna Back", f"{antname}_back"),
        ("S11 Plot", f"{antname}_S11"),
        ("Smith Chart", f"{antname}_Smith"),
    ]

    assets = []
    for title, stem in ordered_suffixes:
        p = find_first_image_by_stem(dirs_to_search, stem)
        if p is not None:
            assets.append((title, p))
    return assets
