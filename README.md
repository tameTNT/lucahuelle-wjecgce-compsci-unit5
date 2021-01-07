# WJEC GCE Computer Science Unit 5 Project

Luca Huelle (1902) - Rougemont School (68362)

September 2020 - May 2021

## Installation/setup

Install pipenv (used to set up a clean python virtual environment, venv, for this project) following
the instructions at
https://pipenv.pypa.io/en/latest/install/#installing-pipenv. e.g.

```shell
C:\Users> pip install --user pipenv
```

After a successful installation, navigate to the directory of this README file (i.e. the directory
containing `Pipfile.lock`) in your terminal. e.g.

```shell
C:\Users> cd "\path\to\this\dir"
```

Then run the following command to create the venv for the project. This will automatically install
all required dependencies and make the venv easier to clean up after use.

```shell
C:\Users\path\to\this\dir> pipenv shell
```

_(please make sure that **at least Python 3.8** is installed on your system for this command to
run)_

Finally, to run the application, execute the following command _within the created venv_ (which
should already by running).

```shell
(venv_name_here) C:\Users\path\to\this\dir> python main.py
```
