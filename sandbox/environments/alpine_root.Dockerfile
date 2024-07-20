# Use an official Alpine runtime as a parent image
FROM alpine:3.14

# Install Python and other dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip python3-dev && \
    apk add --no-cache curl wget git && \
    apk add --no-cache build-base && \
    apk add --no-cache nano net-tools iproute2 iputils sudo

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

# Set the default command to bash
CMD ["/bin/sh"]
