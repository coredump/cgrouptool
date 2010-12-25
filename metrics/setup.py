#!/usr/bin/python

from setuptools import setup, find_packages
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

try:
    from debian_bundle.changelog import Changelog
    from debian_bundle.deb822 import Deb822
    from email.utils import parseaddr

    version = Changelog(open(path.join(path.dirname(__file__), 'debian/changelog')).read()).\
              get_version().full_version

    maintainer_full = Deb822(open(path.join(path.dirname(__file__), 'debian/control')))['Maintainer']
    maintainer, maintainer_email = parseaddr(maintainer_full)
except:
    version = '0.0.0'
    maintainer = ''
    maintainer_email = ''

setup(
    name="debathena.metrics",
    version=version,
    description="Metrics gatherer for Debathena cluster machines.",
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    license="MIT",
    requires=['Pyrex'],
    packages=find_packages(),
    ext_modules=[
        Extension("debathena.metrics.connector",
                  ["debathena/metrics/connector.pyx"])
        ],
    cmdclass= {"build_ext": build_ext}
)
