import sys
from setuptools import setup


if sys.version_info['0'] < 3:
    # populate `__version__`
    execfile('hooked/version.py')
else:
    exec(open("hooked/version.py").read())


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
        'Django>=1.6',
    ],
    keywords=[
        'gapi',
        'g adventures',
        'g api',
        'gapipy'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-django',
    ],
)
