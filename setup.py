from setuptools import setup, find_packages

setup(
    name='autoload',
    version='0.0.1',
    description='Simple HTTPerf loadtest runner with pretty output.',
    long_description = open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/autoload',
    packages = find_packages(),
    install_requires = [
        'pgmagick < 0.4.0',
        'gruffy',
        'reportlab',
    ],
    scripts=['autoload/bin/autoload'],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
