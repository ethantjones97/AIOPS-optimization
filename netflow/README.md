# netflow
A python package for network optimization using Google OR Tools. 

## Install
Given that this package is still under active development, the recommended way to install is in editable mode using `pip`. Editable mode allows a person to import the `netflow` package and use as normal, but also reflects live updates to the codebase. To install the package in editable mode, open a terminal and change directories to the root folder where the `setup.py` file lives. From there, run the `pip` command,
```
pip install -e .
```
After the package is in a more robust and sustainable state, the recommended way to install is by running the `setup.py` file,
```
python setup.py install
```

## Contributing
To contribute, please follow the standard pipeline:
* Create feature branch
* Make changes in feature branch
* Create pull request and select reviewers
* If approved, feature branch will be merged into master, otherwise, additional changes will be needed as requested by reviewer(s)