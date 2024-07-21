import os
from abilities import ability, ability_action
from abilities.base_ability import BaseAbility
from utils.shell_utils import print_fancy
from abilities.browsing.view_webpage import handle_view_webpage
from abilities.browsing.perform_google_search import handle_perform_google_search


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
    def view_webpage(self, args):
        return handle_view_webpage(args)
    
    @ability_action("google_search_get_url", "Search Google for web results", {"query": {"type": "string", "description": "A search query. Do NOT use a URL for a search"}, "instructions": "string"}, ["query", "instructions"])
    def perform_google_search(self, args):
        return handle_perform_google_search(args)
