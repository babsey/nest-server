### STAGE 1: Build NEST ###
FROM ubuntu:18.04 as nest-builder
LABEL maintainer="Sebastian Spreizer <spreizer@web.de>"

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    cython3 \
    libgsl-dev \
    libltdl-dev \
    libncurses5-dev \
    libreadline-dev \
    python3-all-dev \
    python3-numpy \
    wget

# install 'nest simulator'
WORKDIR /tmp
RUN VERSION=2.18.0 && \
    wget -O nest-simulator-$VERSION.tar.gz https://github.com/nest/nest-simulator/archive/v$VERSION.tar.gz && \
    tar -zxf nest-simulator-$VERSION.tar.gz && \
    mkdir /tmp/nest-build && cd /tmp/nest-build && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/opt/nest/ -Dwith-python=3 /tmp/nest-simulator-$VERSION && \
    make -j 4 && make install && \
    rm -rf /tmp/simulator-$VERSION /tmp/nest-build


### STAGE 2: Setup ###
FROM ubuntu:18.04
LABEL maintainer="Sebastian Spreizer <spreizer@web.de>"

RUN apt-get update && apt-get install -y \
    libgsl-dev \
    libltdl-dev \
    python3-numpy \
    python3-pip

RUN pip3 install nest-server --upgrade

COPY --from=nest-builder /opt/nest /opt/nest

# add user 'nest'
RUN adduser --disabled-login --gecos 'NEST' --home /home/nest nest && \
    chown nest:nest /home/nest

# copy entrypoint to nest home folder
COPY ./docker/entrypoint.sh /home/nest
RUN chown nest:nest /home/nest/entrypoint.sh && \
    chmod +x /home/nest/entrypoint.sh && \
    echo '. /opt/nest/bin/nest_vars.sh' >> /home/nest/.bashrc

EXPOSE 5000
WORKDIR /home/nest
USER nest
ENTRYPOINT ["/home/nest/entrypoint.sh"]
