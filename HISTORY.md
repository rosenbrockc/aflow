# `aflow` Revision History

## Revision 0.0.11

- Minor changes to requirements/dependencies.
- Updated `README.md` to show how to install from `conda`.

## Revision 0.0.9

- Fixed a bug that prevented "bz2" and "png" files from being downloaded.

## Revision 0.0.8

- Fixed a bug that showed the wrong number of configs for `__len__` when slices are used.

## Revision 0.0.7

- Added support for easy file downloading via the database `Entry.files` attribute.
- Added additional examples to the documentation.

## Revision 0.0.6

- Fixed a bug in AFLUX handling of multiple instances of same keyword with complex logical conditions.
- Added support for multiple keywords on select and except.

## Revision 0.0.5

- Added `atoms` method to entry object to create `quippy` or `ase` atoms objects.
- Added some stability bug-fixes for null-result responses.

## Revision 0.0.4

- Fixed a bug in `caster.py`.

## Revision 0.0.3

- Full test coverage for both python 2 and python 3.
- Partial API documentation generation.

## Revision 0.0.2

- Coverage up to 95%
- Optimized generation of `keywords.py` and `entries.py` files.

## Revision 0.0.1

- Core functionality all working.
- 93% unit test coverage.
- Added slicing over query result sets.