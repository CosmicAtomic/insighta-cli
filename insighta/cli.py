import click
from .auth import login, logout, whoami
from .api import list_profiles, get_profile, search_profiles, create_profile, export_profiles
from rich.console import Console
from rich.table import Table

console = Console()

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

@app.group()
def profiles():
    """Manage profiles."""
    pass

@profiles.command(name="list")
@click.option('--gender', help='Filter by gender')
@click.option('--country', help='Filter by country')
@click.option('--age-group', help='Filter by age group')
@click.option('--min-age', type=int, help='Minimum age')
@click.option('--max-age', type=int, help='Maximum age')
@click.option('--sort-by', help='Sort by field')
@click.option('--order', default='asc', help='Sort order')
@click.option('--page', default=1, type=int)
@click.option('--limit', default=20, type=int)
def list_cmd(gender, country, age_group, min_age, max_age, sort_by, order, page, limit):
    with console.status("Fetching profiles..."):
        data = list_profiles(gender=gender, country_id=country, age_group=age_group, min_age=min_age, max_age=max_age, sort_by=sort_by, order=order, page=page, limit=limit)
    if not data:
        return

    table = Table(title=f"Profiles (Page {data['page']} of {data.get('total_pages', '?')})")
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Country")

    for p in data["data"]:
        table.add_row(p["name"], p["gender"], str(p["age"]), p["country_id"])

    console.print(table)
    console.print(f"Total: {data['total']}")

@profiles.command(name="get")
@click.argument('id')
def get_cmd(id):
    with console.status("Fetching profile..."):
        data = get_profile(id)
    if not data:
        return
    table = Table(title="Profile")
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Country")
    p = data["data"]
    table.add_row(p["name"], p["gender"], str(p["age"]), p["country_id"])
    console.print(table)

@profiles.command(name="search")
@click.argument('query')
def search_cmd(query):
    with console.status("Searching profiles..."):
        data = search_profiles(query=query)
    if not data:
        return
    table = Table(title=f"Search results for '{query}'")
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Country")
    for p in data["data"]:
        table.add_row(p["name"], p["gender"], str(p["age"]), p["country_id"])
    console.print(table)

@profiles.command(name="create")
@click.option('--name', required=True, help='Name of profile')
def create_cmd(name):
    with console.status("Creating profile..."):
        data = create_profile(name)
    if not data:
        return
    table = Table(title="Profile Created")
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age")
    table.add_column("Country")
    p = data["data"]
    table.add_row(p["name"], p.get("gender", "-"), str(p.get("age", "-")), p.get("country_id", "-"))
    console.print(table)

@profiles.command()
@click.option('--format', type=click.Choice(['csv']), default='csv')
@click.option('--gender', help='Filter by gender')
@click.option('--country', help='Filter by country')
def export(format, gender, country):
    with console.status("Exporting..."):
        content = export_profiles(format=format, gender=gender, country_id=country)
    if not content:
        return
    filename = "profiles_export.csv"
    with open(filename, "wb") as f:
        f.write(content)
    console.print(f"Saved to {filename}")

if __name__ == "__main__":
    app()