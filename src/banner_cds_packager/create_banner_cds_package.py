from .package import Package
from .package import DirectoryPackage
from .package import ZipPackage
from enum import Enum
import glob
import typer
from pathlib import Path
import re
from rich import print
from rich.console import Console
import subprocess
from typing_extensions import Annotated

class OutputMode(str, Enum):
    zip = "zip"
    directory = "directory"

def create(
    base: Annotated[str, typer.Option(help="The sha ID of the commit after which changes are made")],
    head: Annotated[str, typer.Option(help="The sha ID of the head commit")],
    username: Annotated[str, typer.Option(help="The oracle username to run SQL commands as")],
    output_mode: Annotated[OutputMode, typer.Option()] = OutputMode.zip,
    output_dir: Annotated[Path, typer.Option(exists=True, writable=True, dir_okay=True, file_okay=False, help="Path to the directory where the output will be written")] = Path("/tmp"),
    output_filename: Annotated[str, typer.Option(help="The filename to use for the result. If not specified, will be 'deploy-<base>_<head>.zip' for zip output and 'deploy-<base>_<head>/' for directory mode.")] = None,

    # Options for identifying changed banner files to add to the package.

    # SQL
    object_create_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match table and object definition file patterns. Can be specified multiple times.")] = ["*/table/*.create.sql", "*/object/*.create.sql"],
    object_setup_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match table and object setup file patterns. Can be specified multiple times.")] = ["*/table/*.setup.sql", "*/object/*.setup.sql"],
    object_dml_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match table and object DML file patterns. Can be specified multiple times.")] = ["*/table/*.dml.sql", "*/object/*.dml.sql"],
    function_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match file patterns. Can be specified multiple times.")] = ["*/function/*.fnc"],
    view_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match view file patterns. Can be specified multiple times.")] = ["*/views/*.vw"],
    matview_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match materialized view file patterns. Can be specified multiple times.")] = ["*/matview/*.mv", "*/matview/*.sql", "*/matview/*.vw"],
    sequence_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match sequence file patterns. Can be specified multiple times.")] = ["*/sequence/*.sql"],
    package_spec_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match package specification file patterns. Can be specified multiple times.")] = ["*/package/*.pks"],
    package_body_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match package body file patterns. Can be specified multiple times.")] = ["*/package/*.pkb"],
    procedure_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match procedure file patterns. Can be specified multiple times.")] = ["*/procedure/*.prc"],
    trigger_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match trigger file patterns. Can be specified multiple times.")] = ["*/trigger/*.trg"],
    adhoc_sql_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match ad-hoc SQL file patterns. Can be specified multiple times.")] = ["*/adhoc/*.sql"],
):
    err_console = Console(stderr=True)
    instructions = []
    changed_files = run_git_command(['git', 'diff', '--name-only', '--diff-filter=d', f"{base}..{head}"]).splitlines()
    changed_files = list(map(lambda file: Path(file), changed_files))

    if output_mode == OutputMode.directory:
        if output_filename:
            package = DirectoryPackage(output_dir / output_filename)
        else:
            package = DirectoryPackage(output_dir / f"deploy-{base}_{head}")
    elif output_mode == OutputMode.zip:
        if output_filename:
            package = ZipPackage(output_dir / output_filename)
        else:
            package = ZipPackage(output_dir / f"deploy-{base}_{head}.zip")
    else:
        raise ValueError(f"Unknown --output_mode {output_mode}")

    add_sql(instructions, package, changed_files, object_create_pattern, username)
    add_sql(instructions, package, changed_files, object_setup_pattern, username)
    add_sql(instructions, package, changed_files, object_dml_pattern, username)
    add_sql(instructions, package, changed_files, function_pattern, username)
    add_sql(instructions, package, changed_files, view_pattern, username)
    add_sql(instructions, package, changed_files, matview_pattern, username)
    add_sql(instructions, package, changed_files, sequence_pattern, username)
    add_sql(instructions, package, changed_files, package_spec_pattern, username)
    add_sql(instructions, package, changed_files, package_body_pattern, username)
    add_sql(instructions, package, changed_files, procedure_pattern, username)
    add_sql(instructions, package, changed_files, trigger_pattern, username)
    add_sql(instructions, package, changed_files, adhoc_sql_pattern, username)

    if instructions:
        package.create_file("\n".join(instructions) + "\n", Path("inst.txt"))
        err_console.print(f"Packaged into:")
        # Print the filename to stdout for access by other scripts
        print(str(package.get_path()))
    else:
        package.delete()
        err_console.print("No changes to package")

def run_git_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f'Git command failed with the following error:\n{stderr.decode()}')
    return stdout.decode().strip()

def add_sql(instructions: list, package: Package, changed_files: list, file_patterns: list, username: str):
    for file in match_files(changed_files, file_patterns):
        destination_file = rename_sql_if_needed(file)
        package.copy_in_file(file, destination_file)
        instructions.append(f"RUNSQL {username} {destination_file}")

def match_files(files: list, patterns: list):
    matches = set()
    for file in files:
        for pattern in patterns:
            regex = re.compile(glob.translate(pattern))
            if regex.search(str(file)):
                matches.add(file)
    return matches

def rename_sql_if_needed(file: Path):
    # Ensure there is a .sql suffix.
    if file.suffix not in ['.sql', '.pks', '.pkb']:
        file = file.with_suffix('.sql')
    name = str(file)
    # Ensure that there are not any sub-directories or other unallowed characters.
    disallowed = ['/', '-', '[', '@', '!', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?', '\\', '|', '}', '{', '~', ':']
    for char in disallowed:
        name = name.replace(char, '_')
    return Path(name)
