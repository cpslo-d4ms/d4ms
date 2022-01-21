# Drones for Marine Science and Agricultural

## d4ms
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/cdnjs/cdnjs.svg?style=flat)]()
[![Read the Docs](https://readthedocs.org/projects/yt2mp3/badge/?version=latest)](link)


A Cal Poly research project on using drones for marine and agricultural
research. We are using this [gitHub](link) repo for software development and
this [Google Drive](https://drive.google.com/drive/folders/1CnEYAmkELO2a23fZwlhrstGxjyTkJW6a)
for other project documents and training data storage. We are
using [dvc](https://dvc.org/) for training data version control in order to
avoid problems that git has with large files.

## Setup

When working on multiple projects on the same machine it is a good idea to use a
virtual Python environment. I like to
use [Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
but Python comes equipped with the `virtualenv` package if you don't want to
install 3rd party software. Check out
this [tutorial](https://realpython.com/python-virtual-environments-a-primer/) if
you would like some guidance. This document assumes you are using a bash shell,
so your mileage may vary on other systems.

Run the following code in your virtual environment to install all dependencies:

```
pip install -r requirements.txt
```

## Documentation

The full documentation can be found under `/docs` and in a more readable format
at [readTheDocs](link). We are using the Google documentation style.

## Packages

This project is split into **4** modules, each containing separable code units
for the different project groups.

### drone

Drone flight and behavior to be utilized mainly by the Drones group. Use
the `#drones` Slack channel to ask questions about this module.

### mission

Mission planning and control to be used mainly by the Multi-Agent fleet group.
Use the `#agents` Slack channel to ask questions about this module.

### network

Ad hoc network protocol. This module is maintained by Joel Valdovinos Miranda.

### model

Deep learning model for spotting interesting objects. Use
the `#machine-learning` Slack channel to ask questions about this module.

## Style Checking

In order to maintain project readability, we will use the following style
checkers and linters. Linting is a commonly used term in software development
for programs that automatically fix style issues whenever you save them.

### PyCodeStyle for Python

To install PyCodeStyle (formerly known as PEP8), run the following command:

```
pip install pycodestyle
```

In your editor of choice, add the python path and enable linting. For VSCode,
open the command palette (`Ctrl+Shift+P`)
and select the **Python: Enable Linting** command.

Alternatively, for VSCode, add the following to
`.vscode/settings.json`, replacing `<path>` with your python path:

```json
{
  "python.pythonPath": "<path>",
  "python.linting.Enabled": true,
  "python.linting.lintOnSave": true
}
```

### Format on Save

In your editor of choice, enable format on save so that linting is done
automatically. For VSCode, add the following to `.vscode/settings.json`:

```json
{
  "editor.defaultFormatter": null,
  "editor.formatOnSave": true,
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Prettier and ESLint for JavaScript

For modules involving a web interface, using `Node.js` is a powerful and (
relatively) easy approach. This setup is inspired by
this [tutorial](https://thomaslombart.com/setup-eslint-prettier-react/). Please
follow the link for further guidance.

To install ESLint and Prettier, run the following command in the `frontend`
directory:

```
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-prettier husky lint-staged
```

The following Prettier options are modified from their default value:

| Option | Description | 
| ------ | ----------- | 
| `"jsxBracketSameLine": true` | Put the > of a multi-line JSX element at the end of the last line instead of being alone on the next line (does not apply to self closing elements). |
| `"endOfLine": "auto"` | Maintain existing line endings (mixed values within one file are normalized by looking at what’s used after the first line). |


## TODO
* Import all data to Google Drive
* Refactor code in the `drone` module
* Update each README.
* Agree on project style standards
* Move style guides to CODE_OF_CONDUCT file?
* add ReadTheDocs page
* add Sphinx (with napoleon for Google style comments?)
* add dvc
