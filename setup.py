from setuptools import setup

setup(
    name='buzzerweb',
    packages=['buzzerweb'],
    include_package_data=True,
    install_requires=[
        'flask',
        'rpyc'
    ],
)
