import os
import sys
import platform
import shutil
import subprocess
from utils.system_packages import PackageManager, get_package_manager, is_installed, \
    install_package
from utils.shell_utils import print_fancy
from utils.network import download_file
from utils.shell_utils import add_to_path


def is_poppler_installed():
    """
    Checks if Poppler is installed on the system.
    
    Returns:
        bool: True if Poppler is installed, False otherwise.
    """

    return is_installed("pdftoppm")


def install_poppler():
    """
    Installs poppler to the system for PDF -> Image conversion.
    """
    
    platform_type = platform.system()
    package_manager = get_package_manager()
    
    if platform_type == "Windows" and package_manager == PackageManager.CHOCO:
        __install_to_windows()
    elif platform_type == "Darwin" and package_manager == PackageManager.BREW:
        __install_to_mac()
    elif platform_type == "Linux" and package_manager:
        __install_to_linux(package_manager)
    else:
        print_fancy("Poppler not installed and no package manager found to install it.", bold=True, color="red")
        sys.exit(1)

    
def __install_to_windows():
    # Get a temp path
    temp_path = os.getenv("TEMP")
    temp_extract_path = os.path.join(temp_path, "poppler")
    
    # Get the installation path in AppData/Local
    local_app_data = os.getenv("LOCALAPPDATA")
    install_dir = os.path.join(local_app_data, "poppler")
    
    # Download the Windows release of Poppler
    download_file("https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip", "poppler.zip")
    
    # Unzip the release with tar
    subprocess.run(["tar", "-xf", "poppler.zip", "-C", temp_extract_path])
    
    # Move contents of {temp}/Release-24.02.0-0/poppler-24.02.0 to the install directory
    __move_directory_contents(os.path.join(temp_extract_path, "Release-24.02.0-0", "poppler-24.02.0"), install_dir)
    
    # Add to PATH
    add_to_path(os.path.join(install_dir, "Library", "bin"))
    
    pass


def __install_to_mac():
    install_package("poppler")
    
    pass


def __install_to_linux(package_manager):
    if package_manager == PackageManager.APT:
        install_package("poppler-utils")
    elif package_manager == PackageManager.YUM:
        install_package("poppler-utils")
    elif package_manager == PackageManager.PACMAN:
        install_package("poppler")
    elif package_manager == PackageManager.DNF:
        install_package("poppler-utils")
    elif package_manager == PackageManager.ZYPPER:
        install_package("poppler-tools")
    elif package_manager == PackageManager.APK:
        install_package("poppler-utils")
    else:
        print_fancy(f"Unknown package manager: {package_manager}. Cannot install poppler dependency.", bold=True, color="red")
        sys.exit(1)


def __move_directory_contents(src, dest):
    """
    Moves the contents of a directory to another directory.
    
    Args:
        src (str): The source directory.
        dest (str): The destination directory.
    """
    # Ensure the destination directory exists
    if not os.path.exists(dest):
        os.makedirs(dest)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            # Ensure subdirectories exist in destination
            if not os.path.exists(d):
                os.makedirs(d)
            __move_directory_contents(s, d)
        else:
            shutil.move(s, d)
