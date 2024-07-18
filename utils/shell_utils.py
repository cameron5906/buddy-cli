import os
import socket
import subprocess
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel
import requests
import platform
import getpass

console = Console()


def format_markdown_for_terminal(markdown_text):
    md = Markdown(markdown_text)
    console.print(Panel(md, expand=True, border_style="bold blue"))


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    full_stdout = []
    full_stderr = []

    stdout_iter = iter(process.stdout.readline, '')
    stderr_iter = iter(process.stderr.readline, '')

    for stdout_line in stdout_iter:
        print_fancy(stdout_line.strip(), italic=True, color="light_gray")
        full_stdout.append(stdout_line)
    
    for stderr_line in stderr_iter:
        print_fancy(stderr_line.strip(), italic=True, color="red")
        full_stderr.append(stderr_line)

    process.stdout.close()
    process.stderr.close()
    process.wait()

    return ''.join(full_stdout), ''.join(full_stderr)


def print_fancy(text, bold=False, italic=False, underline=False, color=None, bg=None):
    text_obj = Text(text)
    
    if bold:
        text_obj.stylize("bold")
    if italic:
        text_obj.stylize("italic")
    if underline:
        text_obj.stylize("underline")
    if color:
        text_obj.stylize(color)
    if bg:
        text_obj.stylize(f"on {bg}")

    console.print(text_obj)


def get_system_context():
    # Operating system
    os_name = platform.system()
    os_version = platform.version()
    os_details = platform.uname()

    # Local network IP
    local_ip = socket.gethostbyname(socket.gethostname())

    # External IP
    try:
        external_ip = requests.get('https://api.ipify.org').text
    except requests.RequestException:
        external_ip = 'Unavailable'

    # Username
    username = getpass.getuser()

    # Current working directory
    cwd = os.getcwd()

    # Current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    context = (
        f"**Operating System:** {os_name} {os_version}\n"
        f"**OS Details:** {os_details}\n"
        f"**Local Network IP:** {local_ip}\n"
        f"**External IP:** {external_ip}\n"
        f"**Username:** {username}\n"
        f"**Current Working Directory:** {cwd}\n"
        f"**Current Date and Time:** {current_datetime}"
    )

    return context
