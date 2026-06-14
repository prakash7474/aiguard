from setuptools import setup, find_packages

setup(
    name="aiguard",
    version="0.2.0",
    description="AI Guard CLI - Antivirus for Local AI Coding Agents (Ollama)",
    packages=find_packages(),
    py_modules=["aiguard"],
    entry_points={
        "console_scripts": [
            "aiguard=aiguard:app",
        ],
    },
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.7.0",
        "watchdog>=4.0.0",
        "ollama>=0.4.0",
    ],
)
