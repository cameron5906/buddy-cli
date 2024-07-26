# Use an official Alpine runtime as a parent image
FROM alpine:3.14

# Install Python and other dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip python3-dev && \
    apk add --no-cache curl wget git && \
    apk add --no-cache build-base && \
    apk add --no-cache nano net-tools iproute2 iputils sudo

# Create a user named "tester" with sudo privileges
RUN adduser -D -s /bin/sh tester && \
    echo "tester:password" | chpasswd && \
    adduser tester wheel && \
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

# Set the default command to sh
CMD ["/bin/sh"]
