import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="outback_mate_rs232-ryanf55", # Replace with your own username
    version="0.0.1",
    author="Ryan Friedman",
    description="Package for reading from Outback Mate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ryanf55/outback_mate_rs232",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6.9',

)