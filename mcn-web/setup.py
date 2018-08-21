import os
from setuptools import setup

setup(
    name="mcn-web",
    version="0.0.1",

    author="",
    author_email="",
    packages=["mcn"],
    include_package_data=True,
    url="",

    #
    # license="LICENSE.txt",
    description="mcn web",
    # long_description=open("README.txt").read(),
    install_requires=[
        "flask",
        "mcn-core",
    ],
)

