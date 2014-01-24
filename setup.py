from setuptools import setup, find_packages
 
setup (
    name = 'sk-import',
    version = '0.2',
    description="Bypass Songkick's import hard limit by hitting the site directly",
    long_description="Bypass Songkick's import hard limit by hitting the site directly",
    author='rattboi',
    author_email='rattboi@gmail.com', # Removed to limit spam harvesting.
    url='http://github.com/rattboi/sk-import/',
    package_data = {'': ['*.xml']},
    packages = find_packages(exclude="tests"),
    install_requires=[
        'beautifulsoup4',
        'requests',
    ],
    entry_points={
        'console_scripts': [
                'sk-import = sk_import.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
    ],
    zip_safe = False 
)
