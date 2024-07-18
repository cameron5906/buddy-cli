import subprocess
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel

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
