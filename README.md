# Simple crawler

Built as a test task for a job and serves no practical purpose.

## Usage

The crawler is a Python package, it installs a command line tool named `crawler`, which
takes a domain name and output file path as arguments. Optionally debug logging can be enabled with
the `--verbose` option.

The quickest way to get started would be to build a Docker image and run the crawler as a container.

```bash
docker build -t mraag/crawler .
docker run -v `pwd`:`pwd` -w `pwd` -it mraag/crawler:latest hypercritical.co sitemap.txt
```

The run command mounts the current working directory in the container and executes the command
in it, to ensure the output file will be saved there.

Alternatively install the Python application directly. The application depends on
[Python 3.8](https://www.python.org/downloads/) and [Poetry](https://poetry.eustace.io).
You might want to use [pyenv](https://github.com/pyenv/pyenv) to manage the Python installation.

```bash
# Build the pacakge
poetry build
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate
# Install the package in it
pip install dist/crawler-*.whl
# Run the crawler
crawler hypercritical.co sitemap.txt
```

The output file will include one line per crawled path under the domain. Each line is a comma
separated list of paths, where the first value is the path of the crawled page and subsequent values
are all links found on the page.

For example:

```
/,/foo,/bar
/foo,/bar,/baz
/bar,/foo
/baz,/foo
```

The page at path `/` includes links to `/foo` and `/bar`, the page at path `/foo` includes links to
`/bar` and `/baz` etc.

## Development setup

Development requires the same dependencies as are required for running the application, described
above.

Install requirements for development.

```bash
poetry install --develop=.
```

Run tests.

```bash
poetry run pytest
```

Run the command line tool.

```bash
poetry run crawler hypercritical.co sitemap.txt
```
