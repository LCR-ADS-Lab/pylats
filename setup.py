import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylats",
    version="0.37",
    author="Kristopher Kyle",
    author_email="kristopherkyle1@gmail.com",
    description="Text preprocessing for downstream linguistic analyses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LCR-ADS-Lab/pylats",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)