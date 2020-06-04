"""Configure package."""
import os
from setuptools import setup, find_packages

# -----------------------------------------------------------------------------
# For information on this file, see:
# https://packaging.python.org/distributing/#setup-args
#
# For examples, look here:
# https://gitlab.pixsystem.net/groups/libraries
# -----------------------------------------------------------------------------


here = os.path.abspath(os.path.dirname(__file__))

# Store version in version['__version__'].
version = {}
with open(os.path.join(here, "lambda_function", "_version.py")) as ver_file:
    exec(ver_file.read(), version)

# This is your package/library name.
packages = [
    package
    for package in find_packages()
    if package.startswith("lambda_function")
]

# Put the pip-installable libraries your library depends on here;
# e.g. 'requests'
install_requires = ["certbot", "certbot-dns-route53"]

dependency_links = []

setup_requires = ["pytest-runner"]

tests_require = ["moto", "pytest", "pytest-cov", "pytest-sugar"]

extras_require = {
    "dev": ["flake8", "autopep8", "cfn-lint", "sphinx"] + tests_require
}

setup(
    name="certbot-runner",
    version=version["__version__"],
    description="Creates a certificate if it doesn't exist or is about to expire and uploads the files to S3 and ACM.",
    packages=packages,
    url="https://github.com/cgartner/letsencrypt-cert-manager",
    author="Chad Gartner",
    author_email="cgartner@x2x.media",
    keywords=["lambda"],
    install_requires=install_requires,
    extras_require=extras_require,
    setup_requires=setup_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
)
