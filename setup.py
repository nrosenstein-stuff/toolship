# This file was auto-generated by Shut. DO NOT EDIT
# For more information about Shut, check out https://pypi.org/project/shut/

from __future__ import print_function
import io
import os
import setuptools
import sys

readme_file = 'README.md'
if os.path.isfile(readme_file):
  with io.open(readme_file, encoding='utf8') as fp:
    long_description = fp.read()
else:
  print("warning: file \"{}\" does not exist.".format(readme_file), file=sys.stderr)
  long_description = None

requirements = [
  'PySide2 >=5.15.2,<6.0.0',
  'yubikey-manager >=4.0.5,<5.0.0',
  'nr.optional >=0.1.1,<1.0.0',
  'global-hotkeys >=0.0.4,<1.0.0',
  'pynput >=1.7.3,<2.0.0',
]

setuptools.setup(
  name = 'toolship',
  version = '0.0.0',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Package description here.',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = None,
  license = None,
  packages = setuptools.find_packages('src', ['test', 'test.*', 'tests', 'tests.*', 'docs', 'docs.*']),
  package_dir = {'': 'src'},
  include_package_data = True,
  install_requires = requirements,
  extras_require = {},
  tests_require = [],
  python_requires = '>=3.5.0,<4.0.0',
  data_files = [],
  entry_points = {},
  cmdclass = {},
  keywords = [],
  classifiers = [],
  zip_safe = True,
)
