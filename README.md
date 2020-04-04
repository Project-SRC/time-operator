# Time Operator - Project SRC - OpenFaaS Function

[![codecov](https://codecov.io/gh/Project-SRC/time-operator/branch/develop/graph/badge.svg)](https://codecov.io/gh/Project-SRC/time-operator)
[![Build Status](https://travis-ci.com/Project-SRC/time-operator.svg?branch=develop)](https://travis-ci.com/Project-SRC/time-operator)

The Time Operator is responsible to operate the time mathematically for the Project SRC stack.

## Dependencies

- Python 3.7.6

## Configuration

The Time Operator configuration is through operating system environment variables. Therefore the configuration must be done in host or must be passed to the container environment.

The available settings are:

> To be defined

If you have questions about how to set environment variables check these links:

- [Environment Variables - Linux](https://www.digitalocean.com/community/tutorials/how-to-read-and-set-environmental-and-shell-variables-on-a-linux-vps)
- [Environment Variables - Docker](https://serverascode.com/2014/05/29/environment-variables-with-docker.html)

**Observation**: The system was developed to run in Linux and Docker environments. No official support for Windows.

## Development

### Installing VirtualEnvWrapper

We recommend using a virtual environment created by the __virtualenvwrapper__ module. There is a virtual site with English instructions for installation that can be accessed [here](https://virtualenvwrapper.readthedocs.io/en/latest/install.html). But you can also follow these steps below for installing the environment:

```shell
sudo python3 -m pip install -U pip             # Update pip
sudo python3 -m pip install virtualenvwrapper  # Install virtualenvwrapper module
```

**Observation**: If you do not have administrator access on the machine remove `sudo` from the beginning of the command and add the flag `--user` to the end of the command.

Now configure your shell to use **virtualenvwrapper** by adding these two lines to your shell initialization file (e.g. `.bashrc`,` .profile`, etc.)

```shell
export WORKON_HOME=\$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

If you want to add a specific project location (will automatically go to the project folder when the virtual environment is activated) just add a third line with the following `export`:

```shell
export PROJECT_HOME=/path/to/project
```

Run the shell startup file for the changes to take effect, for example:

```shell
source ~/.bashrc
```

Now create a virtual environment with the following command (entering the name you want for the environment), in this example I will use the name **time-op**:

```shell
mkvirtualenv -p $(which python3) time-op
```

To use it:

```shell
workon time-op
pip install -r time_operator/requirements.txt
```

**Observaion**: Again, if necessary, add the flag `--user` to make the pipenv package installation for the local user.

### Local Execution

For local system execution, run the following command in the project root folder (assuming _virtualenv_ is already active):

```shell
faas-cli deploy time_operator
```

This will run the system on _localhost_ and will be available on the Open FaaS UI configured for the system. This way you can test new implementations.

## Tests

To run the Time Operator tests follow the script below:

1.  Enable _virtualenv_ **time-op**;
2.  Ensure that the dependencies are installed, especially:

        pytest
        pytest-coverage
        flake8

3.  Run the commands below:

```shell
export PYTHONPATH=$(pwd)                                      # Set the python path as the project folder
pytest time_operator/                                         # Performs the tests
pytest --cov=time_operator time_operator/                     # Performs tests evaluating coverage
pytest --cov=time_operator --cov-report xml time_operator/    # Generate the XML report of coverage
flake8 time_operator/                                         # Run PEP8 linter
unset PYTHONPATH                                              # Unset PYTHONPATH variable
```

During the tests the terminal will display a output with the test report (failures, skips and successes) and the system test coverage. For other configurations and supplemental documentation go to [pytest](https://pytest.org/en/latest/) and [coverage](https://pytest-cov.readthedocs.io/en/latest/).

During the lint process the terminal will report a bug report and warnings from the PEP8 style guide, for more configurations and additional documentation go to [flake8](http://flake8.pycqa.org/en/latest/index.html#quickstart) and [PEP8](https://www.python.org/dev/peps/pep-0008/)

## Build

To build the Time Operator function just follow the script below:

```shell
faas-cli build -f time_operator.yml --build-arg ADDITIONAL_PACKAGE="python3-dev libstdc++ g++"
```

Make sure you have logged in to the [docker hub](https://hub.docker.com/) service. If you do not, run the `docker login` command.

```shell
faas-cli push -f time_operator.yml
```
