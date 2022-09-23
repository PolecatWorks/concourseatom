#!/usr/bin/env python
"""CLI tools for working with concourse objects
"""
import io
import click
import ruamel.yaml
from concourseatom.models import Pipeline, Job, Resource, ResourceType

yaml = ruamel.yaml.YAML()


# ------------- CLI commands go below here -------------


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    """
    Simple concourse manaagement functions
    """
    if debug:
        click.echo(f"Debug mode is {'on' if debug else 'off'}")


@cli.command()
@click.argument("srcs", nargs=-1)
def merge(srcs):
    """
    Merge concourse jobs
    """
    click.echo(f"Starting to merge {srcs}")

    f = io.StringIO()

    ben = Pipeline(
        resource_types=[
            ResourceType(
                "name1",
                "registry-image",
            ),
            ResourceType(
                "name2",
                "registry-image",
            ),
        ],
        resources=[
            Resource("d", "d", {"blah": "bahbab"}),
        ],
        jobs=[Job("f", [])],
    )

    yaml.dump(ben, f)

    click.echo(f.getvalue())
    click.echo("done")

    f.close()


if __name__ == "__main__":
    cli()
