# banner_cds_packager

A CLI program to build a package which can be deployed via Banner CDS. Files chosen are those changed in a range of commits.

# Installation

This program can be installed for normal usage with pip and pipx:

```
pip install pipx
pipx install git+https://github.com/middlebury/banner_cds_packager.git
```

The you can run the program with:
```
banner_cds_packager --help
```

## Development Installation

This program can be installed for normal usage with pip and pipx:

```
pip install pipx
git clone git@github.com:middlebury/banner_cds_packager.git
cd banner_cds_packager
pipx install --editable .
```

The you can run the program with:
```
banner_cds_packager --help
```

# Usage

Run this program from within a clone of your banner repository and pass it a base and a head commit. It will build a package with an instruction set in `inst.txt` and the state of the files at the head commit for all supported files changed since the base commit.

## Example

```
cd banner
banner_cds_packager --sql-user <username> --base 123abc45 --head 82b2a35
```
might yield a zip file containing:

* `inst.txt` with contents:
    ```
    RUNSQL <username> @oracle/student/table/saturn_example.ssbtest.create.sql
    RUNSQL <username> @oracle/student/table/saturn_example.stvtest.create.sql
    RUNSQL <username> @oracle/student/table/saturn_example.ssbtest.setup.sql
    RUNSQL <username> @oracle/student/views/saturn_example.syvtest.vw.sql
    PUTCRON svc_custom.crontab
    ```
* `oracle/student/table/saturn_example.ssbtest.create.sql`
* `oracle/student/table/saturn_example.stvtest.create.sql`
* `oracle/student/table/saturn_example.ssbtest.setup.sql`
* `oracle/student/views/saturn_example.syvtest.vw.sql`
* `svc_custom.crontab`

# Order of inclusion in `inst.txt`

1. `RUNSQL` instructions are ordered first by group, then alphabetically. The
  ordering allows commands to be run after the creation of objects that they may
  depend on. The default globbing patterns are indicated below, but can be
  specified in options.
   1. `table/*.create.sql`, `object/*_create.sql`: Creating new or modifying
    existing database objects.
   2. `table/*.setup.sql`, `object/*.setup.sql`: Job setup scripts (registration
    of the job, job parameters, etc).
   3. `table/*.dml.sql`, `object/*.dml.sql`: Initializing new tables with any
    seed data, or any DML in general.
   4. `function/*.fnc` Function definitions
   5. `views/*.vw`: Database view scripts.
   6. `matview/*.mv`: Materialized view definitions.
   7. `sequence/*.sql`: Sequences.
   8. `package/*.pks`: Package specifications.
   9. `package/*.pkb`: Package bodies.
   10. `procedure/*.prc`: Procedure files
   11. `triggers/*.trg`: Database triggers.
   12. `adhoc/*.sql`: Any other database actions.
2. `PUTCRON` *not yet implemented*
