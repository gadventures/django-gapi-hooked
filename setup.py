from setuptools import setup

setup(name='django-hooked',
    version='0.1.0',
    author='G Adventures',
    author_email='software@gadventures.com',
    url='https://github.com/gadventures/django-hooked',
    packages=[
        'hooked',
    ],
    test_suite='hooked.runtests.main',
    install_requires=[
        'Django>=1.6',
    ]
)
