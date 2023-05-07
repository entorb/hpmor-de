# syntax=docker/dockerfile:1

# base image
FROM ubuntu:latest

# set timezone
ENV TZ=Europe/Berlin

# prevent keyboard input requests in apt install
ARG DEBIAN_FRONTEND=noninteractive

# install core packages
RUN apt-get update
RUN apt-get install -y python3

# for pdf, copied from scripts/install_requirements_pdf.sh
RUN apt-get install -y texlive-xetex texlive-lang-german latexmk
# for ebook, copied from scripts/install_requirements_ebook.sh
RUN apt-get install -y texlive-extra-utils pandoc calibre imagemagick ghostscript
