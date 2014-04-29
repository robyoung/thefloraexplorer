from setuptools import setup, find_packages
import sys

setup(
    name='whatsthisplant',
    version='0.0.1',
    url='none',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests>=1.2',
        'futures>=2.1',
        'docopt>=0.6',
    ],
    entry_points={
        "console_scripts": [
            "wtp-scrape = whatsthisplant.commands.scrape:main",
        ],
    },
)


