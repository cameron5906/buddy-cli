import requests


def download_file(url, dest):
    """
    Download a file from a URL to a destination on disk.
    
    Args:
        url (str): The URL to download the file from
        dest (str): The destination path on disk to save the file to
    """
    
    response = requests.get(url)
    response.raise_for_status()
    
    with open(dest, 'wb') as f:
        f.write(response.content)
        
    return dest
