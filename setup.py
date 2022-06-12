from setuptools import setup, find_packages

setup(
    name='demographic-lookup',
    version='0.0.1',
    author='John Merrill',
    author_email='john@fairplay.ai',
    description='Basic name handlers for BISG',
    packages=find_packages(),    
    install_requires=['numpy>=1.22.3', 'pandas>=1.4.2']
)