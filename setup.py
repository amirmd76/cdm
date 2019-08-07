from setuptools import setup, find_packages

readme = "Charzeh Download Manager"

setup(
    name='cdm',
    version='0.0.5',
    description='Charzeh Download Manager',
    long_description=readme,
    author='AmirMohammad Dehghan',
    author_email='dehghan@mit.edu',
    url='https://github.com/amirmd76/cdm.git',
    entry_points={
        'console_scripts': ['cdm = cdm.cdm:main']
    },
    license='MIT',
    packages=find_packages(),
    install_requires=[]
)
