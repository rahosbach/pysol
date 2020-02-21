from setuptools import setup

setup(
    name="pysoleng",
    url="https://github.com/rahosbach/pysoleng",
    author="Robert Hosbach",
    author_email="robert.hosbach@gmail.com",
    # Needed to actually package something
    packages=["pysoleng"],
    # Needed for dependencies
    install_requires=[],
    # *strongly* suggested for sharing
    version="0.1",
    # The license can be anything you like
    license="MIT",
    description="A package implementing the solar calculations from Duffie and Beckman's Solar Engineering of Thermal Processes (2006)",
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
