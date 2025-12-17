"""Setup configuration for aicli."""

from setuptools import setup, find_packages

setup(
    name="aicli",
    version="0.1.0",
    description="AI CLI - Code modification using Ollama models",
    author="Your Name",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
    ],
    entry_points={
        "console_scripts": [
            "aicli=aicli.main:cli",
        ],
    },
    python_requires=">=3.8",
)
