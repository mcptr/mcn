import os
from setuptools import setup

setup(
    name="mcn-scraper",
    version="0.0.1",

    author="mcptr",
    author_email="",
    packages=["mcn"],
    include_package_data=True,
    url="",

    #
    # license="LICENSE.txt",
    description="Mechanoia: scraper",
    # long_description=open("README.txt").read(),
    install_requires=[
        "requests",
        "pymongo",
        "bs4",
        "lxml",
    ],
)

