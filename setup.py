from setuptools import setup, find_packages

setup(
    name="porkbun-cli",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "porkbun=porkbun.cli:main",
        ],
    },
)
