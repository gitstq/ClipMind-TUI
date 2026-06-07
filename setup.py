#!/usr/bin/env python3
"""Setup script for ClipMind-TUI."""

from setuptools import setup, find_packages
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="clipmind-tui",
    version="1.0.0",
    description="🧠 Lightweight Terminal Intelligent Clipboard Manager",
    long_description=README,
    long_description_content_type="text/markdown",
    author="gitstq",
    author_email="",
    url="https://github.com/gitstq/ClipMind-TUI",
    py_modules=["clipmind"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "clipmind=clipmind:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Office/Business",
    ],
    keywords="clipboard manager terminal tui productivity cross-platform",
    license="MIT",
)
