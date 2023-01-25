from setuptools import find_packages, setup

setup(
    name="doml-model-checker-synthesis",
    packages=find_packages(include=['src']),
    version='1.0.0',
    description="This library allows to synthetize a new DOML from an existing one, following user-specified requirements",
    author='Andrea Franchini',
    license='MIT',
    install_requires=['z3-solver'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests'
)
