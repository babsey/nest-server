To install sphinx for documentation
```
pip3 install sphinx
```

To initializee sphinx docs:
```
cd docs
sphinx-quickstart
```


To build rst docs of NEST server module:
```
sphinx-apidoc -o docs/api nest_server
```


To build html docs with sphinx locally:
```
cd docs
make html
```
