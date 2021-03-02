from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="QAutoLibrary",
    version="0.0.11",
    author="QAutomate",
    author_email="contact@qautomate.fi",
    description="QAutofamily testing framework library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QAutofamily/QAutoLibrary",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'selenium>=3.141.0',
        'robotframework>=3.2.1',
        'requests>=2.25.1',
        'Pillow>=8.0.1',
        'lxml>=4.3.2',
        'simplejson>=3.17.2',
        'pymongo>=3.9.0',
        'pycryptodome>=3.9.8',
        'tika>=1.24'
    ],
    package_data={'QAutoLibrary.config': ['*.xml', '*.ini', '*.txt*'], 'QAutoLibrary': ['*.ico']},
    license='Apache Software License 2.0',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",

    ],
    python_requires='>=3.7',
    entry_points = {'console_scripts': ['WebDriverUpdater = QAutoLibrary.WebDriverUpdater.check_and_update_drivers:main']}
)
