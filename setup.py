from setuptools import setup, find_packages

setup(
    name="codebase-navigator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "chromadb",
        "ollama",
        "gitpython",
    ],
    entry_points={
        'console_scripts': [
            'nav=codebase_nav.cli:main',
        ],
    },
    python_requires='>=3.8',
)