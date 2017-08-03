# python setup.py sdist register upload
from setuptools import setup

setup(
    name='sw-python-email-devino',
    version='0.0.2',
    description='Integration with email API of devinotele.com',
    author='Telminov Sergey',
    url='https://github.com/telminov/sw-python-email-devino',
    packages=[
        'email_devino',
        'email_devino.tests',
    ],
    include_package_data=True,
    license='The MIT License',
    install_requires=[
        'requests'
    ],
    tests_requirements=[
        'mock',
    ]
)