from setuptools import setup, find_packages

# Read the contents of requirements.txt file
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='stock_management',
    version='1.0',
    description='GUI for stock management',
    packages=find_packages(),
    install_requires=requirements,
)