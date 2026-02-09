"""
ViewController for Report Generation Interface
Handles logic between View and Model
"""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading

from gui.ReportGeneratorView import ReportGeneratorView
from reporting.ReportManager import ReportManager


class ReportGeneratorViewController:
    """Controller for report generation interface"""
    
    def __init__(self, parent_frame):
        """Initialize controller with view"""
        self.view = ReportGeneratorView(parent_frame)
        self.report_manager = None
        self.processing = False
        
        # Connect buttons to handlers
        self.view.process_all_btn.config(command=self.on_process_all)
        self.view.process_single_btn.config(command=self.on_process_single)
    
    def on_process_all(self):
        """Handle process all button click"""
        if self.processing:
            messagebox.showwarning("Warning", "Processing already in progress")
            return
        
        config = self.view.get_config()
        
        # Validate directories
        data_dir = Path(config["data_dir"])
        if not data_dir.exists():
            messagebox.showerror("Error", f"Data directory not found: {data_dir}")
            return
        
        # Run in background thread
        self.processing = True
        self.view.clear_status()
        self.view.append_status("Starting report generation...")
        
        thread = threading.Thread(
            target=self._process_all_worker,
            args=(config,),
            daemon=True
        )
        thread.start()
    
    def _process_all_worker(self, config: dict):
        """Worker thread for processing all S1P files"""
        try:
            self.report_manager = ReportManager(
                data_dir=config["data_dir"],
                reports_dir=config["reports_dir"]
            )
            
            results = self.report_manager.process_all_s1p_files(
                directory=config["data_dir"],
                author=config["author"],
                clean_reports_first=True,
            )
            
            # Display results
            self.view.append_status("\n=== Report Generation Complete ===")
            
            success_count = sum(1 for r in results if r["success"])
            total_count = len(results)
            
            self.view.append_status(f"Processed: {success_count}/{total_count} files successfully")
            
            for result in results:
                if result["success"]:
                    self.view.append_status(f"✓ {result['antname']}")
                else:
                    self.view.append_status(f"✗ {result['antname']}: {result['error']}")
            
            self.view.append_status(f"\nReports saved to: {config['reports_dir']}")
            
            if success_count == total_count:
                messagebox.showinfo("Success", f"Generated {success_count} reports successfully!")
            else:
                messagebox.showwarning(
                    "Partial Success",
                    f"Generated {success_count}/{total_count} reports\n({total_count - success_count} failed)"
                )
        
        except Exception as e:
            self.view.append_status(f"\nERROR: {str(e)}")
            messagebox.showerror("Error", f"Report generation failed:\n{str(e)}")
        
        finally:
            self.processing = False
    
    def on_process_single(self):
        """Handle process single file button click"""
        if self.processing:
            messagebox.showwarning("Warning", "Processing already in progress")
            return
        
        config = self.view.get_config()
        
        # File dialog
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select S1P File",
            initialdir=config["data_dir"],
            filetypes=[("S1P Files", "*.s1p"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Run in background thread
        self.processing = True
        self.view.clear_status()
        self.view.append_status(f"Processing: {Path(file_path).name}")
        
        thread = threading.Thread(
            target=self._process_single_worker,
            args=(file_path, config),
            daemon=True
        )
        thread.start()
    
    def _process_single_worker(self, file_path: str, config: dict):
        """Worker thread for processing single S1P file"""
        try:
            self.report_manager = ReportManager(
                data_dir=config["data_dir"],
                reports_dir=config["reports_dir"]
            )
            
            result = self.report_manager.process_single_s1p(
                s1p_file=file_path,
                design_freq_ghz=config["design_freq_ghz"],
                notes=config["notes"],
                author=config["author"],
            )
            
            if result["success"]:
                self.view.append_status(f"\n✓ Successfully processed {result['antname']}")
                self.view.append_status(f"\nGenerated files:")
                self.view.append_status(f"  S11 Plot: {result['s11_plot']}")
                self.view.append_status(f"  Smith Chart: {result['smith_chart']}")
                self.view.append_status(f"  PDF Report: {result['pdf_report']}")
                
                messagebox.showinfo("Success", f"Report generated for {result['antname']}")
            else:
                self.view.append_status(f"\n✗ Failed: {result['error']}")
                messagebox.showerror("Error", f"Failed to process file:\n{result['error']}")
        
        except Exception as e:
            self.view.append_status(f"\nERROR: {str(e)}")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
        
        finally:
            self.processing = False
