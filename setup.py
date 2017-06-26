from setuptools import setup

# populate `__version__`
execfile('hooked/version.py')

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
