# Dockerfile for opencv-dlib project
FROM ubuntu:18.04
RUN mkdir -p /mnt/c/shasuri/opencv
COPY . /mnt/c/shasuri/opencv
RUN apt-get -y -qq update && \
	apt-get -y -qq install vim python3 python3-pip cmake && \
	apt-get -y -qq install libsm6 libxext6 libxrender-dev && \
	pip3 install opencv-python && \
	pip3 install numpy && \
	pip3 install dlib && \
	rm -rf /var/lib/apt/lists/*
