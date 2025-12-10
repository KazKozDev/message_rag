"""Setup script for Message RAG System."""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="message-rag",
    version="0.1.0",
    description="RAG system that processes messages and answers questions with source attribution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Message RAG Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "message-rag=src.cli:main",
        ],
    },
)
