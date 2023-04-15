from distutils.core import setup

setup(
    name='cmdify',
    version='0.1',
    packages=['cmdify', ],
    license='MIT License',
    long_description=open('README.md').read(),
    install_requires=[
        'bidict~=0.22.1',
        'textdistance~=4.5.0'
    ]
)
