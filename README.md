# GMAT-Python-simple

An extra wrapper library for the GMAT Python API to simplify setting up mission simulations. The wrapper aims to align
Python
commands with GMAT script ones, greatly reducing the number of lines required to model a mission. To do this, it
automatically creates relevant subclasses and sets default values, while still allowing the user full control over
parameters if they need something specific. The aim is to reduce the time that the user needs to spend thinking about
how the API works, so they can instead focus on the orbital mechanics and broader design of their particular mission.

Due to the library's extensive use of classes and methods rather than strings, it also supports full code completion. It
has been designed to be as intuitive as possible for the user, while still closely matching GMAT's design philosophy.

## Compatibility

The library itself should be compatible with Python 3.9 to 3.14. If you find any incompatibilities, please raise an
[issue](https://github.com/weasdown/GMAT-Python-simple/issues). However, out of the box, GMAT R2025a supports only
Python 3.9 to 3.12. This means that **without adding extra plugins to your GMAT install, this library can only be used
with Python 3.9 to 3.12.** You can find the required plugins and instructions on how to install them in the
[plugins](plugins) directory.

## Getting Started

[//]: # (TODO: remove TestPyPI specifying)
You can install this library with:

`pip install -i https://test.pypi.org/simple/ gmat-py-simple`

Then in your Python scripts, import the library:

```python
import gmat_py_simple as gp
```

`gp` is the recommended abbreviation as is used throughout this
documentation.

### Specifying GMAT path

[//]: # (TODO: add link to instructions for specifying GMAT path)
For this library to be able to communicate with GMAT, you will also need to specify the path that GMAT is installed in.
You can do this either using an environment variable or in a configuration file.

[//]: # (TODO: add instructions for path specifying via environment variable or config file.)

## Examples

The [`examples`](examples) directory gives several example scripts that demonstrate the power of this library (and GMAT
generally). GMAT has several tutorials built-in, supplied in its `[GMAT root]/samples` folder. The scripts in
[`examples/tutorials`](examples/tutorials) have exactly the same functionality as these, but have been written using
this library rather than GMAT's standard Python API or its scripting language. Tutorials 1 to 4 are currently
implemented, with the rest planned to be added in future once the library has the required features.

[//]: # (TODO: update above paragraph once more tutorials implemented.)

[//]: # (<details> <summary><b>Pre-fix</b></summary>)

[//]: # ()

[//]: # (**On 19/4/25, NASA released [GMAT-R2025a]&#40;https://sourceforge.net/projects/gmat/&#41;. This wrapper was developed and tested)

[//]: # (with R2022a, so while I expect everything to still work, I cannot guarantee it. If you find any parts that don't work)

[//]: # (with R2025a, please raise an [issue]&#40;https://github.com/weasdown/GMAT-Python-simple/issues&#41;.**)

[//]: # ()

[//]: # (## Components implemented so far)

[//]: # ()

[//]: # (* Spacecraft - mostly complete: not all fields settable with from_dict&#40;&#41; but all settable with SetField&#40;&#41;)

[//]: # (    * Tanks - complete)

[//]: # (    * Thrusters - complete)

[//]: # (* ImpulsiveBurn - complete)

[//]: # (* Propagate command - mostly complete)

[//]: # (    * StopCondition - tested so far: ElapsedSecs, ElapsedDays, Apoapsis, Periapsis)

[//]: # ()

[//]: # (## WIP components)

[//]: # ()

[//]: # (* Maneuver command)

[//]: # (* FiniteBurn)

[//]: # ()

[//]: # (</details>)