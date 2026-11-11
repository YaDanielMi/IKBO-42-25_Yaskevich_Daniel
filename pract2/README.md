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

## Stage 2. Data collection

The npm package format is used. The direct dependencies of the package are
taken from the registry given by `--repo` (the public npm registry by
default): the manifest of the latest version is requested over HTTP
(`<registry>/<package>/latest`) with the standard library `urllib`, and the
names from its `dependencies` field are printed. The key-value output of
the parameters (stage 1 only) is removed.

```
./run.sh -p express
```

## Stage 3. Basic operations

The full transitive dependency graph is built with a breadth-first search
(BFS) that uses a queue and no recursion (`src/depgraph/graph.py`).

* Packages whose name contains the `--filter` substring are not analysed
  (together with the dependencies that only they bring). The analysed
  package itself must not match the filter.
* Cyclic dependencies are handled: every package is visited once and the
  back edge is kept in the graph.
* Test mode (`-t -r FILE -p A`): the repository is a text file, one package
  per line, packages are named with uppercase Latin letters:

```
A: B C
B: D
C: D
D:
```

Test repositories for different cases are in `examples/test_repos`:
`chain`, `diamond`, `cycle`, `self_loop`, `isolated`, `filter`, `complex`.

```
./run.sh -t -r examples/test_repos/cycle.txt -p A
./run.sh -t -r examples/test_repos/filter.txt -p A -f B
```
