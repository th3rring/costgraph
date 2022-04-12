#!/bin/bash
tmux new-session -d -s jupyter_lab 'cd /home/therring/Workspace/ && jupyter lab --no-browser --port=8888'
