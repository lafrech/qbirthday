"""Setup file"""
from setuptools import setup, find_packages


with open("README.rst") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(
    name="qbirthday",
    version="0.7.0b3",
    description="QBirthday birthday reminder",
    long_description=LONG_DESCRIPTION,
    author="Jérôme Lafréchoux",
    author_email="jerome@jolimont.fr",
    license="GPLv2",
    keywords="QBirthday birthday reminder",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"gui_scripts": ["qbirthday = qbirthday:main"]},
    package_data={
        "qbirthday": ["ui/*.ui", "pics/*.png", "i18n/*.qm"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Environment :: X11 Applications :: Qt",
        (
            "License :: OSI Approved :: "
            "GNU General Public License v2 or later (GPLv2+)"
        ),
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.7",
    ],
    url="https://github.com/lafrech/qbirthday",
    project_urls={
        "Bug Tracker": "https://github.com/lafrech/qbirthday/issues",
        "Source Code": "https://github.com/lafrech/qbirthday",
    },
)
