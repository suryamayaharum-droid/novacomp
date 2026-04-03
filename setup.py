from setuptools import setup, find_packages

setup(
    name="novacomp",
    version="0.1.0",
    description="A Python project",
    author="suryamayaharum-droid",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
)