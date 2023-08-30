import sys

from setuptools import setup

_version_file = 'hooked/version.py'

with open(_version_file) as vf:
    exec(vf.read())

setup(
    name='django-gapi-hooked',
    version=__version__,
    author='G Adventures',
    author_email='software@gadventures.com',
    description='A tiny library to add a G Adventures API Web Hook receiver view to your code base.',
    download_url='https://github.com/gadventures/django-gapi-hooked/tarball/%s' % __version__,
    url='https://github.com/gadventures/django-gapi-hooked',
    packages=[
        'hooked',
    ],
    install_requires=[
        'django',
    ],
    keywords=[
        'gapi',
        'g adventures',
        'g api',
        'gapipy'
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-django',
        ],
    },
)
