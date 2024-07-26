import os
import platform
import subprocess
import sys
from utils.shell_utils import add_to_path, is_included_in_path, print_fancy


def install(args):
    """
    Installs an alias for Buddy to the system. Optionally, allows user to provide a new name for Buddy.

    Args:
        args (dict): The arguments provided by the user
    """
    
    import buddy_cli
    buddy_alias = len(args) > 0 and args[0] or "buddy"

    script_path = os.path.abspath(buddy_cli.__file__)
    os_name = platform.system()
    
    if os_name == "Windows":
        __create_windows_alias(buddy_alias, script_path)
    elif os_name in ["Darwin", "Linux"]:
        __create_bash_alias(buddy_alias, script_path)
    else:
        print_fancy(f"Unsupported OS: {os_name}", bold=True, color="red")
        sys.exit(1)
        
    print_fancy(f"Installed Buddy as '{buddy_alias}'", color="green")


def __create_windows_alias(alias, script_path):
    """
    Creates a Windows cmd alias.

    Args:
        alias (str): The alias to create
        script_path (str): The path to the script to run
    """
    
    python_path = os.path.join(os.path.dirname(script_path), "..", "venv", "Scripts", "python")
    
    bin_dir = os.path.join(os.environ["USERPROFILE"], "bin")
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)
        
    with open(os.path.join(bin_dir, f"{alias}.cmd"), "w") as f:
        f.write(f'@echo off\n{python_path} "{script_path}" %*')

    if not is_included_in_path(bin_dir):
        add_to_path(bin_dir)


def __create_bash_alias(alias, script_path):
    """
    Creates a bash alias.

    Args:
        alias (str): The alias to create
        script_path (str): The path to the script to run
    """
    
    python_path = os.path.join(os.path.dirname(script_path), "..", "venv", "bin", "python")
    
    with open(os.path.expanduser("~/.bashrc"), "a") as f:
        f.write(f'\nalias {alias}="{python_path} {script_path}"\n')
        
    subprocess.run(["source", os.path.expanduser("~/.bashrc")], shell=True)
