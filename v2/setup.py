"""
Setup script for Substrate Agent

Install:
    pip install .

Or with extras:
    pip install .[gpu]  # For GPU support
    pip install .[dev]  # For development
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="substrate-agent",
    version="2.4.0",
    description="Background intelligence agent for hybrid memory systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pakorn Musikaper",
    author_email="pakorn@example.com",
    url="https://github.com/pakornmusikaper-blip/Hybrid-memory-system",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "accelerate>=0.25.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "gpu": [
            "bitsandbytes>=0.41.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "substrate=substrate.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
)
