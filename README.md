# nest-server

**NEST Server**

![nest-logo](http://www.nest-simulator.org/wp-content/uploads/2015/03/nest_logo.png)

A flask server with REST API for [NEST simulator](http://www.nest-simulator.org/).


## Download
```
git clone https://github.com/babsey/nest-server.git
cd nest-server
```


## Usage

### Using host system

Compile and install NEST 2.14 or higher (See [instructions](http://www.nest-simulator.org/installation/)).

Install python flask (<= 0.12.4)
```
sudo apt install python3-flask
```

Install flask cors.
```
sudo pip3 install flask-cors
```

Start nest server.
```
python3 app/main.py --hist 0.0.0.0
```

### Using Docker

Build a docker image
```
docker build -t nest-server .
```

Start a docker container
```
docker run -d -p 5000:5000 -t nest-server
```
It listens on port 5000.

### Using Singularity

Install singularity 2.6 from source code (See [instructions](https://www.sylabs.io/guides/2.6/user-guide/installation.html))

Build a singularity image of nest server (with sudo)
```
sudo singularity build nest-server.simg Singularity/nest-server.def
```

The image contains NEST 3, python flask (0.12.4) and nest server.
Run singularity container from nest-server image (without sudo)
```
singularity run nest-server.simg
```
It listens on port 5000.


## Check

Check if nest server is running.
```
curl localhost:5000
```

### License [MIT](LICENSE)
