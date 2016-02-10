#run setup.py sdist or python setup.py bdist_wininst
from distutils.core import setup
setup(name='PyUACalc',
      version='0.1',
      description='Python Wrapper around UACalc .ua files.',
      author='Jamie Wannenburg',
      author_email='jamiewannenburg@yahoo.com',
      url='https://www.github.com/jamiewannenburg/',
      py_modules=['pyuacalc'],
      )