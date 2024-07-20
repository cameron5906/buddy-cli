import os
from abilities import ability, ability_action
from base_ability import BaseAbility
from utils.system_packages import is_installed, update_packages, install_package, get_package_manager, PackageManager
from utils.shell_utils import print_fancy, is_included_in_path, add_to_path, run_command
from utils.network import download_file
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


@ability("browsing", "Browse the web for research tasks", {})
class Browsing(BaseAbility):
    """
    The browsing ability allows Buddy to search Google, look at webpages and perform other browsing tasks.
    """

    def enable(self, args=None):
        """
        Enablement process of the browsing ability. Installs Google Chrome if not already installed.
        """
        print_fancy("Enabling browsing ability...", bold=True, color="cyan")
        
        if not self.__check_chrome_installation():
            if not self.__handle_chrome_install():
                print_fancy("Failed to install Chrome", bold=True, color="red")
                return False
        else:
            print_fancy("Chrome found", italic=True, color="cyan")
            
        return True
    
    def disable(self):
        pass
    
    @ability_action("view_webpage_url", "Opens a webpage URL to seek information using the instructions provided", {"url": "string", "instructions": "string"}, ["url", "instructions"])
    def view_webpage(self, model, args):
        """
        Allows Buddy to view a webpage using a web browser with vision capabilities.
        Buddy is provided with the following tools:
            stop_reading: Allows Buddy to stop reading the webpage when the instructions have been fulfilled
            add_note: Allows Buddy to add a note to the findings
        
        Args:
            model (BaseModel): The model that is calling the action
            args (dict): The arguments for the search from the model
                url (str): The URL of the webpage to view
                instructions (str): The instructions for what to do on the page
                
        Returns:
            str: An explanation of the findings
        """
        
        url = args["url"]
        instructions = args["instructions"]
        messages = [
            {
                "role": "system",
                "content": f"""
You are viewing a webpage to look for information. You will be provided with instructions on what to do on the webpage.

Obey the following guidelines:
- Provide supporting information back to the user by using the add_note tool
- Upon fulfilling the instructions, stop reading the webpage using the stop_reading tool
- Your notes should be formatted as markdown text
"""
            },
            {
                "role": "user",
                "content": instructions
            }
        ]
        tools = [
            model.make_tool(
                "stop_reading",
                "Stop reading the webpage when you have found the information you need",
                {},
                []
            ),
            model.make_tool(
                "add_note",
                "Add a note to your findings",
                {"note": "string"},
                ["note"]
            )
        ]
        
        driver = self.__get_driver()
        
        print_fancy(f"Opening webpage {url}: {instructions}", italic=True, color="cyan")
        
        driver.get(url)
        
        result_segments = []
        first_look = True
        
        while first_look or not self.__is_scrolled_to_bottom(driver):
            first_look = False
            screen_base64 = driver.get_screenshot_as_base64()
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screen_base64}"
                        }
                    }
                ]
            })
            
            response = model.run_inference(
                messages=messages,
                tools=tools
            )
            
            messages.append(response.choices[0])
            
            note_call_id, note_call_args, note_call = model.get_tool_call("add_note", response)
            
            if note_call_id is not None:
                result_segments.append(note_call_args["note"])
                messages.append(model.make_tool_result(note_call, "Success"))
                
            if model.get_tool_call("stop_reading", response)[0] is not None:
                break
                
            if not self.__is_scrolled_to_bottom(driver):
                print_fancy("Scrolling for more information...", italic=True, color="cyan")
                self.__scroll_page(driver)
            
        driver.close()
        
        print_fancy("Finished reading the webpage", italic=True, color="cyan")
        
        if len(result_segments) == 0:
            return "No information found"
        
        return "\\n\\n".join(result_segments)
    
    @ability_action("google_search_get_url", "Search Google for web results", {"query": {"type": "string", "description": "A search query. Do NOT use a URL for a search"}, "instructions": "string"}, ["query", "instructions"])
    def perform_google_search(self, model, args):
        """
        Allows Buddy to perform a Google search using a web browser with vision capabilities.
        Buddy is provided with the following tools:
            get_link_url: Retrieves the URL by using the title of the search result
        
        Args:
            model (BaseModel): The model that is calling the action
            args (dict): The arguments for the search from the model
                query (str): The search query
                instructions (str): The instructions for the search
                
        Returns:
            str | None: The URL of the first search result, or None if no matching results were found
        """
        
        instructions = args["instructions"]
        query = args["query"]
        
        search_url = f"https://www.google.com/search?q={query}"
        messages = [
            {
                "role": "system",
                "content": f"""
You are performing a Google search based on the instructions provided to you by the user. You will locate the first result that best matches these instructions and provide the URL back to the user.
You will use your vision capabilities to view the results from the Google search page.
You will be able to scroll down the page in order to find the best result.
When you have found a result that you believe matches the goal of the search, you will use your get_link_url tool to retrieve the URL for that result, which will then be returned to the user.
"""
            },
            {
                "role": "user",
                "content": instructions
            }
        ]
        tools = [
            model.make_tool(
                "get_link_url",
                "Retrieves the URL by using the title of the search result",
                {"link_text": "string"},
                ["link_text"]
            )
        ]
        
        driver = self.__get_driver()
        
        print_fancy(f"Performing Google search for '{query}': {instructions}", italic=True, color="cyan")
        
        driver.get(search_url)
        
        print_fancy("Checking results...", italic=True, color="cyan")
        
        result = None
        
        while result is None and not self.__is_scrolled_to_bottom(driver):
            screen_base64 = driver.get_screenshot_as_base64()
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screen_base64}"
                        }
                    }
                ]
            })
            
            response = model.run_inference(
                messages=messages,
                tools=tools
            )
            
            messages.append(response.choices[0])
            
            call_id, call_args, call = model.get_tool_call("get_link_url", response)
            
            if call_id is not None:
                link_text = call_args["link_text"]
                link = driver.find_element(By.PARTIAL_LINK_TEXT, link_text)
                
                # If its not an anchor, find the closest one
                if link.tag_name != "a":
                    link = link.find_element_by_tag_name("a")
                    
                result = link.get_attribute("href")
                
                messages.append(model.make_tool_result(call, result))
                break
                
            self.__scroll_page(driver)
        
        driver.quit()
        
        if result is None:
            return "No results found"
        
        return result
    
    def __get_driver(self):
        return uc.Chrome(headless=True, use_subprocess=False, loglevel=50)

    def __scroll_page(self, driver):
        """
        Scrolls by the height of the window
        
        Args:
            driver (WebDriver): The WebDriver instance to scroll
        """
        
        driver.execute_script("window.scrollBy(0, window.innerHeight)")
        
    def __is_scrolled_to_bottom(self, driver):
        """
        Determines if the page is scrolled to the bottom
        
        Args:
            driver (WebDriver): The WebDriver instance to check
        
        Returns:
            bool: True if the page is scrolled to the bottom, False otherwise
        """
        
        return driver.execute_script("return window.innerHeight + window.scrollY >= document.body.scrollHeight")

    def __check_chrome_installation(self):
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

    def __handle_chrome_install(self):
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
                
        return self.__check_chrome_installation()
