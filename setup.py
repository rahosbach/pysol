from setuptools import setup

setup(
    name='pysol',
    url='https://github.com/jladan/package_demo',
    author='Robert Hosbach',
    author_email='robert.hosbach@gmail.com',
    # Needed to actually package something
    packages=['pysol'],
    # Needed for dependencies
    install_requires=['numpy'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)