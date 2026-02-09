"""
GUI View for Report Generation Interface
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


class ReportGeneratorView:
    """GUI interface for generating antenna reports"""
    
    def __init__(self, parent_frame):
        """Initialize report generator view"""
        self.frame = ttk.LabelFrame(parent_frame, text="Report Generator", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data directory selection
        dir_frame = ttk.Frame(self.frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(dir_frame, text="Data Directory:").pack(side=tk.LEFT)
        self.data_dir_var = tk.StringVar(value="./data")
        ttk.Entry(dir_frame, textvariable=self.data_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_data_dir).pack(side=tk.LEFT)
        
        # Reports directory
        reports_frame = ttk.Frame(self.frame)
        reports_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(reports_frame, text="Reports Directory:").pack(side=tk.LEFT)
        self.reports_dir_var = tk.StringVar(value="./reports")
        ttk.Entry(reports_frame, textvariable=self.reports_dir_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(reports_frame, text="Browse", command=self.browse_reports_dir).pack(side=tk.LEFT)
        
        # Design frequency
        freq_frame = ttk.Frame(self.frame)
        freq_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(freq_frame, text="Design Freq (GHz):").pack(side=tk.LEFT)
        self.design_freq_var = tk.StringVar(value="")
        ttk.Entry(freq_frame, textvariable=self.design_freq_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # Author
        author_frame = ttk.Frame(self.frame)
        author_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(author_frame, text="Author:").pack(side=tk.LEFT)
        self.author_var = tk.StringVar(value="")
        ttk.Entry(author_frame, textvariable=self.author_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Notes
        notes_frame = ttk.Frame(self.frame)
        notes_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(notes_frame, text="Notes:").pack(side=tk.LEFT)
        self.notes_var = tk.StringVar(value="")
        ttk.Entry(notes_frame, textvariable=self.notes_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.process_all_btn = ttk.Button(button_frame, text="Process All S1P Files")
        self.process_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.process_single_btn = ttk.Button(button_frame, text="Process Single File")
        self.process_single_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress/Status text
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(anchor=tk.NW)
        
        scrollbar = ttk.Scrollbar(status_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_text = tk.Text(status_frame, height=6, yscrollcommand=scrollbar.set)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.status_text.yview)
        
    def browse_data_dir(self):
        """Browse for data directory"""
        dir_path = filedialog.askdirectory(title="Select Data Directory")
        if dir_path:
            self.data_dir_var.set(dir_path)
    
    def browse_reports_dir(self):
        """Browse for reports directory"""
        dir_path = filedialog.askdirectory(title="Select Reports Directory")
        if dir_path:
            self.reports_dir_var.set(dir_path)
    
    def get_config(self) -> dict:
        """Get current configuration from view"""
        design_freq = None
        if self.design_freq_var.get().strip():
            try:
                design_freq = float(self.design_freq_var.get())
            except ValueError:
                pass
        
        return {
            "data_dir": self.data_dir_var.get(),
            "reports_dir": self.reports_dir_var.get(),
            "design_freq_ghz": design_freq,
            "author": self.author_var.get(),
            "notes": self.notes_var.get(),
        }
    
    def append_status(self, message: str):
        """Append message to status text box"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.update()
    
    def clear_status(self):
        """Clear status text"""
        self.status_text.delete(1.0, tk.END)
