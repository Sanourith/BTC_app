from setuptools import setup, find_packages

setup(
    name="btc_functions",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas"
    ],
    entry_points={
        'console_scripts': [
            'run_api=api_creation:app'
        ]
    }
)