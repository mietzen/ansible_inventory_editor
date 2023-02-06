import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='ansible-inventory-editor',
    version='0.1.0',
    license='MIT',
    description="This package adds and deletes hosts from the ansible hosts file.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Nils Stein",
    author_email='social.nstein@mailbox.org',
    packages=find_packages(),
    url='https://github.com/n-stone/ansible_inventory_editor',
    keywords='ansible inventory editor',
    install_requires=[
        'PyYAML',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
    'console_scripts': ['ansible-inventory-editor=ansible_inventory_editor.cli:main']
    },
)
