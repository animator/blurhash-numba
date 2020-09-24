#!/usr/bin/env python
from setuptools import setup

### To run the tests:
# $ pytest

### To install on a machine:
# $ sudo python setup.py install

### To install in a home directory (~/lib):
# $ python setup.py install --home=~

exec(open('blurhash_numba/version.py').read())

with open('README.md', 'r') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

INSTALL_PILLOW = ["Pillow>=7.2.0",]
TESTS_REQUIRE = ['pytest',] + INSTALL_PILLOW


setup(name="blurhash-numba",
      version=__version__,
      description="Numba aware BlurHash encoder and decoder implementation for Python",
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      author="Ankit Mahato",
      author_email="ankit@realworldpython.guide",
      keywords='blurhash python numba placeholder image',
      packages=["blurhash_numba"],
      url="https://realworldpython.guide/blurhash-numba/",
      project_urls={
            "Source Code": "https://github.com/animator/blurhash-numba",
            "Bug Tracker": "https://github.com/animator/blurhash-numba/issues",
            "Documentation": "https://realworldpython.guide/blurhash-numba/",
      },
      test_suite="test",
      install_requires=["numba>=0.51.0"],
      tests_require=TESTS_REQUIRE,
      extras_require={
            'testing': TESTS_REQUIRE,
            'pillow': INSTALL_PILLOW,
      },
      python_requires='>=3.6',
      classifiers=[  
            'Development Status :: 5 - Production/Stable', 
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Natural Language :: English',
      ],      
      )
