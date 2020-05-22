from setuptools import setup

setup(name='gasopt-lib',
    version='0.1',
    description='Optimization of gas consumption',
    url='',
    author='Andrey Sapronov',
    author_email='asapronov@hse.ru',
    license='LGPL',
    packages=['gasopt-lib'],
    install_requires=[
        'pandas', 'numpy', 'scipy', 'matplotlib', 'nose'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    scripts=[],
    zip_safe=False)
