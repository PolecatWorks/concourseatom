import click


def test_cli(cli_runner):
    @click.command()
    @click.argument("name")
    def hello(name):
        click.echo("Hello %s!" % name)

    result = cli_runner.invoke(hello, ["Peter"])
    assert result.exit_code == 0
    assert result.output == "Hello Peter!\n"
