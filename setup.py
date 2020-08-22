from setuptools import setup, find_packages

setup(
    name="csgo",
    version="0.1",
    packages=find_packages(),
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        "pandas>=0.25.3",
        "numpy>=1.18.1",
        "scipy>=1.4.1",
        "matplotlib>=3.1.2",
        "textdistance>=4.2.0",
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": [
            "*.go",
            "data/map/*.png",
            "data/nav/*.nav",
            "data/nav/*.xz",
            "*.mod",
            "*.sum",
        ]
    },
)
