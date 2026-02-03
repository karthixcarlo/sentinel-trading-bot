"""
Setup configuration for Project Sentinel
"""

from setuptools import setup, find_packages

setup(
    name="sentinel",
    version="0.1.0",
    description="Autonomous Intraday Trading Agent - Phase 1: Core Risk Management Modules",
    author="Project Sentinel Team",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
