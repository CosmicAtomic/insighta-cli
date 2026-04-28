import click
from .auth import login, logout, whoami

@click.group()
def app():
    pass

@app.command()
def hello():
    click.echo("Insighta CLI is working")

@app.command(name="login")
def login_cmd():
    login()

@app.command(name="logout")
def logout_cmd():
    logout()

@app.command(name="whoami")
def whoami_cmd():
    whoami()

if __name__ == "__main__":
    app()