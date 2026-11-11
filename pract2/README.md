# depgraph

Dependency graph visualiser for npm packages (practical work, variant 31).

The project is developed in stages. Dependencies are collected by the tool
itself: no package managers and no third-party libraries are used, only the
Python standard library.

## Stage 1. Minimal prototype with configuration

The application is configured with command line options and prints all of
them as `key: value` pairs.

| Option | Meaning |
|--------|---------|
| `-p`, `--package` | name of the analysed package (required) |
| `-r`, `--repo` | repository URL or path to the test repository file |
| `-t`, `--test-mode` | work with a test repository described in a file |
| `-o`, `--output` | name of the generated PNG file (default `graph.png`) |
| `-a`, `--ascii-tree` | print the dependencies as an ASCII tree |
| `-f`, `--filter` | ignore packages whose name contains this substring |

Every option is validated; an invalid value gives `error: ...` on stderr
and exit code 1.

## Build and tests

```
make test
```

## Usage

```
./run.sh -p express -f babel -a
```
