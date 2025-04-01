# syntax=docker/dockerfile:1

# base image
FROM ubuntu:24.04

# set timezone
ENV TZ=Europe/Berlin

# prevent keyboard input requests in apt install
ENV DEBIAN_FRONTEND=noninteractive

# install packages and cleanup afterwards
RUN apt-get update && apt-get dist-upgrade -y && \
    apt-get install -y \
    calibre \
    ghostscript \
    git \
    imagemagick \
    latexmk \
    pandoc \
    python3 \
    python3-lxml \
    texlive-extra-utils \
    texlive-lang-german \
    texlive-lang-greek \
    texlive-xetex && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    useradd -m -s /bin/bash app

# switch to non-root user
USER app

# set working directory
WORKDIR /app

# mount host directory as volume
VOLUME /app

# default command: build 1-vol pdf and all ebook formats
# CMD latexmk hpmor ; ./scripts/make_ebooks.sh

# 1. preparation
# 1.1 build/update image from Dockerfile
#  docker build -t hpmor .

# 1.2 create container that mounts current working dir to /app
#  docker run --name hpmor-de -it --mount type=bind,src="$(pwd)",dst=/app hpmor bash
#  exit

# note: in Windows you need to replace "$(pwd)" by "%cd%" for the following commands

# 2. use container
#  docker start -ai hpmor-de
#  latexmk hpmor ; ./scripts/make_ebooks.sh
#  exit

# 3. optionally: cleanup/delete hpmor from docker
# delete container
#  docker rm hpmor-de
# delete image
#  docker rmi hpmor
# delete all docker containers and cache
#  docker system prune -f
