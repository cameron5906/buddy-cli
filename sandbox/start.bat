@echo off
REM Batch script to build a sandbox Docker image for buddy using Ubuntu 20.04

REM Define image and container names
set IMAGE_NAME=buddy_cli
set CONTAINER_NAME=buddy_sandbox
set HASH_FILE=last_image_hash.txt

REM Enable delayed expansion for variable handling inside loops
setlocal EnableDelayedExpansion

REM The update flag will skip the image build and only update the Python files in the existing container
REM WARNING: This will not install new requirements or update the Python environment in any way
if "%1%"=="update" (
    echo Update mode enabled. Skipping image build...
    call :check_container_existence
    if "%CONTAINER_EXISTS%"=="1" (
        call :check_container_running
        if "%CONTAINER_RUNNING%"=="1" (
            call :copy_python_files
            echo Restarting the container...
            docker restart %CONTAINER_NAME%
            docker exec -it %CONTAINER_NAME% /bin/bash
            goto :eof
        ) else (
            echo Container %CONTAINER_NAME% exists but is not running. Starting the container...
            call :start_container
            call :copy_python_files
            docker exec -it %CONTAINER_NAME% /bin/bash
            goto :eof
        )
    ) else (
        echo Container does not exist, proceeding with regular build and run flow...
        call :regular_flow
        goto :eof
    )
) else (
    call :regular_flow
    goto :eof
)

REM Function for checking whether the sandbox already exists or not
:check_container_existence
    echo Checking if container %CONTAINER_NAME% exists...
    docker container inspect %CONTAINER_NAME% >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set CONTAINER_EXISTS=1
        echo Container %CONTAINER_NAME% exists.
    ) else (
        set CONTAINER_EXISTS=0
        echo Container %CONTAINER_NAME% does not exist.
    )
goto :eof

REM Function to check if the sandbox is running
:check_container_running
    echo Checking if container %CONTAINER_NAME% is running...
    docker inspect --format="{{.State.Running}}" %CONTAINER_NAME% | findstr "true" >nul
    if %ERRORLEVEL% equ 0 (
        set CONTAINER_RUNNING=1
        echo Container %CONTAINER_NAME% is running.
    ) else (
        set CONTAINER_RUNNING=0
        echo Container %CONTAINER_NAME% is not running.
    )
goto :eof

REM Function to start the sandbox if it is not running
:start_container
    echo Starting container %CONTAINER_NAME%...
    docker start %CONTAINER_NAME%
    if %ERRORLEVEL% equ 0 (
        echo Container %CONTAINER_NAME% started successfully.
        set CONTAINER_RUNNING=1
    ) else (
        echo Failed to start the container %CONTAINER_NAME%. Please check the Docker logs for more details.
        set CONTAINER_RUNNING=0
    )
goto :eof

REM Function to copy Python files into the sandbox
:copy_python_files
    echo Copying Python files to the existing container...
    for /R .. %%f in (*.py) do (
        set "filepath=%%f"
        set "relative_path=%%~pf"

        echo !relative_path! | findstr /i /c:"\\venv\\" >nul
        if !errorlevel! equ 1 (
            echo Copying file: %%f
            set "docker_path=!relative_path:~2!"  REM remove drive letter
            set "docker_path=!docker_path:\=/!"

            docker exec %CONTAINER_NAME% mkdir -p /app/!docker_path!
            docker cp "%%f" %CONTAINER_NAME%:/app/!docker_path!%%~nxf
        )
    )
goto :eof

REM Regular build and run flow
:regular_flow
    echo Building the sandbox image...
    docker build -t %IMAGE_NAME% -f Dockerfile .. > build_output.txt 2>&1

    echo Checking if build was successful...
    findstr /c:"exporting layers" build_output.txt >nul
    if %ERRORLEVEL% equ 0 (
        echo Build successful. Handling containers...
        call :check_container_existence
        if "%CONTAINER_EXISTS%"=="1" (
            echo Stopping and removing existing container...
            docker stop %CONTAINER_NAME%
            docker rm %CONTAINER_NAME%
        )
        echo Running a new container...
        docker run -it --network host --name %CONTAINER_NAME% %IMAGE_NAME%
    ) else (
        echo Build was not successful. Please check the build output for errors.
    )
    echo Cleaning up...
    del build_output.txt
    echo Done.
goto :eof
