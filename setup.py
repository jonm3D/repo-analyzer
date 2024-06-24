from setuptools import setup, find_packages

setup(
    name='repo_analyzer',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'repo_analyzer=repo_analyzer.analyzer:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['repo_analyzer_config.txt'],
    },
)
