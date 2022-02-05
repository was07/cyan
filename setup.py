import os
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, "src")

import ast

with open(os.path.join(src, "__init__.py")) as f:
    mod = ast.parse(f.read())
    version = [
        t
        for t in [*filter(lambda n: isinstance(n, ast.Assign), mod.body)]
        if t.targets[0].id == "__version__"
    ][0].value.value

meta = {
    "name": "Cyan",
    "license": "MIT",
    "url": "https://github.com/was07/Cyan",
    "version": version,
    "author": "was07",
    "python_requires": ">=3.8",
    "keywords": [
        "interactive", "interpreter", "language", "shell",
        "packages",
        "hot reload",
        "auto install",
        "aspect oriented",
        "version checking",
        "functional",
    ],
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
    ],
    "fullname": "Cyan",
    "dist_files": ["pytest.ini", "tests/pytest.ini"],
    "description": "a pure-python language",
    "maintainer": "was07",
    "platforms": ["any"],
    "download_url": "https://github.com/was07/Cyan/" "archive/refs/heads/main.zip",
}


requires = (
    "wheel(>= 0.36.2)",
)


with open("readme.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_name="cyan",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    requires=requires,
    install_requires=requires,
    setup_requires=requires,
    zip_safe=True,
    **meta
)
