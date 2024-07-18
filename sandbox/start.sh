#!/bin/bash
docker build -t buddy_cli -f Dockerfile ..
docker run -it --rm --network host buddy_cli