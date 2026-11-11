# depgraph

Dependency graph visualiser for npm packages (practical work, variant 31).

`depgraph` collects the dependencies of an npm package **by itself** (no
package managers and no third-party libraries are used, only the Python 3
standard library), builds the transitive dependency graph with a
breadth-first search, prints it as text and as an ASCII tree and draws it
with PlantUML into a PNG file.

Requirements: Python 3.9+. PlantUML is optional (see "Image generation").

## Project layout

```
src/depgraph/          source code
    cli.py             command line interface
    config.py          parameters and their validation
    npm_repository.py  direct dependencies from an npm registry (HTTP)
    file_repository.py test repository stored in a text file
    repository.py      choice of the repository
    graph.py           BFS graph, reverse dependencies, filter
    ascii_tree.py      ASCII tree output
    plantuml.py        PlantUML text and PNG rendering
tests/                 unit tests (unittest)
examples/test_repos/   test repositories for different cases
scripts/compare.sh     comparison with `npm ls`
run.sh, Makefile       run and test commands
```

## Options and features

| Option | Meaning |
|--------|---------|
| `-p`, `--package` | name of the analysed package (required) |
| `-r`, `--repo` | repository URL (default `https://registry.npmjs.org`); in test mode, path to the test file |
| `-t`, `--test-mode` | work with a test repository described in a file |
| `-o`, `--output` | name of the generated PNG file (default `graph.png`) |
| `-a`, `--ascii-tree` | print the dependencies as an ASCII tree |
| `-f`, `--filter` | ignore packages whose name contains this substring |
| `--reverse` | print reverse dependencies: packages that depend on `-p` |

Every option is validated. An invalid value (empty or malformed package
name, bad URL, missing test repository file, output name that is not
`*.png` or is in a missing directory, filter with whitespace, unknown
package, unreachable registry, malformed repository file, ...) gives
`error: ...` on stderr and exit code 1.

### Dependency graph (BFS)

* The transitive graph is built with a BFS that uses a queue and no
  recursion (`graph.py`). Each package is visited once.
* Packages whose name contains the `--filter` substring are not analysed,
  together with the dependencies that only they bring. The analysed package
  itself must not match the filter.
* Cyclic dependencies (also a package depending on itself) are handled:
  the back edge stays in the graph and the traversal terminates.
* Only the `dependencies` field of the latest version of a package is used
  (`<registry>/<package>/latest`); `devDependencies`, `peerDependencies`
  and `optionalDependencies` are ignored.

### Reverse dependencies

`--reverse` prints the packages that depend on `-p`, directly or through
other packages, with the same BFS going along the edges backwards. An npm
registry cannot list all its packages, so reverse dependencies are
available in test mode only.

### ASCII tree

`--ascii-tree` prints the graph as a tree. A package that closes a cycle is
marked `(cycle)`, a package whose subtree is already shown above is marked
`(*)` and is not expanded again (like `deduped` in `npm ls`).

### Image generation

The graph is written in the PlantUML language to `<output>.puml` (an arrow
`A --> B` means "A depends on B") and rendered into the PNG file given by
`--output`. The renderer is chosen automatically:

1. `java -jar $PLANTUML_JAR` if the `PLANTUML_JAR` variable is set;
2. the `plantuml` command if it is installed;
3. otherwise the public PlantUML server (needs network access).

If rendering fails, the `.puml` text is kept and can be rendered manually.

### Test mode

In test mode the repository is a text file with one package per line:
the name, a colon and the direct dependencies. Packages are named with
uppercase Latin letters. Empty lines and lines starting with `#` are
ignored.

```
A: B C
B: D
C: D
D:
```

Ready-made repositories are in `examples/test_repos`: `chain`, `diamond`,
`cycle`, `self_loop`, `isolated`, `filter`, `complex`.

## Build and tests

No build is needed, only Python 3.

```
make test        # run all unit tests
make run ARGS="-p express"
make demo        # graphs of express, react and axios (network needed)
make compare PKG=express   # compare with npm ls (npm and network needed)
```

Without `make`: `PYTHONPATH=src python3 -m unittest discover -s tests`.

## Usage examples

### npm packages

```
./run.sh -p express
./run.sh -p express -a -o express.png
./run.sh -p @babel/core -f plugin -a
./run.sh -p express -r https://registry.npmjs.org
```

### Test repository

```
$ ./run.sh -t -r examples/test_repos/complex.txt -p A -a -o complex.png
Dependencies of A: 8 package(s)
  A -> B, C
  B -> D, E
  C -> F
  D -> G
  E -> G, H
  F -> H
  G -> (none)
  H -> I
  I -> B

A
|-- B
|   |-- D
|   |   `-- G
|   `-- E
|       |-- G (*)
|       `-- H
|           `-- I
|               `-- B (cycle)
`-- C
    `-- F
        `-- H (*)
PlantUML text: complex.puml
Graph image: complex.png
```

Filter (`AB` and `BC` contain `B`, so they and `D` are not reached):

```
$ ./run.sh -t -r examples/test_repos/filter.txt -p A -f B
Dependencies of A: 1 package(s)
  A -> C
  C -> (none)
```

Reverse dependencies, with a cycle B -> E -> H -> I -> B in the graph:

```
$ ./run.sh -t -r examples/test_repos/complex.txt -p G --reverse
Reverse dependencies of G: 8 package(s)
  G <- D, E
  D <- B
  E <- B
  B <- A, I
  A <- (none)
  I <- H
  H <- E, F
  F <- C
  C <- A
```

The PlantUML text of a cycle (`examples/test_repos/cycle.txt`):

```
@startuml
title Dependencies of A
rectangle "A" as n0 #LightBlue
rectangle "B" as n1
rectangle "C" as n2
rectangle "D" as n3
n0 --> n1
n1 --> n2
n2 --> n0
n2 --> n3
@enduml
```

### Errors

```
$ ./run.sh -p "Bad Name"
error: invalid package name 'Bad Name': expected an npm name
$ ./run.sh -t -r examples/test_repos/chain.txt -p Z
error: package 'Z' not found in the test repository
$ ./run.sh -t -r examples/test_repos/chain.txt -p A -f A
error: package 'A' contains the filter substring 'A'
$ ./run.sh -t -r nofile.txt -p A
error: test repository file not found: nofile.txt
$ ./run.sh -p express --reverse
error: an npm registry cannot list all packages, so reverse dependencies are available only in test mode
```

## Comparison with the standard tool

`scripts/compare.sh PACKAGE` installs the package into a temporary
directory, takes the package names from `npm ls --all --parseable` and
prints the names that are present only in `npm ls` or only in `depgraph`.
Differences are expected for these reasons:

* `npm ls` shows what was installed: the versions selected by semver
  ranges and placed (hoisted, deduplicated) in `node_modules`; `depgraph`
  reads the `dependencies` of the latest published version of every package.
* npm installs `peerDependencies` (npm 7+) and platform specific
  `optionalDependencies` (for example `fsevents`); `depgraph` reads only
  `dependencies`.
* `npm ls` marks repeated packages as `deduped`, `depgraph` as `(*)` and
  cycles as `(cycle)`.
* `--filter` removes packages that `npm ls` still shows.
