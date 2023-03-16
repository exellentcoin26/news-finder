import os
import sys


def add_module_to_python_path():
    # Add the parent directory of this script to the Python path
    main_script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(main_script_dir, ".."))

    sys.path.append(parent_dir)


add_module_to_python_path()
