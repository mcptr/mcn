import os
from setuptools import setup

setup(
    name="mcn-manager",
    version="0.0.1",

    author="",
    author_email="",
    packages=["mcn"],
    include_package_data=True,
    url="https://mechanoia.com",

    #
    # license="LICENSE.txt",
    description="Mechanoia: manager",
    # long_description=open("README.txt").read(),
    install_requires=[
        "requests",
    ],
)

