import os
from setuptools import setup, find_packages

__version__ = '0.1'

HERE = os.path.dirname(__file__)


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='rubberjack-cli',
    version=__version__,
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    zip_safe=True,

    # metadata for upload to PyPI
    author='LaterPay GmbH',
    url='https://github.com/laterpay/rubberjack-cli',
    description='RubberJack manages (AWS) Elastic Beanstalks',
    long_description=readme(),
    license='MIT',
    keywords='aws',

    install_requires=[
        'boto',
        'click',
    ],

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],

    entry_points={
        'console_scripts': [
            'rubberjack=rubberjackcli.click:rubberjack',
        ],
    },

)
