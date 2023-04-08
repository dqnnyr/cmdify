from distutils.core import setup

setup(
    name='TI4 NLP',
    version='0.1dev',
    packages=['ti4nlp', ],
    license='MIT License',
    long_description=open('README.md').read(),
    install_requires=[
        "textdistance >= 4.5.0"
    ]
)
