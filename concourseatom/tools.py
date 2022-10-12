#!/usr/bin/env python
# concourseatom Copyright (C) 2022 Ben Greene
"""CLI tools for working with concourse objects
"""
import sys
import click

from concourseatom.models import Pipeline

# ------------- CLI Boiler plate here -------------


def interactivedebugger(type, value, tb):
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback
        import pdb

        # we are NOT in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print
        # ...then start the debugger in post-mortem mode.
        # pdb.pm() # deprecated
        pdb.post_mortem(tb)  # more "modern"


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    """
    Simple concourse manaagement functions

    concourseatom Copyright (C) 2022 Ben Greene

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions; See LICENSE file for details.
    """
    ctx.ensure_object(dict)

    ctx.obj["DEBUG"] = debug

    if debug:
        click.echo(f"Debug mode is {'on' if debug else 'off'}", err=True)
        sys.excepthook = interactivedebugger


# ------------- CLI commands go below here -------------


@cli.command()
@click.argument("infile", type=click.File("rb"))
@click.pass_context
def read_file(ctx, infile):

    input_file = infile.read()

    click.echo(input_file.decode())


@cli.command()
@click.pass_context
@click.argument(
    "infile0", type=click.File("rb"), default=sys.stdin
)  # , help="File to load as first file for merge")
@click.argument(
    "infile1", type=click.File("rb")
)  # , help="File to load as second file for merge")
@click.option(
    "--deep", is_flag=True, help="Attempt to perform a deep merge of parallel elements"
)
def merge(ctx, infile0, infile1, deep):
    """
    Merge two concourse jobs and resources

    Read input from stdin and named file or from two files.

    Merge will first try to merge the resource types based on the content not on the
    name.
    It will identify resources that are identical but with differing names in both files
    and then create the appropriate rewrites of resource names throughout the
    configuration.

    """
    if ctx.obj["DEBUG"]:
        click.echo(f"Starting to merge0 {infile0.name}", err=True)
        click.echo(f"Starting to merge1 {infile1.name}", err=True)

    pipe0 = Pipeline.parse_raw(infile0)
    pipe1 = Pipeline.parse_raw(infile1)

    merge = Pipeline.merge(pipe0, pipe1)

    click.echo(merge.yaml())


if __name__ == "__main__":
    cli()
