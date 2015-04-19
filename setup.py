from distutils.core import setup
setup(name="ghhooks",
        author="Drew DeVault",
        author_email="sir@cmpwn.com",
        url="https://github.com/SirCmpwn/hooks",
        description="Executes commands based on Github hooks",
        license="MIT",
        version="1.1",
        scripts=["ghhooks"],
        py_modules=["hooks"],
        install_requires=["Flask"])
