"""Homie setup script."""

from setuptools import setup

setup(
    name='Homie',
    version='0.3.0',
    description='Homie Discovery Controller',
    url='https://github.com/timpur/homie-discovery-python',
    author='Tim Purchas',
    license='MIT',
    packages=['homie', 'homie/models', 'homie/tools'],
    zip_safe=True
)
