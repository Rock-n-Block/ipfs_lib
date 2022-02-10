from setuptools import find_packages, setup

setup(
    name="ipfsclient",
    version="0.0.1",
    description="ipfsclient",
    author="akrpv",
    author_email="al.kurapov@gmail.com",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    license="LICENSE.txt",
)
