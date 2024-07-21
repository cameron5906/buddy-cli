import os
import undetected_chromedriver as uc
from utils.network import download_file
from utils.shell_utils import is_included_in_path, add_to_path, print_fancy, run_command
from utils.system_packages import is_installed, update_packages, install_package, get_package_manager, PackageManager


def get_driver():
    return uc.Chrome(headless=True, use_subprocess=False, loglevel=50)


def scroll_page(driver):
    """
    Scrolls by the height of the window
    
    Args:
        driver (WebDriver): The WebDriver instance to scroll
    """
    
    driver.execute_script("window.scrollBy(0, window.innerHeight)")

    
def is_scrolled_to_bottom(driver):
    """
    Determines if the page is scrolled to the bottom
    
    Args:
        driver (WebDriver): The WebDriver instance to check
    
    Returns:
        bool: True if the page is scrolled to the bottom, False otherwise
    """
    
    return driver.execute_script("return window.innerHeight + window.scrollY >= document.body.scrollHeight")


def check_chrome_installation():
    """
    Checks for the existence of Chrome on the system.
    If on Windows, ensures that the Chrome path is included in the PATH environment variable.
    """
    
    package_manager = get_package_manager()
    
    return (
        is_installed("google-chrome") or is_installed("chrome")
        and (
            package_manager != PackageManager.CHOCO
            or is_included_in_path("C:\\Program Files\\Google\\Chrome\\Application\\")
        )
    )


def handle_chrome_install():
    """
    Handles the Chrome install process based on the available package manager.
    """
    
    print_fancy("Chrome not found. Installing...", bold=True, color="yellow")
    
    package_manager = get_package_manager()
    
    print_fancy("Updating package list...", italic=True, color="light_gray")
    update_packages()
    
    if package_manager == PackageManager.APT:
        print_fancy("Downloading Chrome Stable...", italic=True, color="light_gray")
        download_file("https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", "/tmp/google-chrome-stable_current_amd64.deb")
        
        print_fancy("Installing...", italic=True, color="light_gray")
        run_command("dpkg -i /tmp/google-chrome-stable_current_amd64.deb", superuser=True, display_output=False)
        run_command("dpkg --configure -a", superuser=True, display_output=False)
        run_command("apt-get install -f -y --fix-missing", superuser=True, display_output=False)
        
        # Clean it up
        os.remove("/tmp/google-chrome-stable_current_amd64.deb")
    elif package_manager == PackageManager.CHOCO:
        print_fancy("Installing Chrome stable...", italic=True, color="light_gray")
        
        install_package("googlechrome")

        if not is_included_in_path("C:\\Program Files\\Google\\Chrome\\Application\\"):
            print_fancy("Chrome not found in PATH. Adding...", italic=True, color="light_gray")
            add_to_path("C:\\Program Files\\Google\\Chrome\\Application\\")
    elif package_manager == PackageManager.YUM:
        print_fancy("Installing Chrome stable...", italic=True, color="light_gray")
        
        # Add Google Chrome repository
        with open('/etc/yum.repos.d/google-chrome.repo', 'w') as repo_file:
            repo_file.write(
                "[google-chrome]\n"
                "name=google-chrome\n"
                "baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64\n"
                "enabled=1\n"
                "gpgcheck=1\n"
                "gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub\n"
            )
            
        run_command("yum install -y google-chrome-stable", superuser=True, display_output=False)
    elif package_manager == PackageManager.BREW:
        print_fancy("Installing Chrome stable...", italic=True, color="light_gray")
        install_package("google-chrome")
    else:
        print_fancy("Could not determine installation method for Chrome", color="red")
        return False
            
    return check_chrome_installation()
