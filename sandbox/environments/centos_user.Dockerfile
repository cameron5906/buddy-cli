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

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

# Make the buddy_cli.py script executable
RUN chmod +x buddy_cli.py

# Move the buddy_cli.py script to /usr/local/bin and rename it to buddy
RUN mv buddy_cli.py /usr/local/bin/buddy

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Switch to the "tester" user
USER tester

# Set the default command to bash
CMD ["/bin/bash"]
