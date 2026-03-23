import glob
import typer
from pathlib import Path
import re
import shutil
import subprocess
from typing_extensions import Annotated


def create_banner_cds_package(
    base: Annotated[str, typer.Option(help="The sha ID of the commit after which changes are made")],
    head: Annotated[str, typer.Option(help="The sha ID of the head commit")],
    username: Annotated[str, typer.Option(help="The oracle username to run SQL commands as")],
    temp_dir: Annotated[Path, typer.Option(exists=True, writable=True, dir_okay=True, file_okay=False, help="Path to the temporary directory")] = Path("/tmp"),

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

    # Cron
    cron_pattern: Annotated[list[str], typer.Option(help="A glob pattern that will match cron file patterns. Can be specified multiple times.")] = ["crontab/*.txt"]
):

    package_dir = temp_dir / f"deploy-{base}_{head}"
    print(f"Packaging into {str(package_dir)} ...")

    changed_files = run_git_command(['git', 'diff', '--name-only', '--diff-filter=d', f"{base}..{head}"]).splitlines()
    changed_files = list(map(lambda file: Path(file), changed_files))

    if package_dir.exists():
        shutil.rmtree(package_dir)

    package_dir.mkdir()
    instructions_path = package_dir / 'inst.txt'
    instructions_path.touch()
    instructions = open(instructions_path, "a")

    add_sql(instructions, package_dir, changed_files, object_create_pattern, username)
    add_sql(instructions, package_dir, changed_files, object_setup_pattern, username)
    add_sql(instructions, package_dir, changed_files, object_dml_pattern, username)
    add_sql(instructions, package_dir, changed_files, function_pattern, username)
    add_sql(instructions, package_dir, changed_files, view_pattern, username)
    add_sql(instructions, package_dir, changed_files, matview_pattern, username)
    add_sql(instructions, package_dir, changed_files, sequence_pattern, username)
    add_sql(instructions, package_dir, changed_files, package_spec_pattern, username)
    add_sql(instructions, package_dir, changed_files, package_body_pattern, username)
    add_sql(instructions, package_dir, changed_files, procedure_pattern, username)
    add_sql(instructions, package_dir, changed_files, trigger_pattern, username)
    add_sql(instructions, package_dir, changed_files, adhoc_sql_pattern, username)

    instructions.close()


def run_git_command(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f'Git command failed with the following error:\n{stderr.decode()}')
        return stdout.decode().strip()
    except Exception as e:
        print(e)

def add_sql(instructions, package_dir, changed_files, file_patterns, username):
    for file in match_files(changed_files, file_patterns):
        destination_file = rename_sql_if_needed(file)
        copy_file(file, package_dir, destination_file)
        instructions.write(f"RUNSQL {username} @{destination_file}\n")

def match_files(files, patterns):
    matches = set()
    for file in files:
        for pattern in patterns:
            regex = re.compile(glob.translate(pattern))
            if regex.search(str(file)):
                matches.add(file)
    return matches

def rename_sql_if_needed(file):
    if file.suffix in ['.sql', '.pks', '.pkb']:
        return file
    return file.with_suffix('.sql')

def copy_file(source_file, package_dir, destination_file):
    destination_path = package_dir / destination_file
    destination_path.parent.mkdir(parents=True)
    shutil.copy(source_file, destination_path)
