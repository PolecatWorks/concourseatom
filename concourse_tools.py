#!/usr/bin/env python

from dataclasses import dataclass
import click
import io
import ruamel.yaml

yaml = ruamel.yaml.YAML()

from models import FullThing, Job, Resource, ResourceConfig, ResourceType


# ------------- CLI commands go below here -------------

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    """
    Simple concourse manaagement functions
    """
    if debug:
        click.echo(f"Debug mode is {'on' if debug else 'off'}")






@cli.command()
@click.argument('srcs', nargs=-1)
def merge(srcs):
    """
    Merge concourse jobs
    """
    click.echo(f'Starting to merge {srcs}')

    f= io.StringIO()

    ben = FullThing(
        resource_types=[ResourceType('name1', 'registry-image',
            ResourceConfig('suhlig/concourse-rss-resource', 'latest'),
            ),
        ResourceType('name2', 'registry-image',
            ResourceConfig('suhlig/concourse-rss-resource', 'latest'),
            ),
        ],
        resources=[
            Resource('d','d', {'blah': 'bahbab'}),
        ],
        jobs=[
            Job('f', [])
        ]
    )

    yaml.dump(ben, f)


    click.echo(f.getvalue())
    click.echo(f'done')

    f.close()





if __name__ == '__main__':
    cli()