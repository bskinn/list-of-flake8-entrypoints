List of flake8 Plugin Entry Points
==================================

Flake8 uses the `entry_points` mechanism in Python packaging
to define (at minimum) the scope of the error codes raised
by a code-checking plugin.

If multiple plugins try to claim the same error code
namespace, one or the other plugin will silently(?)
just not be loaded.

Goal here is to automatically assemble a list of the
full claimed namespace of flake8 error codes,
to allow authors of new plugins to confidently
choose error codes that are likely to be as-yet unclaimed.

