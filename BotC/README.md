# Blood on the Clocktower tools

The only use cases I currently have are trivial.
1. Creating a script with the maximum number of jinxes. For this, I have a handful of necessary requirements:
  * Parse character data, including:
    * Character name
    * Character type [Townsfolk/Outsider/Minion/Demon] (for maintaining a legal count of each)
    * Jinxes
  * Construct a graph representation of Jinxes
  * Identify which variations to the base Ravenswood Bluff count (13/4/4/4) are acceptable.
  * Identify the maximum number of jinxes possible on a script and the associated characters.
  * Optional extras:
    * Output in JSON format for the script tool

2. Determine night order ranking for all characters. For this:
  * Output in YAML format to save in this repository
  * Parse character names