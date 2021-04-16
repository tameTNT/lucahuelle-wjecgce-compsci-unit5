# WJEC GCE Computer Science Unit 5 Project

*Luca Huelle (1902) - Rougemont School (68362)*

*September 2020 - May 2021*

## Installation

Install **pipenv** (used to set up a clean Python virtual environment - a 'venv' - for this project) following the instructions at:
https://pipenv.pypa.io/en/latest/install/#installing-pipenv.

e.g.

```cmd
C:\Users>pip install --user pipenv
```

After a successful installation, navigate to the directory of this `README.md` file (i.e. the directory containing `Pipfile.lock`) in your terminal.

e.g.

```cmd
C:\Users>cd "\path\to\this\dir"
```

Then run the following command to create the venv for the project. This will automatically install all required dependencies and make the venv easier to clean up after use.

_NB: Please make sure that **at least Python 3.8** is installed on your system before running this command_

```cmd
C:\Users\path\to\this\dir>pipenv shell
```

## Typical Usage

To run the application, execute the following command _within the created venv_ (which should already by running from the previous section).

_NB: Your venv name may be different from 'gce-unit-5'_

```cmd
(gce-unit-5) C:\...\dir>python main.py --show-gui
```

For further help with using this project's `main.py` file, run the following command.

```cmd
(gce-unit-5) C:\...\dir>python main.py --help
```

Some extra explanatory detail on these functions is provided below.

## Additional functions

### Creating admin/staff accounts

This operation can only be done from the command line in order to prevent students from registering themselves as a user.

Begin an interactive terminal session to create a new staff user with the following command.

_NB: Make sure that this is run from within a terminal environment (and not within an IDE) as passwords cannot be entered securely within the latter_

```cmd
(gce-unit-5) C:\...\dir>python main.py --create-staff-account
```

### Loading specific database files

The `-f SUFFIX` (or `--file-save-suffix SUFFIX`) argument allows custom database tables to be loaded. By default, no extra string is appended to table names on loading.

For example, not supplying the argument means the file `ResourceTable.txt` is loaded and later saved on program termination. However, if you instead run the following command.

```cmd
(gce-unit-5) C:\...\dir>python main.py -f " (backup)" --show-gui
```

The file `ResourceTable (backup).txt` is loaded and later saved instead.

This is useful when using the program while **maintaining multiple databases** on the same computer or when **loading test databases** (see below).

### Generating test databases

This program comes bundled with functionality to automatically populate student tables with random student accounts. This was mainly used for testing purposes.

The function clears all tables - except for Staff login details - and creates a specified number of students with random usernames, year groups and award levels - all with the password `password`.

Begin an interactive terminal session to generate random student accounts using the following command.

```cmd
(gce-unit-5) C:\...\dir>python main.py --populate-tables
```

You can then use these newly generated tables in the application using the `-f " (test students)"` flag (in combination with any of the other commands detailed above or in `--help`).

e.g.

```cmd
(gce-unit-5) C:\...\dir>python main.py -f " (test students)" --show-gui
```
