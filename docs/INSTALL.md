# NEST Server

## Installation instructions

### Download
```
git clone https://github.com/babsey/nest-server.git
cd nest-server
```


### Install on host system

###### Step 1
Compile and install NEST 2.14 or higher (See [instructions](http://www.nest-simulator.org/installation/)).

###### Step 2
Install uwsgi flask and flask cors via pip3.
```
sudo pip3 install uwsgi flask flask-cors
```

###### Step 3.a
Start nest server uwsgi.
```
uwsgi uwsgi/uwsgi.ini
```

###### Step 3.b
Start nest server with flask.
```
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export HOST=0.0.0.0
export FLASK_APP=app/main.py
flask run
```

###### Step 3.c
Start nest server with flask (lazy start).
```
python3 app/main.py (--host 0.0.0.0)
```

###### Step 4
Check if nest server is running on port 5000.
```
curl localhost:5000
```


### Docker

###### Step 1
Build a docker image
```
docker build -f docker/dockerfiles/nest-server.Dockerfile -t nest-server:X.Y .
```
###### Step 1 (alternative)
 Load image from a file (nest-server-vX.Y.dimg)
```
sudo docker load --input nest-server-vX.Y.dimg
```

###### Step 2
Start docker container with daemon
```
docker run -d -p 5000:5000 -t nest-server:X.Y
```
NEST Server is running on port 5000.

###### Step 3
Check if docker container is running.
```
sudo docker ps
```

###### Step 4
Stop docker container.
```
sudo docker stop <CONTAINER ID>
```


### Singularity

###### Step 1
Install singularity 2.6 from source code (See [instructions](https://www.sylabs.io/guides/2.6/user-guide/installation.html))

###### Step 2
Build a singularity image of nest server (with sudo)
```
sudo singularity build nest-server-vX.Y.simg Singularity/nest-server.def
```
The image contains NEST 3, python flask (0.12.4) and nest server.

###### Step 3
Run singularity container from nest-server image (without sudo).
```
singularity run nest-server-vX.Y.simg
```
or

```
singularity exec nest-server-vX.Y.simg python3 /opt/nest-server/main.py
```
NEST Server is running on port 5000.


### License [MIT](LICENSE)
