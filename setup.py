from setuptools import setup, find_packages

setup(
    name="pymonkey",
    version="0.0.1",
    packages=find_packages(where='src'),
    package_dir={'monkey': 'src/monkey'},
    entry_points={
        'console_scripts': [
            'pymonkey = monkey.main:main'
        ]
    }
)
