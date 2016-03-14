from setuptools import setup

setup(name='django-hooked',
    version='0.2.0',
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-gapi-hooked',
    packages=[
        'hooked',
    ],
    test_suite='hooked.runtests.main',
    install_requires=[
        'Django>=1.6',
    ]
)
