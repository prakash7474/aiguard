from setuptools import setup, find_packages

setup(
    name="aiguard",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["aiguard"],
    entry_points={
        "console_scripts": [
            "aiguard=aiguard:app",
        ],
    },
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
)
