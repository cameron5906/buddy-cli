import os
import sys
import subprocess
import platform
import getpass
from enum import Enum
from typing import Optional
from utils.shell_utils import print_fancy, run_command


class PackageManager(Enum):
    APT = "apt"
    YUM = "yum"
    PACMAN = "pacman"
    DNF = "dnf"
    ZYPPER = "zypper"
    APK = "apk"
    BREW = "brew"
    CHOCO = "choco"

    
def get_package_manager() -> Optional[PackageManager]:
    """
    Determines the package manager used by the system.
    
    Returns:
        Optional[PackageManager]: The package manager used by the system, or None if unknown.
    """

    os_type = platform.system()
    
    if os_type == "Linux":
        if os.path.exists("/etc/debian_version"):
            return PackageManager.APT
        elif os.path.exists("/etc/redhat-release"):
            return PackageManager.YUM
        elif is_installed("pacman"):
            return PackageManager.PACMAN
        elif is_installed("dnf"):
            return PackageManager.DNF
        elif is_installed("zypper"):
            return PackageManager.ZYPPER
        elif is_installed("apk"):
            return PackageManager.APK
    elif os_type == "Darwin":
        if is_installed("brew"):
            return PackageManager.BREW
    elif os_type == "Windows":
        if is_installed("choco"):
            return PackageManager.CHOCO
        
    return None


def update_packages():
    package_manager = get_package_manager()
    os_type = platform.system()
    username = getpass.getuser()
    
    if not package_manager:
        print_fancy(f"Could not determine package manager.", italic=True, color="red")
        sys.exit(1)
    
    if os_type == "Linux":
        if package_manager == PackageManager.APT:
            update_args = ["apt-get", "update"]
        elif package_manager == PackageManager.YUM:
            update_args = ["yum", "update"]
        elif package_manager == PackageManager.PACMAN:
            update_args = ["pacman", "-Sy"]
        elif package_manager == PackageManager.DNF:
            update_args = ["dnf", "update"]
        elif package_manager == PackageManager.ZYPPER:
            update_args = ["zypper", "refresh"]
        elif package_manager == PackageManager.APK:
            update_args = ["apk", "update"]
        else:
            print_fancy(f"Unknown package manager: {package_manager}", italic=True, color="red")
            sys.exit(1)
        
        if username != "root":
            update_args.insert(0, "sudo")
            
        run_command(" ".join(update_args), display_output=False)
    elif os_type == "Darwin":
        if package_manager == PackageManager.BREW:
            subprocess.check_call(["brew", "update"])
        else:
            print_fancy(f"Unknown package manager: {package_manager}", italic=True, color="red")
            sys.exit(1)
    elif os_type == "Windows":
        if package_manager == PackageManager.CHOCO:
            subprocess.check_call(["choco", "upgrade", "all", "-y"])
        else:
            print_fancy(f"Unknown package manager: {package_manager}", italic=True, color="red")
            sys.exit(1)
            

def install_package(package_name):
    """
    Installs a package by name using the detected package manager.
    
    Args:
        package_name (str): The name of the package to install.
    """
    package_manager = get_package_manager()
    
    if not package_manager:
        print_fancy(f"Could not determine package manager.", italic=True, color="red")
        return

    print_fancy(f"Installing {package_name} using {package_manager.value}...", italic=True, color="cyan")
    
    try:
        if package_manager == PackageManager.APT:
            install_args = ["apt-get", "install", "-y", package_name]
        elif package_manager == PackageManager.YUM:
            install_args = ["yum", "install", "-y", package_name]
        elif package_manager == PackageManager.PACMAN:
            install_args = ["pacman", "-S", "--noconfirm", package_name]
        elif package_manager == PackageManager.DNF:
            install_args = ["dnf", "install", "-y", package_name]
        elif package_manager == PackageManager.ZYPPER:
            install_args = ["zypper", "--non-interactive", "install", package_name]
        elif package_manager == PackageManager.APK:
            install_args = ["apk", "add", "--no-cache", package_name]
        elif package_manager == PackageManager.BREW:
            install_args = ["brew", "install", package_name]
        elif package_manager == PackageManager.CHOCO:
            install_args = ["choco", "install", package_name, "-y"]
        else:
            raise ValueError(f"Unknown package manager: {package_manager}")
        
        if platform.system() != "Windows" and getpass.getuser() != "root":
            install_args.insert(0, "sudo")
            
        run_command(" ".join(install_args), display_output=False)
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name} using {package_manager.value}: {e}")


def is_installed(command):
    """
    Checks if a command exists on the system.
    
    Args:
        command (str): The command to check.
    
    Returns:
        bool: True if the command exists, False otherwise.
    """
    try:
        if platform.system() == "Windows":
            subprocess.check_call(["where", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.check_call(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
