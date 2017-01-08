# coding=utf-8
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='Meet N Eat',
    version='1.0.0',
    license='MIT',
    author='Carlos Azuaje',
    author_email='carlosjazzc1@gmail.com',
    description='is a social application for meeting people based on their food interests.',
    packages=find_packages('app'),
    package_dir={'': 'app'},
    platforms='any',
    install_requires=[
        'flask>=0.10',
        'sqlalchemy',
        'Flask-HTTPauth',
        'oauth',
        'redis',
        'simplejson',
        'rauth',
        'flask-assets',
        'itsdangerous',
        'foursquare',
        'passlib',
        'colorama'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Food :: WWW/HTTP :: API',
    ],
)
