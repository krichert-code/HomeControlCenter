#!/bin/bash

killall ffmpeg
(ffmpeg -re -i "rtsp://192.168.1.126:554/live0" -c copy -f rtsp rtsp://127.0.0.1:8554/mystream) &
sleep 120
killall ffmpeg