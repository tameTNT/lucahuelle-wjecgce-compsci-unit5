# WJEC GCE Computer Science Unit 5 Software Development

Luca Huelle (1902) - Rougemont School (68362)

September 2020 - May 2021

**The full project report (in `.docx` and `.pdf` formats) is available in the same directory as this
file.**

*README last updated 16/05/2021*

## Requirements and installation

Download the code by navigating to the [master branch of the GitHub project][1]
and clicking _code_ (top right) and then _Download Zip_. Unzip the downloaded file into a folder of
your choice.

Make sure that **Python 3.8** or above installed on your system before running the program.
_You can check your version by running `python --version` from the command line._

### Additional note on included run files

A `\.run` directory is included within the project's files. This directory includes several
`.run.xml` files which can be used in JetBrains' IDEs (including PyCharm) to automatically execute
the `main.py` file with certain command line arguments. They can therefore be ignored for typical
use and are merely included for reference/further testing.

_(NB: these `.run.xml` files use a, now deprecated, virtual environment to run the program.)_

## Usage

To run the application, navigate to the directory containing this `README.md` file and execute the
command below:

```cmd
C:\...\gce-unit-5>python main.py --show-gui
```

For further help with using this project's `main.py` file, run the following command.

```cmd
C:\...\gce-unit-5>python main.py --help
```

Extra explanatory detail on the functions listed from this help command are provided below in
**Additional functionality**.

### Fully completed features

Many parts of this project are **not fully complete** (*see the abundance of '`todo`'
/ '`wouldbenice`'s in the source code*).

Below is a list of the all the main features available to test and use in the latest version of the
program. They should be *mostly* bug-free and working as intended. Feel free to experiment with
these to get a feel for the program's capabilities:

- **Fully Object-Oriented database** (in `data_handling.py`) : each element in a subclass of *Table*
  is a subclass of *Row* (e.g. *Student* is a row object within *StudentTable*, which is itself
  stored in a *Database* object at runtime)
    - Relational database in **third normal form** with tables: *StudentLogin, Student, Section,
      Resource* and *Staff*
    - Saving data to **text files** for permanent data storage including autoload/save on program
      start/exit
    - Secure login detail storage with **password salting + hashing** (in `password_logic.py`)
- Flexible **validation** procedures (in `validation.py`) for all user input across application
  including emails, dates, etc.
- **Sample unit tests** (e.g. `test_password_logic.py`) which can be used to verify that certain
  procedures work as expected. (These are not fully complete and only partially cover the project.)
- User-friendly **command line interface** (with `--help` documentation) for running all
  operations (creating **staff accounts**, generating sample data and running the GUI application)
- Use of **logging** (to `main_program.log`) throughout program (GUI and CLI) for debugging and
  support purposes
- Scalable and modular **tkinter Graphical User Interface framework** (see `ui/__init__.py` for
  detailed, annotated implementation using layered Frames to keep program within one window). The
  complete GUI features are as follows:
    - **Login** functionality for students
        - **Student dashboard** to view an overview of current award progress and general
          information
        - Data entry for **enrolment**
        - Data entry and viewing for **section start/in progress**
        - Section **evidence uploading** - including marking evidence as an assessor's report.
          _Evidence is saved in `\uploads\student\id-??`._
    - **Login** functionality for staff
        - **Student overview table** to view award progress of all students at a glance
            - **View students** in table by award level
            - **Search** by student name/username
        - **View all stored data** (including **individual section data**) for a selected student
          and **approve/manage students on an individual basis**
        - **Add new students** to the database with unique logins

### Exemplar database

An exemplar database is provided alongside this project for easy trialing of key features. It
includes several pre-filled-in student accounts at varying stages in their theoretical award.

The database is available in the program by including `-f "(example)"` in any commands (see
**Loading specific database files** below for more information on using this argument).

e.g.

```cmd
C:\...\gce-unit-5>python main.py -f "(example)" --show-gui
```

The usernames and current states for these pre-created accounts are included below. All accounts use
the password `Passw0rd`.

- **Staff account**
    - `staff_am`
- **Student accounts**
    - `student1` - _not yet fully enrolled_
    - `student2` - _enrolled but not yet approved by staff_
    - `student3` - _one section in progress_
    - `student4` - _evidence uploaded across 2 sections with 1 assessor's report_

## Additional functionality

### Creating staff/admin accounts (`--create-staff-account`)

This operation can only be done from the command line in order to prevent students from registering
themselves as a staff/admin user.

Begin an interactive terminal session to create a new staff user with the following command.

_NB: Make sure that this is run from within a terminal environment (and not within an IDE) as
passwords cannot be entered securely within the latter._

```cmd
C:\...\gce-unit-5>python main.py --create-staff-account
```

### Loading specific database files (`-file-save-suffix SUFFIX`)

The `-f SUFFIX` (or `--file-save-suffix SUFFIX`) argument allows custom database tables to be
loaded. By default, no extra string is appended to table names on loading.

For example, not supplying the argument means the file `ResourceTable.txt` is loaded and later saved
on program termination. However, if you instead run the following command.

```cmd
C:\...\gce-unit-5>python main.py -f " (backup)" --show-gui
```

The file `ResourceTable (backup).txt` is loaded and later saved instead.

This is useful when using the program while **maintaining multiple databases** on the same computer
or when **loading test databases** (see below).

_(NB: always enclose suffixes in `"` and do not include `-` characters.)_

### Generating test databases (`--populate-tables`)

This program comes bundled with functionality to automatically populate student tables with random
student accounts. This was mainly used for testing purposes.

The function clears all tables - except for Staff login details - and creates a specified number of
students with random usernames, year groups and award levels - all with the password `password`.

Begin an interactive terminal session to generate random student accounts using the following
command.

```cmd
C:\...\gce-unit-5>python main.py --populate-tables
```

You can then use these newly generated tables in the application using the `-f " (test students)"`
flag (in combination with any of the other commands detailed above or in `--help`).

e.g.

```cmd
C:\...\gce-unit-5>python main.py -f " (test students)" --show-gui
```

[1]: https://github.com/tameTNT/lucahuelle-wjecgce-compsci-unit5
