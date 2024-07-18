import subprocess
import sys
from rich.console import Console
from rich.text import Text

console = Console()


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    full_stdout = []
    full_stderr = []

    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output == '' and error == '' and process.poll() is not None:
            break
        if output:
            print_fancy(output.strip(), italic=True, color="light_gray")
            full_stdout.append(output)
        if error:
            print_fancy(error.strip(), italic=True, color="red")
            full_stderr.append(error)

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
