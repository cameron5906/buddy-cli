import subprocess
import sys


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
            print(output.strip())
            full_stdout.append(output)
        if error:
            print(error.strip(), file=sys.stderr)
            full_stderr.append(error)

    return ''.join(full_stdout), ''.join(full_stderr)
