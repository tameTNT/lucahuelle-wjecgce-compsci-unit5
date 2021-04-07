# WJEC GCE Computer Science Unit 5 Project

Luca Huelle (1902) - Rougemont School (68362)

September 2020 - May 2021

## Installation/Initial setup

Install **pipenv** (used to set up a clean Python virtual environment - a 'venv' - for this project)
following the instructions at
https://pipenv.pypa.io/en/latest/install/#installing-pipenv.

e.g.
```commandline
C:\Users>pip install --user pipenv
```

After a successful installation, navigate to the directory of this `README.md` file
(i.e. the directory containing `Pipfile.lock`) in your terminal. e.g.

```commandline
C:\Users>cd "\path\to\this\dir"
```

Then run the following command to create the venv for the project. This will automatically install
all required dependencies and make the venv easier to clean up after use.

_Please make sure that **at least Python 3.8** is installed on your system before running this
command:_

```commandline
C:\Users\path\to\this\dir>pipenv shell
```

## Running the program

To run the application, execute the following command _within the created venv_
(which should already by running from the previous section).

_NB: Your venv name may be different from 'gce-unit-5'_

```commandline
(gce-unit-5) C:\...\dir>python main.py --show-gui
```

For further help with using this project's main.py file, run:

```commandline
(gce-unit-5) C:\...\dir>python main.py --help
```

### Loading specific text databases

The `-s STR` (or `--file-save-suffix STR`) argument allows custom database tables to be loaded. By
default, no extra string is appended to table names on loading.

For example, not supplying the argument means the file `ResourceTable.txt`
is loaded and later saved. However, if instead you run the following:

```commandline
(gce-unit-5) C:\...\dir>python main.py --show-gui -s " (backup)"
```

the file `ResourceTable (backup).txt` is loaded and later saved instead.

This is useful when running the program using multiple databases stored on the same computer or when
loading test databases.

### Creating admin/staff accounts

This can only be done from the command line in order to prevent just anyone from registering
themselves as a user.

Begin an interactive terminal session to create a new staff user with the following command:

```commandline
(gce-unit-5) C:\...\dir>python main.py --create-staff-account
```

_NB: make sure that this is run from within a terminal environment and not within an IDE as
passwords cannot be entered securely within the latter_
