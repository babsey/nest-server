import setuptools
import sys

assert sys.version_info >= (3,), "Python 3 is required to run NEST Server"

with open("README.md", "r") as fh:
    long_description = fh.read()

from nest_server.environments import VERSION

setuptools.setup(
    name="nest-server",
    version=VERSION,
    description="A server for NEST Simulator with REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/babsey/nest-server",
    license="MIT License",
    packages=setuptools.find_packages(),
    scripts=["bin/nest-server"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    install_requires=["numpy", "flask==0.12.4", "flask-cors", "uwsgi", "nestml"],
)
