import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
    setuptools.setup(
        name="CDK",
        version="0.0.1",
        description="My CDK Diploma Project",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=setuptools.find_packages(),
        python_requires='>=3.7'
    )
