# Build Instructions for Cloud Cost Optimization CLI

## Prerequisites
- Python 3.x installed
- pip installed

## Step 1: Install build dependencies
Open a terminal in the project root and run:
```
pip install setuptools wheel
```

## Step 2: Build the package
Run the following command in the project root (where `setup.py` is located):
```
python setup.py sdist bdist_wheel
```
This will create distribution files in the `dist/` folder.

## Step 3: Distribute the package
- Share the files in the `dist/` folder (`.whl` and `.tar.gz`) with users.
- Users can install the package using:
```
pip install <path-to-file.whl>
```
or
```
pip install <path-to-file.tar.gz>
```

## Step 4: Usage
After installation, users can run CLI commands such as:
```
cost-opt list
cost-opt recommend ec2
cost-opt remediate ec2 1
```

## Troubleshooting
- If you see `ModuleNotFoundError: No module named 'setuptools'`, install it with `pip install setuptools wheel`.
- Make sure your Python Scripts directory is in your system PATH for CLI commands to work.
