"""
ReportManager - Integrates S1P file analysis and PDF report generation with ATR system
"""
from pathlib import Path
import os
import shutil
import time
import numpy as np
from scipy.signal import find_peaks
import skrf as rf

from reporting.antennareport_lib import io as ar_io
from reporting.antennareport_lib import analysis as ar_analysis
from reporting.antennareport_lib import plots as ar_plots
from reporting.antennareport_lib import report as ar_report


class ReportManager:
    """Generate comprehensive antenna reports from S1P files"""
    
    def __init__(self, data_dir: str = "./data", reports_dir: str = "./reports"):
        """
        Initialize ReportManager
        
        Args:
            data_dir: Directory containing .s1p and .meta.txt files
            reports_dir: Directory where reports will be generated
        """
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        
    def find_s1p_files(self, directory: str = None) -> list:
        """Find all .s1p files in directory and subdirectories"""
        target_extension = ".s1p"
        search_dir = directory or str(self.data_dir)
        files_of_type = []
        
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith(target_extension):
                    files_of_type.append(os.path.join(root, file))
        
        return files_of_type
    
    def process_single_s1p(
        self,
        s1p_file: str,
        design_freq_ghz: float = None,
        notes: str = "",
        author: str = "",
    ) -> dict:
        """
        Process a single S1P file and generate plots + report
        
        Args:
            s1p_file: Path to .s1p file
            design_freq_ghz: Design frequency in GHz (optional)
            notes: Additional notes for report
            author: Report author name
            
        Returns:
            dict with results including paths to generated files
        """
        results = {
            "success": False,
            "error": None,
            "antname": None,
            "s11_plot": None,
            "smith_chart": None,
            "pdf_report": None,
            "minima_data": None,
        }
        
        try:
            # Load network
            ntwk = rf.Network(s1p_file)
            antname = Path(s1p_file).stem
            results["antname"] = antname
            
            # Prepare output paths
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            figfile = self.reports_dir / f"{antname}_S11.png"
            smith_file = self.reports_dir / f"{antname}_Smith.png"
            pdffile = self.reports_dir / f"{antname}.pdf"
            
            # Read metadata
            meta = ar_io.read_meta_txt(self.data_dir / f"{antname}.meta.txt")
            if design_freq_ghz is None and "design_freq_ghz" in meta:
                try:
                    design_freq_ghz = float(meta["design_freq_ghz"])
                except ValueError:
                    design_freq_ghz = None
            
            meta_notes = meta.get("notes", "")
            if notes:
                meta_notes = notes if not meta_notes else f"{meta_notes} | {notes}"
            
            # Extract S11 data
            freq = ntwk.f / 1e9  # Convert to GHz
            s11_db = ntwk.s_db[:, 0, 0]
            
            # Find peaks (minima in S11, maxima in -S11)
            numpeaks = 4
            db_threshold = -4
            peaks, props = find_peaks(-s11_db, distance=5, width=4, height=-db_threshold)
            peaks = np.sort(peaks)[:numpeaks]
            
            # Find design frequency points
            design_min_idx = ar_analysis.min_s11_in_window(freq, s11_db, design_freq_ghz, window_ghz=0.5)
            design_pt_idx, design_pt_freq, design_pt_s11 = ar_analysis.s11_at_design(freq, s11_db, design_freq_ghz)
            
            # Build minima table data
            minima_rows = [["#", "Frequency (GHz)", "S11 (dB)"]]
            minima_data = []
            
            for i, idx in enumerate(peaks, start=1):
                minima_rows.append([str(i), f"{freq[idx]:.6f}", f"{s11_db[idx]:.2f}"])
                minima_data.append({
                    "index": i,
                    "frequency_ghz": float(freq[idx]),
                    "s11_db": float(s11_db[idx]),
                })
            
            if design_freq_ghz is not None:
                if design_min_idx is not None:
                    minima_rows.append(["Design (±0.5)", f"{freq[design_min_idx]:.6f}", f"{s11_db[design_min_idx]:.2f}"])
                else:
                    minima_rows.append(["Design (±0.5)", "No points in range", "—"])
                if design_pt_idx is not None:
                    minima_rows.append(["At Design f", f"{design_pt_freq:.6f}", f"{design_pt_s11:.2f}"])
            
            results["minima_data"] = minima_data
            
            # Generate plots
            ar_plots.plot_s11(freq, s11_db, peaks, design_min_idx, design_pt_idx, figfile, antname, design_freq_ghz)
            ar_plots.plot_smith(ntwk, peaks, smith_file)
            
            results["s11_plot"] = str(figfile)
            results["smith_chart"] = str(smith_file)
            
            # Collect assets for report
            assets = ar_io.collect_assets(antname, dirs_to_search=[self.data_dir, self.reports_dir])
            
            # Generate PDF report
            ar_report.build_antenna_report(
                output_pdf=str(pdffile),
                antname=antname,
                minima_rows=minima_rows,
                title="Antenna Report",
                subtitle="S-Parameters / Patterns / Measurements",
                author=author,
                notes=("Auto-generated" + (f" | {meta_notes}" if meta_notes else "")),
                design_freq_ghz=design_freq_ghz,
                assets=assets,
            )
            
            results["pdf_report"] = str(pdffile)
            results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
            import traceback
            traceback.print_exc()
        
        return results
    
    def process_all_s1p_files(
        self,
        directory: str = None,
        author: str = "",
        clean_reports_first: bool = True,
    ) -> list:
        """
        Process all S1P files in directory
        
        Args:
            directory: Directory to search (uses data_dir if None)
            author: Report author name
            clean_reports_first: Remove old reports before generating new ones
            
        Returns:
            List of result dictionaries for each file processed
        """
        if clean_reports_first and self.reports_dir.exists():
            shutil.rmtree(self.reports_dir)
        
        files_to_process = self.find_s1p_files(directory)
        results = []
        start_time = time.perf_counter()
        
        print(f"Processing {len(files_to_process)} S1P files...")
        
        for s1p_file in files_to_process:
            result = self.process_single_s1p(s1p_file, author=author)
            results.append(result)
            
            if result["success"]:
                print(f"✓ {result['antname']}: Report generated successfully")
            else:
                print(f"✗ {result['antname']}: {result['error']}")
        
        elapsed = time.perf_counter() - start_time
        print(f"Processing completed in {elapsed:.2f}s")
        
        return results
