# Miscellaneous Projects
This is somewhere between a working space and a graveyard. Projects which have been enough work to be worthwhile displaying, but not enough to earn their own repository, can live here.

Some projects come here to die, and many will end up being stale. Consider this more a demonstration of my regular work towards improving my own abilities and testing myself. A lot of these projects have very short development lifecycles, so the code quality is substandard compared to my usual work.

# Workflows

I've begun trialling GitHub workflows as an experiment here, if for no other reason than keeping code here readable.

## Linting

Python's `yamllint` and `flake8` modules are used to enforce a mostly consistent style. To run these locally:
* `yamllint .`
* `flake8 .` OR `/usr/bin/python3 -m flake8 .` (for dual-installation python). The workflows are run with 3.10.

## Testing

The workflows are constructed so that tests for a given subproject are run when the files in the subproject are touched.