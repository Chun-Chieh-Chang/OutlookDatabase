#!/usr/bin/env python3
"""
Setup script for Outlook Database Tool
"""

from setuptools import setup, find_packages

setup(
    name="outlook-database-tool",
    version="1.0.0",
    description="Extract and query emails from local Outlook application",
    author="Outlook Database Tool",
    py_modules=["outlook_db_builder", "query_examples"],
    install_requires=[
        "pywin32>=306",
        "pandas>=1.3.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
