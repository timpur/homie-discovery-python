"""Homie setup script."""

from setuptools import setup

setup(
    name='Homie',
    version='0.3.1',
    description='Homie Discovery Controller',
    url='https://github.com/timpur/homie-discovery-python',
    author='Tim Purchas',
    license='MIT',
    packages=['homie', 'homie/models', 'homie/tools'],
    install_requires=['attr'],
    zip_safe=True
)
