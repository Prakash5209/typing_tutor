from setuptools import setup, find_packages

setup(
    name='typing_tutor',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],  # You can list dependencies here if needed
    entry_points={
        'console_scripts': [
            'typing-tutor=main:main',  # Assuming your main.py has a main() function
        ],
    },
)
