FROM ubuntu:18.04

LABEL maintainer="Sebastian Spreizer <spreizer@web.de>"

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    cython3 \
    libgsl0-dev \
    libltdl7-dev \
    libncurses5-dev \
    libreadline6-dev \
    python3-all-dev \
    python3-pip \
    python3-numpy \
    git

RUN pip3 install flask==0.12.4 flask-cors

WORKDIR /tmp
RUN git clone https://github.com/compneuronmbu/nest-simulator.git && \
    cd /tmp/nest-simulator && \
    git fetch && \
    git checkout nest-3 && \
    mkdir /tmp/nest-build

WORKDIR /tmp/nest-build
RUN cmake -DCMAKE_INSTALL_PREFIX:PATH=/opt/nest/ -Dwith-python=3 /tmp/nest-simulator && \
    make && \
    make install && \
    rm -rf /tmp/*

COPY ./app /nest-server
WORKDIR /nest-server

EXPOSE 5000
RUN chmod 755 entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
