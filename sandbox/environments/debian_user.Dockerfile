# Use an official Debian runtime as a parent image
FROM debian:11

# Set environment variables to non-interactive mode to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get install -y curl wget git && \
    apt-get install -y build-essential && \
    apt-get install -y nano net-tools iproute2 iputils-ping sudo && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Create a user named "tester" with sudo privileges
RUN useradd -m -s /bin/bash tester && \
    echo "tester:password" | chpasswd && \
    usermod -aG sudo tester && \
    echo "tester ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt requirements.txt

# Create a Python virtual environment
RUN python3 -m venv venv

# Install any needed packages specified in requirements.txt
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY ./ ./

# Make the buddy_cli.py script executable
RUN chmod +x src/buddy_cli.py

# Install an alias to point "buddy" command to the buddy_cli.py script. Need to activate the venv first
RUN echo "alias buddy='source /app/venv/bin/activate && python /app/src/buddy_cli.py'" >> ~/.bashrc

# Switch to the "tester" user
USER tester

# Set the default command to bash
CMD ["/bin/bash"]
