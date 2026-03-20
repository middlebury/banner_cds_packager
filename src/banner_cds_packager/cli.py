import typer

from .create_banner_cds_package import create_banner_cds_package

app = typer.Typer()
app.command()(create_banner_cds_package)

if __name__ == "__main__":
    app()
