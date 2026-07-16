from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from time import sleep
import typer
from typing_extensions import Annotated

def upload(
    s3_base: Annotated[str, typer.Option(help="Base path in s3 for CDS. E.g. s3://service-cds-v3-myuniversity")],
    environment: Annotated[str, typer.Option(help="Environment to upload into. NONPROD or PROD")],
    sid: Annotated[str, typer.Option(help="SID to upload into. E.g. TEST")],
    package_file: Annotated[Path, typer.Option(exists=True, writable=True, dir_okay=False, file_okay=True, help="Packaged file to be uploaded")],
):
    date = datetime.today().strftime('%Y-%m-%dT%H-%M-%S')
    dest_name = f'{date}-{package_file.name}'
    target_path = f'{s3_base}/DEPLOY_NOW/{environment}/{sid}/{dest_name}'
    upload_result = subprocess.run(f'aws s3 cp {str(package_file)} {target_path}', capture_output=True, shell=True)
    if upload_result.returncode != 0:
        raise Exception(upload_result.stderr.decode("utf-8"))
    print(f'Uploaded to {target_path}', file=sys.stderr)

    delay = 10
    total_delay = 0
    tries = 30
    i = 0
    log_result = None
    print('-' * tries, file=sys.stderr)
    while i < tries and log_result == None:
        i = i + 1
        sleep(delay * i)
        print('.', file=sys.stderr, end='')
        total_delay = total_delay + (delay * i)
        log_list_result = subprocess.run(f'aws s3 ls --recursive {s3_base}/LOGGING | grep out.txt | grep {environment}_{sid}_{dest_name}', capture_output=True, shell=True)
        if log_list_result.returncode == 0:
            log_file = re.search(r'LOGGING/.+\.zip/out\.txt', str(log_list_result.stdout.decode("utf-8")))
            if log_file:
                print(f"\nFound {log_file.group(0)}", file=sys.stderr)
                log_result = subprocess.run(f'aws s3 cp {s3_base}/{log_file.group(0)} -', capture_output=True, shell=True)
                print(log_result.stdout.decode("utf-8"))
                return 0

    raise Exception(f"Unable to fetch log files matching {environment}_{sid}_{dest_name}/out.txt after {i} tries over {total_delay} seconds", file=sys.stderr)
