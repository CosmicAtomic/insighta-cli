import click

@click.group()
def app():
    pass

@app.command()
def hello():
    click.echo("Insighta CLI is working")

if __name__ == "__main__":
    app()