# nest-server
A flask server for nest simulator with REST API

## Using Docker

Build a docker image
```
docker build -t nest-server .
```

Start a docker container
```
docker run -d -p 5000:5000 -t nest-server
```

Check if nest server simulation is running
```
curl localhost:5000
```
