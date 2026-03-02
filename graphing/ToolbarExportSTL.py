import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from graphing.PlotController import PlotController


class ToolbarExportSTL:
    def __init__(self, parent, plot_controller: PlotController):
        self.parent = parent
        self.plot_controller = plot_controller

        btn = ttk.Button(parent, text="Export STL", command=self.on_export_stl_clicked)
        btn.pack(side=tk.LEFT, padx=2, pady=2)

    def on_export_stl_clicked(self):
        """Handle Export STL button click."""
        try:
            # Generate default filename with current frequency
            default_filename = self._generate_default_filename()

            # Open Save-As dialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".stl",
                filetypes=[("STL files", "*.stl"), ("All files", "*.*")],
                initialfile=default_filename
            )

            # If user cancels, do nothing
            if not filepath:
                return

            # Attempt export
            self.plot_controller.export_stl(filepath)

            # Show success message
            messagebox.showinfo("Export STL", f"Successfully exported STL to:\n{filepath}")

        except RuntimeError as e:
            # Show validation error
            messagebox.showerror("Export STL Failed", str(e))
        except Exception as e:
            # Show unexpected error
            messagebox.showerror("Export STL Failed", f"Unexpected error: {str(e)}")

    def _generate_default_filename(self) -> str:
        """Generate a default filename based on current frequency."""
        try:
            current_freq = self.plot_controller.plotter_variables.current_frequency
            if current_freq is not None:
                return f"pattern_{current_freq / 1e9:.3f}GHz.stl"
        except Exception:
            pass

        return "pattern.stl"
