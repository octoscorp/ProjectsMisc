from abc import ABC, abstractmethod     # Abstract classes

class WaveFunctionCollapsible:
    """To be turned into An abstract class, which all objects using WaveFunctionCollapseManager should extend"""
    # Example also defined add_neighbour, getNeighbour, getDirections, getPossibilities

    def __init__(self):
        # All possibilities
        # Entropy = len(possibilities)
        # Neighbours = dict()
        pass
    
    def collapse(self):
        # Get weights of possibilities (ex: defined in a dictionary)
        # Choose a possibility (ex: random.choices(self.possibilities, weights=weights, k=1))
        # Set entropy to 0
        pass

    def constrain(self):
        # if entropy > 0:
        # Create empty list
        # Add all edges (relevant) edges of possibilities of the tile which has called this.
        # Grab the opposite of the direction (ex did this with 4 if statements, a lookup would be faster)

        # Loop over the possibilities for this tile
        # If the opposite side of this possibility cannot connect to any, we remove it and set a flag
        # EOL

        # Update entropy
        # Return boolean of whether any were removed
        pass

class WFCManager:
    """A class for applying the wave function collapse algorithm to a set of objects"""
    def __init__(self):
        pass
    
    def wave_function_collapse(self):
        # Get list of tiles with lowest entropy
        # If list is empty, return 0
        # Choose the tile to collapse, and collapse it
        # Push it onto a stack

        # While the stack is not empty:
        # Pop from stack
        # Get all possibilities for that tile
        # Get directions from tile

        # For each direction:
        # get neighbour in that direction
        # If the neighbour's entropy != 0 (this is the check whether it has been collapsed)
        # Constrain the neighbour and fetch a boolean of whether it was reduced
        # If it was reduced, push it onto the stack
        # EOL

        # EOL

        # Return 1
        pass