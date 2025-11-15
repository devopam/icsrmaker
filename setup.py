"""
Setup configuration for E2B R3 ICSR XML Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='icsrmaker',
    version='1.0.0',
    description='Generate E2B R3 ICSR XML in HL7 format from JSON input data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ICSR Maker Team',
    author_email='contact@example.com',
    url='https://github.com/yourusername/icsrmaker',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'icsrmaker': ['map_metadata.csv'],
    },
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'lxml>=4.9.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    entry_points={
        'console_scripts': [
            'icsrmaker=icsrmaker.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='e2b icsr hl7 pharmacovigilance adverse-events xml medical healthcare',
)
