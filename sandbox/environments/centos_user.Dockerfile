# Use an official CentOS runtime as a parent image
FROM centos:8

# Set environment variables to non-interactive mode to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other dependencies
RUN yum -y update && \
    yum -y install python3 python3-pip python3-virtualenv && \
    yum -y install curl wget git && \
    yum -y groupinstall "Development Tools" && \
    yum -y install nano net-tools iproute iputils sudo && \
    yum clean all

# Create a user named "tester" with sudo privileges
RUN useradd -m -s /bin/bash tester && \
    echo "tester:password" | chpasswd && \
    usermod -aG wheel tester && \
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

# Install an alias to point "buddy" command to the buddy_cli.py script using the venv interpreter
RUN echo "alias buddy='/app/venv/bin/python /app/src/buddy_cli.py'" >> ~/.bashrc

# Switch to the "tester" user
USER tester

# Set the default command to bash
CMD ["/bin/bash"]
