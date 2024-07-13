from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements=f.read().splitlines()

setup(
    name='dependency_eval',
    version='1.0.0',
    author='Niklas Loeser',
    description='Evaluate the dependency eval dataset',
    packages=["dependency_eval"],    
    install_requires=requirements,
)