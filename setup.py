import setuptools
import sys

from nest_server import __version__

assert sys.version_info >= (3,), "Python 3 is required to run NEST Server"

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nest-server",
    version=__version__,
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
    install_requires=["flask", "flask-cors", "nestml", "numpy", "RestrictedPython", "uwsgi"],
)
