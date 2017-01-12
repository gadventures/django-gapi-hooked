from setuptools import setup

setup(name='django-hooked',
    version='0.2.0',
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-gapi-hooked',
    packages=[
        'hooked',
    ],
    install_requires=[
        'Django>=1.6',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
