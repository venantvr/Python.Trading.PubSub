"""Setup configuration for Python Trading PubSub library."""

import os

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Python.Trading.PubSub",
    version="0.1.0",
    author="venantvr",
    author_email="venantvr@gmail.com",
    description="A professional Python library for building publish-subscribe messaging systems "
    "tailored for trading applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/venantvr/Python.Trading.PubSub",
    project_urls={
        "Bug Tracker": "https://github.com/venantvr/Python.Trading.PubSub/issues",
        "Documentation": "https://github.com/venantvr/Python.Trading.PubSub",
        "Source Code": "https://github.com/venantvr/Python.Trading.PubSub",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-asyncio>=0.21.0",
            "requests-mock>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line scripts here if needed
            # 'pubsub-client=core.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="pubsub, messaging, trading, socketio, realtime, async, websocket",
)
