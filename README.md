# GMAT-Python-simple
An extra wrapper for the GMAT Python API to simplify setting up mission simulations. The wrapper aims to align Python commands with GMAT script ones, greatly reducing the number of lines required to model a mission. To do this, it automatically creates relevant subclasses and sets default values, while still allowing the user full control over parameters if they need something specific. The aim is to reduce the time that the user needs to spend thinking about how the API works, so they can instead focus on the orbital mechanics and broader design of their particular mission.

Due to the wrapper's extensive use of classes and methods rather than strings, it also supports full code completion. It has been designed to be as intuitive as possible for the user, while still closely matching GMAT's design philosophy.

## Examples
To demonstrate the wrapper, tutorials will be added to the [examples](https://github.com/weasdown/GMAT-Python-simple/tree/main/examples)/[tutorials](https://github.com/weasdown/GMAT-Python-simple/tree/main/examples/tutorials) directory as the required feature level is reached. These tutorials will match those distributed with GMAT by default (in the \[GMAT root]/samples folder) and will demonstrate the power of the wrapper to create missions using very little code.

## Components implemented so far
* Spacecraft - mostly complete: not all fields settable with from_dict() but all settable with SetField()
  * Tanks - complete
  * Thrusters - complete
* ImpulsiveBurn - complete
* Propagate command - mostly complete
  * StopCondition - tested so far: ElapsedSecs, ElapsedDays, Apoapsis, Periapsis

## WIP components
* Maneuver command
* FiniteBurn
