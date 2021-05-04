# WJEC GCE Computer Science Unit 5 Software Development

Luca Huelle (1902) - Rougemont School (68362)

September 2020 - May 2021

*README last updated 20/04/2021*

## Installation

Install **pipenv** (used to set up a clean Python virtual environment - a 'venv' - for this project)
following the instructions at:
https://pipenv.pypa.io/en/latest/install/#installing-pipenv.

e.g.

```cmd
C:\Users>pip install --user pipenv
```

After a successful installation, navigate to the directory of this `README.md` file (i.e. the
directory containing `Pipfile.lock`) in your terminal.

e.g.

```cmd
C:\Users>cd "\path\to\this\dir"
```

Then run the following command to create the venv for the project. This will automatically install all required
dependencies and make the venv easier to clean up after use.

_NB: Please make sure that **at least Python 3.8** is installed on your system before running this command_

```cmd
C:\Users\path\to\this\dir>pipenv shell
```

### Additional notes on .run files

A `.run\` directory is included within the project's files. These can be used in JetBrains' IDEs (including PyCharm),
after setting up the venv, to automatically execute the `main.py` file with certain command line arguments. They can
therefore be ignored for typical use and are merely included for reference/further testing.

## Typical Usage

To run the application, execute the following command _within the created venv_ (which should already by running from
the previous section).

_NB: Your venv name may be different from 'gce-unit-5'_

```cmd
(gce-unit-5) C:\...\dir>python main.py --show-gui
```

For further help with using this project's `main.py` file, run the following command.

```cmd
(gce-unit-5) C:\...\dir>python main.py --help
```

Extra explanatory detail on these functions is provided further below.

### _IMPORTANT_: Completed features

Many parts of this project are **not fully complete** (*see the abundance of '`todo`'
/ '`wouldbenice`'s in the source code*).

Below is a list of the all the main features available to test and use in this latest version of the
program. They should be *mostly* bug-free and working as intended. Feel free to experiment with
these to get a feel for the program's capabilities:

- **Fully Object-Oriented database** (in `data_handling.py`) : each element in a subclass of *Table*
  is a subclass of *Row* (e.g. *Student* is a row object within *StudentTable*, which is itself
  stored in a *Database* object at runtime)
  - Relational database in **third normal form**: *StudentLogin, Student, Section, Resource* and *
    Staff*
  - Saving data to **text files** for permanent data storage including autoload/save on program
    start/exit
  - Secure login detail storage with **password salting + hashing** (in `password_logic.py`)
- Flexible **validation** procedures (in `validation.py`) for all user input across application
  including emails, dates, etc.
- **Sample unit tests** (e.g. `test_password_logic.py`) which can be used to verify that certain
  procedures work as expected
- User-friendly **command line interface** (with `--help` documentation) for running all
  operations (creating admin accounts, test data, running GUI application)
- Use of **logging** (to `main_program.log`) throughout program (GUI and CLI) for user '
  self-debugging' and for easing IT support
- Scalable and modular **tkinter Graphical User Interface framework** (see `ui/__init__.py` for
  detailed, annotated implementation) using layered Frames to keep program within one window. The
  complete GUI features are as follows:
  - **Login** functionality for students
    - **Student dashboard** to view an overview of current award progress and general information
    - Data entry **enrolment**
    - Data entry and viewing for **section start/in progress**
    - Section **evidence uploading** - including marking evidence as an assessor's report
  - **Login** functionality for staff
    - **Student overview table** to view award progress of all students at a glance
      - **Refine** student **views** by award level
      - **Search** by student name/username
    - **View all stored data** (including **individual section data**) for a selected student and
      **approve/manage students on an individual basis**

## Additional functionality

### Creating admin/staff accounts

This operation can only be done from the command line in order to prevent students from registering
themselves as a user.

Begin an interactive terminal session to create a new staff user with the following command.

_NB: Make sure that this is run from within a terminal environment (and not within an IDE) as
passwords cannot be entered securely within the latter_

```cmd
(gce-unit-5) C:\...\dir>python main.py --create-staff-account
```

### Loading specific database files

The `-f SUFFIX` (or `--file-save-suffix SUFFIX`) argument allows custom database tables to be
loaded. By default, no extra string is appended to table names on loading.

For example, not supplying the argument means the file `ResourceTable.txt` is loaded and later saved
on program termination. However, if you instead run the following command.

```cmd
(gce-unit-5) C:\...\dir>python main.py -f " (backup)" --show-gui
```

The file `ResourceTable (backup).txt` is loaded and later saved instead.

This is useful when using the program while **maintaining multiple databases** on the same computer
or when **loading test databases** (see below).

### Generating test databases

This program comes bundled with functionality to automatically populate student tables with random
student accounts. This was mainly used for testing purposes.

The function clears all tables - except for Staff login details - and creates a specified number of
students with random usernames, year groups and award levels - all with the password `password`.

Begin an interactive terminal session to generate random student accounts using the following
command.

```cmd
(gce-unit-5) C:\...\dir>python main.py --populate-tables
```

You can then use these newly generated tables in the application using the `-f " (test students)"`
flag
(in combination with any of the other commands detailed above or in `--help`).

e.g.

```cmd
(gce-unit-5) C:\...\dir>python main.py -f " (test students)" --show-gui
```
