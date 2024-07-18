def execute_with_confirmation(command):
    """"
    This method will execute a shell command after asking the user for confirmation.
    
    Args:
    command (str): The shell command to execute
    """
    
    print(f"About to execute: {command}")
    confirm = input("Do you want to proceed? (yes/no): ").strip().lower()

    if confirm == 'yes':
        import subprocess
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
        else:
            print("Command executed successfully.")
    else:
        print("Command execution cancelled.")
