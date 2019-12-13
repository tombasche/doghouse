from pathlib import Path
from setuptools import setup, find_packages

config_dir = ".doghouse"
Path(Path.home() / config_dir).mkdir(parents=True, exist_ok=True)


setup(
    name="doghouse",
    version="0.1",
    description="Datadog config as code",
    author="Thomas Basche",
    author_email="tcbasche@gmail.com",
    packages=find_packages(),
    install_requires=["pyYAML", "datadog", "click", "datadiff"],
    entry_points={"console_scripts": ["doghouse=doghouse.entrypoint:main"]},
)
