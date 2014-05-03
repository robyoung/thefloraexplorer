from setuptools import setup, find_packages
import sys

setup(
    name='thefloraexplorer',
    version='0.0.1',
    url='https://github.com/robyoung/thefloraexplorer',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests>=1.2',
        'futures>=2.1',
        'docopt>=0.6',
        'praw>=2.1',
    ],
    entry_points={
        "console_scripts": [
            "flora-scrape = flora.commands.scrape:main",
            "flora-reddit = flora.commands.reddit:main",
        ],
    },
    tests_require=['nose'],
    test_suite='nose.collector',
)


