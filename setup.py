"""Setup script for Rejoice Slim v2."""
from setuptools import setup

# Read the README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="rejoice-slim",
    version="2.0.0",
    description="Local-first voice transcription tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)

