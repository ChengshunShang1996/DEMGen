#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "1.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "Feb 23, 2026"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

#!!! It only wroks for Windows now

import platform, os, sys, zipfile, subprocess

def setup_kratos():
    # Get the absolute path to the directory containing this script
    base = os.path.dirname(os.path.abspath(__file__))
    system = platform.system()
    
    if system == "Windows":
        # Construct absolute paths
        kratos_path = os.path.abspath(os.path.join(base, "src", "external", "kratos_win", "Release"))
        libs_path = os.path.join(kratos_path, "libs")
        
        # Unzip the Kratos release if it exists
        kratos_zip_path = os.path.abspath(os.path.join(base, "src", "external", "kratos_win"))
        release_zip = os.path.join(kratos_zip_path, "Release.zip")
        if os.path.exists(release_zip):
            with zipfile.ZipFile(release_zip, 'r') as zip_ref:
                zip_ref.extractall(kratos_zip_path)
        
        # --- PERMANENTLY UPDATE PYTHONPATH (Windows) ---
        current_pp = os.environ.get("PYTHONPATH", "")
        if kratos_path not in current_pp:
            new_pp = f"{kratos_path};{current_pp}".strip(";")
            try:
                subprocess.run(['setx', 'PYTHONPATH', new_pp], check=True, capture_output=True)
                print(f"Success: {kratos_path} added to PYTHONPATH permanently.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to set PYTHONPATH: {e}")

        # --- PERMANENTLY UPDATE PATH (Windows) ---
        current_path = os.environ.get("Path", "")
        if libs_path not in current_path:
            new_path = f"{libs_path};{current_path}".strip(";")
            try:
                subprocess.run(['setx', 'Path', new_path], check=True, capture_output=True)
                print(f"Success: {libs_path} added to Path permanently.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to set Path: {e}")

        # Update current process memory
        os.environ["PYTHONPATH"] = f"{kratos_path};{os.environ.get('PYTHONPATH', '')}"
        os.environ["Path"] = f"{libs_path};{os.environ.get('Path', '')}"

    elif system == "Linux":
        # Construct absolute paths
        kratos_path = os.path.abspath(os.path.join(base, "src", "external", "kratos_linux", "Release"))
        libs_path = os.path.join(kratos_path, "libs")
        
        # --- UNZIP FOR LINUX ---
        kratos_zip_path = os.path.abspath(os.path.join(base, "src", "external", "kratos_win"))
        release_zip = os.path.join(kratos_zip_path, "Release.zip")
        if os.path.exists(release_zip):
            with zipfile.ZipFile(release_zip, 'r') as zip_ref:
                zip_ref.extractall(kratos_zip_path)
        
        # --- PERMANENTLY UPDATE .bashrc (Linux) ---
        bashrc = os.path.expanduser("~/.bashrc")
        # Define the lines to be added
        env_lines = [
            f'\n# Kratos Environment Variables',
            f'export PYTHONPATH="{kratos_path}:$PYTHONPATH"',
            f'export LD_LIBRARY_PATH="{libs_path}:$LD_LIBRARY_PATH"\n'
        ]
        
        # Read bashrc to check if already added
        already_set = False
        if os.path.exists(bashrc):
            with open(bashrc, "r") as f:
                if kratos_path in f.read():
                    already_set = True
        
        if not already_set:
            try:
                with open(bashrc, "a") as f:
                    f.writelines(env_lines)
                print(f"Success: Kratos paths added to {bashrc} permanently.")
                print("Please run 'source ~/.bashrc' or restart your terminal.")
            except Exception as e:
                print(f"Failed to update .bashrc: {e}")

        # --- UPDATE CURRENT PROCESS MEMORY ---
        os.environ["PYTHONPATH"] = f"{kratos_path}:{os.environ.get('PYTHONPATH', '')}"
        os.environ["LD_LIBRARY_PATH"] = f"{libs_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
    # Update sys.path for the current Python interpreter session
    if kratos_path not in sys.path:
        sys.path.insert(0, kratos_path)

setup_kratos()