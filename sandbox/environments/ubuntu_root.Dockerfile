# Use an official Ubuntu runtime as a parent image
FROM ubuntu:20.04

# Set environment variables to non-interactive mode to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get install -y curl wget git && \
    apt-get install -y build-essential && \
    apt-get install -y nano net-tools iproute2 iputils-ping ifupdown systemctl sudo && \
    apt-get install -y software-properties-common

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

# Make the buddy_cli.py script executable
RUN chmod +x buddy_cli.py

# Move the buddy_cli.py script to /usr/local/bin and rename it to buddy
RUN mv buddy_cli.py /usr/local/bin/buddy

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Set the default command to buddy
CMD ["/bin/bash"]
