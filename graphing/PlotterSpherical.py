import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
import struct

from graphing.PlotterVariables import PlotterVariables


class PlotterSpherical:
    """
    Spherical radiation pattern plotter + STL exporter.

    - interpolation == 0  -> scatter plot
    - interpolation > 0   -> surface plot
        * 1..5 uses native scan grid
        * >5 upsamples to (target x target), clamped by max_surface_res
    - Smoothness: Gaussian smoothing in angle-space (smoothing_sigma)
    - Geometry fix: handles Elevation rollover when Elevation spans beyond +/-90
      (e.g. -180..180) by folding into [-90,90] with azimuth +180 flip.
    - STL export: exports the CURRENT surface (self.x/self.y/self.z grids) to binary STL.
    """

    def __init__(self, plotter_variables: PlotterVariables):
        self.plotter_variables = plotter_variables

        self.azimuth_values = None
        self.elevation_values = None

        self.theta = None  # radians azimuth
        self.phi = None    # radians elevation (raw; may rollover)
        self.rho = None

        self.x = None
        self.y = None
        self.z = None

        self.azimuth_grid = None
        self.elevation_grid = None
        self.magnitude_grid = None

        # GUI responsiveness knobs
        self.max_surface_res = 200

        # Smoothing strength in grid cells (0 disables smoothing)
        self.smoothing_sigma = 0.8

    
    def update_raw_coordinates(self):
        df = self.plotter_variables.frequency_limited_data
        self.azimuth_values = df["Azimuth"].to_numpy()
        self.elevation_values = df["Elevation"].to_numpy()

    
    def update_polar_scatter_coordinates(self):
        self.theta = np.radians(self.azimuth_values)
        self.phi = np.radians(self.elevation_values)
        self.rho = np.asarray(self.plotter_variables.response_values, dtype=float)

   


    def _build_response_grid(self):
        df = self.plotter_variables.frequency_limited_data
        resp = np.asarray(self.plotter_variables.response_values, dtype=float)

        az = np.sort(df["Azimuth"].unique())
        el = np.sort(df["Elevation"].unique())

        tmp = df[["Azimuth", "Elevation"]].copy()
        tmp["resp"] = resp

       
        R = tmp.pivot(index="Elevation", columns="Azimuth", values="resp").loc[el, az].to_numpy()

    
        if np.isnan(R).any():
            R = np.nan_to_num(R, nan=np.nanmin(R))

        return az, el, R

    def _upsample_grid_if_requested(self, az, el, R):
        target = int(self.plotter_variables.interpolation)

        # 1..5 => native grid
        if target <= 5:
            return az, el, R

        target = min(target, self.max_surface_res)

        interp = RegularGridInterpolator(
            (el, az), R,
            method="linear",
            bounds_error=False,
            fill_value=np.nan
        )

        el_new = np.linspace(el.min(), el.max(), target)
        az_new = np.linspace(az.min(), az.max(), target)
        ELg, AZg = np.meshgrid(el_new, az_new, indexing="ij")

        pts = np.column_stack([ELg.ravel(), AZg.ravel()])
        R_new = interp(pts).reshape(target, target)
        R_new = np.nan_to_num(R_new, nan=np.nanmin(R_new))

        return az_new, el_new, R_new

    def update_polar_grid_coordinates(self):
        self.theta = np.radians(self.azimuth_grid)
        self.phi = np.radians(self.elevation_grid)
        self.rho = np.nan_to_num(self.magnitude_grid)

    
    def update_cartesian_coordinates(self):
        """
        Handles Elevation that spans beyond +/-90 degrees (e.g. -180..180):
        - wrap to [-180, 180)
        - fold into [-90, 90] with azimuth +180 flip
        Then map using elevation-from-XY-plane:
          x = r cos(el) cos(az)
          y = r cos(el) sin(az)
          z = r sin(el)
        """
        theta = np.array(self.theta, dtype=float, copy=True)
        el = np.array(self.phi, dtype=float, copy=True)

        el_deg = np.degrees(el)
        az_deg = np.degrees(theta)

        # Wrap elevation into [-180, 180)
        el_deg = (el_deg + 180.0) % 360.0 - 180.0

        over = el_deg > 90.0
        under = el_deg < -90.0

        # Fold over/under and rotate azimuth by 180°
        el_deg[over] = 180.0 - el_deg[over]
        az_deg[over] += 180.0

        el_deg[under] = -180.0 - el_deg[under]
        az_deg[under] += 180.0

        # Wrap azimuth into [-180, 180) (optional but keeps things tidy)
        az_deg = (az_deg + 180.0) % 360.0 - 180.0

        el = np.radians(el_deg)
        theta = np.radians(az_deg)

        self.x = self.rho * np.cos(el) * np.cos(theta)
        self.y = self.rho * np.cos(el) * np.sin(theta)
        self.z = self.rho * np.sin(el)

    
    def scatter_plot(self):
        self.update_polar_scatter_coordinates()
        self.update_cartesian_coordinates()

        self.plotter_variables.ax.scatter(
            self.x, self.y, self.z,
            c=self.rho,
            cmap=self.plotter_variables.color_map,
            s=8
        )

    def surface_plot(self):
        az, el, R = self._build_response_grid()
        az, el, R = self._upsample_grid_if_requested(az, el, R)

        # Smooth in angle-space
        if self.smoothing_sigma and self.smoothing_sigma > 0:
            R = gaussian_filter(R, sigma=float(self.smoothing_sigma))

        self.azimuth_grid, self.elevation_grid = np.meshgrid(az, el)
        self.magnitude_grid = R

        self.update_polar_grid_coordinates()
        self.update_cartesian_coordinates()

        norm = Normalize(vmin=np.nanmin(self.rho), vmax=np.nanmax(self.rho))
        cmap = plt.cm.get_cmap(self.plotter_variables.color_map)

        self.plotter_variables.ax.plot_surface(
            self.x, self.y, self.z,
            facecolors=cmap(norm(self.rho)),
            rstride=1, cstride=1,
            linewidth=0,
            antialiased=True,
            alpha=0.95, shade = False
        )

    def start_plot(self):
        self.update_raw_coordinates()

        if int(self.plotter_variables.interpolation) == 0:
            self.scatter_plot()
        else:
            self.surface_plot()

        self.plotter_variables.ax.set_title(
            f"Frequency: {self.plotter_variables.current_frequency / 1e9:.2f} GHz"
        )
        self.plotter_variables.fig.canvas.draw_idle()

    
    def _grid_to_triangles(self, X, Y, Z):
        X = np.asarray(X)
        Y = np.asarray(Y)
        Z = np.asarray(Z)

        nrows, ncols = X.shape
        tris = []

        for i in range(nrows - 1):
            for j in range(ncols - 1):
                v00 = np.array([X[i, j], Y[i, j], Z[i, j]], dtype=np.float32)
                v01 = np.array([X[i, j + 1], Y[i, j + 1], Z[i, j + 1]], dtype=np.float32)
                v10 = np.array([X[i + 1, j], Y[i + 1, j], Z[i + 1, j]], dtype=np.float32)
                v11 = np.array([X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1]], dtype=np.float32)

                if not (np.isfinite(v00).all() and np.isfinite(v01).all() and np.isfinite(v10).all() and np.isfinite(v11).all()):
                    continue

                tris.append([v00, v10, v11])
                tris.append([v00, v11, v01])

        if len(tris) == 0:
            return np.zeros((0, 3, 3), dtype=np.float32)

        return np.asarray(tris, dtype=np.float32)

    def _write_binary_stl(self, filepath, triangles, solid_name="radiation_pattern"):
        triangles = np.asarray(triangles, dtype=np.float32)
        ntri = triangles.shape[0]

        header = (solid_name[:80]).ljust(80, " ").encode("ascii", errors="ignore")

        with open(filepath, "wb") as f:
            f.write(header)
            f.write(struct.pack("<I", ntri))

            for tri in triangles:
                v1, v2, v3 = tri[0], tri[1], tri[2]

                n = np.cross(v2 - v1, v3 - v1)
                norm = np.linalg.norm(n)
                if norm > 0:
                    n = n / norm
                else:
                    n = np.array([0.0, 0.0, 0.0], dtype=np.float32)

                f.write(struct.pack("<3f", float(n[0]), float(n[1]), float(n[2])))
                f.write(struct.pack("<3f", float(v1[0]), float(v1[1]), float(v1[2])))
                f.write(struct.pack("<3f", float(v2[0]), float(v2[1]), float(v2[2])))
                f.write(struct.pack("<3f", float(v3[0]), float(v3[1]), float(v3[2])))
                f.write(struct.pack("<H", 0))

    def export_current_surface_to_stl(self, filepath, solid_name=None, target_max_extent=100.0, min_magnitude_fraction=0.0, axis_scale_factors=(1.0, 2.5, 1.0)):
        """
        Export the currently plotted surface grid (self.x/self.y/self.z) to STL.

        Requirements:
        - You must be in surface mode (interpolation > 0) and have plotted at least once.
        
        Args:
            filepath: Output STL file path
            solid_name: Name for the solid in the STL file
            target_max_extent: Target maximum extent in mm (default 100mm).
                             Coordinates are scaled uniformly to fit within this bounding box.
            min_magnitude_fraction: Minimum magnitude threshold as fraction of max (default 0.0 = no filtering).
                                   Parts weaker than this are removed to avoid too-thin geometry.
            axis_scale_factors: Tuple of (x_scale, y_scale, z_scale) for non-uniform scaling (default (1.0, 2.5, 1.0)).
                               Allows exaggerating one axis for better printability (e.g., Y gets 2.5x).
        """
        if solid_name is None:
            solid_name = f"pattern_{self.plotter_variables.current_frequency / 1e9:.3f}GHz"

        if self.x is None or self.y is None or self.z is None:
            raise RuntimeError("No surface available to export. Set interpolation > 0 and plot once first.")

        X = np.asarray(self.x, dtype=float)
        Y = np.asarray(self.y, dtype=float)
        Z = np.asarray(self.z, dtype=float)

        if X.ndim != 2 or Y.ndim != 2 or Z.ndim != 2:
            raise RuntimeError("Surface arrays are not 2D grids. Export requires a surface plot (interpolation > 0).")

        # Apply magnitude threshold to remove weak/thin features (disabled by default)
        if min_magnitude_fraction > 0:
            X, Y, Z = self._filter_by_magnitude(X, Y, Z, min_magnitude_fraction)

        # Apply axis-specific scaling before uniform scaling
        sx, sy, sz = axis_scale_factors
        X = X * sx
        Y = Y * sy
        Z = Z * sz

        # Scale coordinates uniformly to avoid zero-size geometry
        # Calculate bounding box
        x_min, x_max = np.nanmin(X), np.nanmax(X)
        y_min, y_max = np.nanmin(Y), np.nanmax(Y)
        z_min, z_max = np.nanmin(Z), np.nanmax(Z)
        
        current_max_extent = max(x_max - x_min, y_max - y_min, z_max - z_min)
        
        if current_max_extent > 0:
            scale = target_max_extent / current_max_extent
            X = X * scale
            Y = Y * scale
            Z = Z * scale

        triangles = self._grid_to_triangles(X, Y, Z)
        if triangles.shape[0] == 0:
            raise RuntimeError("No valid triangles generated (grid too small, all filtered, or contains NaNs/Infs).")

        self._write_binary_stl(filepath, triangles, solid_name=solid_name)
        return filepath

    def _filter_by_magnitude(self, X, Y, Z, min_magnitude_fraction):
        """
        Filter out regions with low magnitude (far from origin).
        Removes the weakest parts of the radiation pattern that would be too thin.
        
        Args:
            X, Y, Z: 2D coordinate grids
            min_magnitude_fraction: Keep only points where radial distance >= max_radius * fraction
        
        Returns:
            X, Y, Z with weak regions set to NaN
        """
        # Compute radial distance (magnitude)
        R = np.sqrt(X**2 + Y**2 + Z**2)
        
        # Find threshold
        R_max = np.nanmax(R)
        threshold = R_max * min_magnitude_fraction
        
        # Mask regions below threshold
        mask = R < threshold
        
        X_filtered = X.copy()
        Y_filtered = Y.copy()
        Z_filtered = Z.copy()
        
        X_filtered[mask] = np.nan
        Y_filtered[mask] = np.nan
        Z_filtered[mask] = np.nan
        
        return X_filtered, Y_filtered, Z_filtered
