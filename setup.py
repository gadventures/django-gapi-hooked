import sys

from setuptools import setup

_version_file = 'hooked/version.py'

with open(_version_file) as vf:
    exec(vf.read())


# Include pytest-runner as a setup-requirement only if it looks like we're
# doing something test-related.
#
# This way we can avoid having to install it when, for example, somebody just
# wants to build/install django-gapi-hooked as a dependency.
#
# See: https://pypi.org/project/pytest-runner/#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
maybe_pytest_runner = ['pytest-runner'] if needs_pytest else []


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
    setup_requires=maybe_pytest_runner,
    tests_require=[
        'pytest',
        'pytest-django',
    ],
)
