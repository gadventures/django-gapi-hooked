from setuptools import setup

current_version = '0.3.0'

setup(
    name='django-gapi-hooked',
    version=current_version,
    author='G Adventures',
    author_email='software@gadventures.com',
    description='A tiny library to add a G Adventures API Web Hook receiver view to your code base.',
    download_url='https://github.com/gadventures/django-gapi-hooked/tarball/%s' % current_version,
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
