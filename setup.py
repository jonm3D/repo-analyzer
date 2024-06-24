from setuptools import setup, find_packages

setup(
    name="repo-analyzer",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'repo-analyzer=repo_analyzer.cli:main',
        ],
    },
)

