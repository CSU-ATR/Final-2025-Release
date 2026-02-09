#!/usr/bin/env python3
"""
Example usage of the ReportManager for S1P file analysis and PDF report generation
"""

from reporting import ReportManager
from pathlib import Path


def example_1_process_all_files():
    """Example: Process all S1P files in a directory"""
    print("=" * 60)
    print("EXAMPLE 1: Process All S1P Files")
    print("=" * 60)
    
    # Create report manager
    report_mgr = ReportManager(
        data_dir="./datasets",  # Where S1P files are
        reports_dir="./reports"  # Where to save reports
    )
    
    # Process all S1P files
    results = report_mgr.process_all_s1p_files(
        author="ATR System",
        clean_reports_first=True  # Delete old reports first
    )
    
    # Print summary
    print("\nProcessing Summary:")
    print("-" * 60)
    for result in results:
        if result["success"]:
            print(f"✓ {result['antname']}")
            print(f"  S11 Plot: {result['s11_plot']}")
            print(f"  Smith Chart: {result['smith_chart']}")
            print(f"  PDF Report: {result['pdf_report']}")
        else:
            print(f"✗ {result['antname']}: {result['error']}")
    
    print("\n" + "=" * 60)


def example_2_process_single_file():
    """Example: Process a single S1P file with metadata"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Process Single S1P File")
    print("=" * 60)
    
    report_mgr = ReportManager(
        data_dir="./datasets",
        reports_dir="./reports"
    )
    
    # Process specific file
    result = report_mgr.process_single_s1p(
        s1p_file="./datasets/BestSphericalHorn4-16-25.csv",
        design_freq_ghz=4.0,
        notes="Horn antenna test at 4 GHz design frequency",
        author="Test User"
    )
    
    if result["success"]:
        print(f"Successfully processed: {result['antname']}")
        print(f"\nGenerated Files:")
        print(f"  S11 Plot: {result['s11_plot']}")
        print(f"  Smith Chart: {result['smith_chart']}")
        print(f"  PDF Report: {result['pdf_report']}")
        
        print(f"\nS11 Minima Found:")
        for minima in result["minima_data"]:
            freq = minima["frequency_ghz"]
            s11 = minima["s11_db"]
            print(f"  Min {minima['index']}: {freq:.4f} GHz @ {s11:.2f} dB")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 60)


def example_3_custom_analysis():
    """Example: Custom analysis of S1P data"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Analysis")
    print("=" * 60)
    
    try:
        import skrf as rf
        import numpy as np
        
        # Load S1P file directly
        s1p_path = "./datasets/BestSphericalHorn4-16-25.csv"
        if not Path(s1p_path).exists():
            print(f"File not found: {s1p_path}")
            return
        
        ntwk = rf.Network(s1p_path)
        
        print(f"Network Information:")
        print(f"  Frequency range: {ntwk.f[0]/1e9:.3f} - {ntwk.f[-1]/1e9:.3f} GHz")
        print(f"  Number of points: {len(ntwk.f)}")
        print(f"  S11 range: {ntwk.s_db[:,0,0].min():.2f} - {ntwk.s_db[:,0,0].max():.2f} dB")
        
        # Find minimum S11
        min_idx = np.argmin(ntwk.s_db[:, 0, 0])
        min_freq = ntwk.f[min_idx] / 1e9
        min_s11 = ntwk.s_db[min_idx, 0, 0]
        
        print(f"\n  Best S11 Match:")
        print(f"    Frequency: {min_freq:.4f} GHz")
        print(f"    S11: {min_s11:.2f} dB")
        print(f"    VSwr: {(1 + np.abs(ntwk.s[min_idx, 0, 0])) / (1 - np.abs(ntwk.s[min_idx, 0, 0])):.2f}")
        
    except Exception as e:
        print(f"Error in custom analysis: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nATR Report Generation Examples\n")
    
    # Uncomment the examples you want to run:
    
    # example_1_process_all_files()
    # example_2_process_single_file()
    # example_3_custom_analysis()
    
    print("\nTo run examples:")
    print("1. Make sure you have S1P files in ./datasets/")
    print("2. Uncomment the example functions you want to run")
    print("3. Run: python examples.py")
    print("\nFor full GUI integration, run: python ATR.py")
