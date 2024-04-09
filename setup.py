from setuptools import find_packages, setup
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tjfu',
    packages=find_packages(include=['tjfu']),
    version='3.1.1',
    description='Python library helps optimize Flask development to be flexible and object-oriented.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='DuyNguyen02',
    url="https://github.com/duynguyen02/tjfu",
    install_requires=[
        "flask",
        "flask_cors",
        "flask_jwt_extended",
        "flask_socketio",
        "flask_limiter"
    ],
    python_requires=">=3.9",
    keywords=[
        "Python",
        "Flask"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ]
)