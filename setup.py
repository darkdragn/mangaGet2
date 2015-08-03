#!/usr/bin/env python


from setuptools import setup, Extension

VERSION = (0, 1)
VERSION_STR = ".".join([str(x) for x in VERSION])

setup(
    name='mangaGet2',
    version=VERSION_STR,
    description="Online manga site ripping tool.",
    author='Christopher Jackson',
    author_email='darkdragn.cj@gmail.com',
    url='https://github.com/darkdragn/mangaGet2',
    packages=['mangaGet2', 'mangaGet2.sites'],
    scripts=['mg2Cli.py'],
    install_requires=[ 'beautifulsoup4' ],
    #setup_requires=["nose>=1.0"],
    #test_suite = "nose.collector",
    keywords = ['manga', 'online'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
