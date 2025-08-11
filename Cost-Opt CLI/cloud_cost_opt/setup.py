from setuptools import setup, find_packages

setup(
    name="cloud_cost_opt",
    version="0.1",
    packages=find_packages(),
    install_requires=["click"],
    entry_points={
        'console_scripts': [
            'cost-opt=cloud_cost_opt.cli:cli',
        ],
    },
    include_package_data=True,
    author="Your Name",
    description="Cloud cost optimization CLI tool",
)
