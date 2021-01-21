from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="QAutoLibrary",
    version="0.0.4a",
    author="QAutomate",
    author_email="contact@qautomate.fi",
    description="QAutofamily testing framework library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QAutofamily/QAutoLibrary",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'selenium',
        'robotframework>=3.2.1',
        'requests',
        'Pillow',
        'lxml',
        'simplejson',
        'pymongo',
        'pycryptodome',
        'tika'
    ],
    package_data={'QAutoLibrary.config': ['*.xml', '*.ini', '*.txt*']},
    license='Apache License 2.0',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License", #"License :: OSI Approved :: Apache License 2.0" ei toimi
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points = {'console_scripts': ['WebDriverUpdater = QAutoLibrary.WebDriverUpdater.check_and_update_drivers:main']}
)
