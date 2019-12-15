from pathlib import Path
from setuptools import setup, find_packages

config_dir = ".doghouse"
Path(Path.home() / config_dir).mkdir(parents=True, exist_ok=True)

VERSION = "0.1"

setup(
    name="doghouse",
    version=VERSION,
    description="Datadog config as code",
    author="Thomas Basche",
    author_email="tcbasche@gmail.com",
    packages=find_packages(),
    install_requires=["pyYAML", "datadog", "click", "datadiff"],
    entry_points={"console_scripts": ["doghouse=doghouse.entrypoint:main"]},
)
