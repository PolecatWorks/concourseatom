# concourseatom Copyright (C) 2022 Ben Greene
import os
import click
import pytest

from concourseatom.tools import cli


def test_cli(cli_runner):
    @click.command()
    @click.argument("name")
    def hello(name):
        click.echo("Hello %s!" % name)

    result = cli_runner.invoke(hello, ["Peter"])
    assert result.exit_code == 0
    assert result.output == "Hello Peter!\n"


@pytest.fixture
def input_file(tmp_path):
    # create your file manually here using the tmp_path fixture
    # or just import a static pre-built mock file
    # something like :
    target_output = os.path.join(tmp_path, "mydoc.csv")
    with open(target_output, "w+") as f:
        # write stuff here
        f.write("lflfflfllf")
    return target_output


def test_file_read_sample(cli_runner, input_file):
    @click.command()
    @click.argument("infile", type=click.File("rb"))
    def read_file_sample(infile):

        input_file = infile.read()

        click.echo(f"Open file: {input_file.decode()}")

    result = cli_runner.invoke(read_file_sample, [input_file])
    assert result.exit_code == 0
    assert result.output == "Open file: lflfflfllf\n"


# def merge_data_generator():
#     for d in xx:
#         yield d


# @pytest.fixture(params = merge_data_generator())
# def merge_data():
#     return request.param


# @pytest.mark.parametrize(
#     "file0, file1",
#     [
#         ('pipeline00.yaml', 'pipeline01.yaml'),
#     ])
# @pytest.fixture(params=)


def generate_test_filename(request, filename):
    module_pathname = os.path.splitext(request.module.__file__)[0]
    function_name = request.node.originalname
    data_dir = f"{module_pathname}-{function_name}"

    return os.path.join(data_dir, filename)


@pytest.mark.parametrize(
    "filename0, filename1",
    [
        ("pipeline00.yaml", "pipeline01.yaml"),
        ("pipeline00.yaml", "manually-triggered.yaml"),
    ],
)
def test_merge_cli(cli_runner, request, filename0, filename1):

    file0 = generate_test_filename(request, filename0)
    file1 = generate_test_filename(request, filename1)
    print(f"Merge data0 = {file0}")
    print(f"Merge data1 = {file1}")

    result = cli_runner.invoke(cli, ["merge", file0, file1])

    print(result)
    assert result.exit_code == 0
    print(result.output)
