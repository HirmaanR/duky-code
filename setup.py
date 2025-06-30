#!/usr/bin/env python3
"""
Setup script for Ducky AI Assistant
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ducky-ai",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A terminal-based AI coding assistant with duck personality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ducky-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "ducky=ducky.main:main",
        ],
    },
    keywords="ai assistant coding terminal cli duck",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ducky-ai/issues",
        "Source": "https://github.com/yourusername/ducky-ai",
    },
)
