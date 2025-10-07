import subprocess
import os

from misc.Logger import Logger

def build_firmware(grbl_source_dir):
    """
    Compiles the GRBL firmware from the specified source directory using Arduino CLI.

    Returns the path to the generated hex file if successful, or None if failed.
    """

    if not os.path.isdir(grbl_source_dir):
        output_message(f"GRBL source directory not found: {grbl_source_dir}", level="error")
        return None

    sketch_name = os.path.basename(grbl_source_dir.rstrip("/\\"))
    fqbn = "arduino:avr:mega"
    build_dir = os.path.join(grbl_source_dir, "build")

    compile_cmd = [
        "arduino-cli", "compile",
        "--fqbn", fqbn,
        "--output-dir", build_dir,
        grbl_source_dir
    ]

    output_message("Compiling GRBL firmware...")
    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            output_message(f"Compilation failed:\n{result.stderr}", level="error")
            return None

        output_message("Compilation successful.")
    except FileNotFoundError:
        output_message("arduino-cli not found. Ensure it is installed and in PATH.", level="error")
        return None

    hex_file = os.path.join(build_dir, f"{sketch_name}.ino.hex")
    if not os.path.isfile(hex_file):
        output_message(f"Compiled hex file not found at: {hex_file}", level="error")
        return None

    return hex_file

def output_message(message, level='info'):
    Logger.ui(message, source='Firmware Builder', level=level)
    

# Path to the folder containing grbl-mega.ino and grbl folder
hex_path = build_firmware("GRBL_SOURCE")

# Upload if build succeeded
if hex_path:
    print(hex_path)