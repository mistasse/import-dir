from setuptools import setup, find_packages


setup(
    name="import-dir",
    author="Maxime Istasse",
    author_email="istassem@gmail.com",
    url="https://github.com/mistasse/import-dir",
    license='LGPL',
    version="0.1.0",
    python_requires='>=3.6',
    description="A library for importing non-package directories",
    long_description_content_type="text/markdown",
    packages=find_packages(include=("import_dir",)),
    install_requires=["redbaron"],
)
