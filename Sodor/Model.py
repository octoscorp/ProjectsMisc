"""
A file which works on an undirected weighted graph
representing rail track on the Island of Sodor.

Goal: "I'm heading to here from here" - how many kilometres, how much fuel - how many stops?
Author: G Hampton
Last Edited: 26/07/23
"""
from math import inf
from collections import namedtuple, deque
from heapq import heappush, heappop

Position = namedtuple('Position', 'x y')

AVERAGE_TRACK_LENGTH = 5.05
COLOURS = {
    'blue': '#16b7f2',
    'green': '#04d435',
    'red': '#e8462a',
    'brown': '#9c6e4b',
}

class Node:
    def __init__(self, id, name, position):
        """ Takes position as an (x, y) tuple. id doubles as list index """
        self.id = id
        self.name = name
        self.position = position

    def __str__(self):
        return self.name

class PriorityQueue:
    def __init__(self):
        """ This one starts off empty. Sorry, nothing fancy here """
        self.contents = []
        self.count = 0
    
    def push(self, task, priority=0):
        """ I really don't need to explain this """
        entry = (priority, self.count, task)
        heappush(self.contents, entry)
        self.count += 1
    
    def pop(self):
        priority, _, task = heappop(self.contents)
        if self.empty():
            self.count = 0  # Not that I'm overly worried about overflowing number counters, but better safe than sorry
        return (task, priority)

    def empty(self):
        return len(self.contents) == 0

class Model:
    def __init__(self, node_file, edge_file):
        self.nodes = []
        self.adj_list = {}
        self.create_nodes(node_file)
        self.create_edges(edge_file)

    def create_nodes(self, filename):
        """ Create nodes from a given file. This expects the file to have each
         node on its own line, in the format <id>, <name>, <x>, <y> 
         where id is an integer starting at 0 and listed in increasing order
         within the file"""
        # Load lines in
        lines = get_lines_of_file(filename)

        # Process lines
        for id, name, x, y in [line.split(', ') for line in lines]:
            self.nodes.append(Node(int(id), name, Position(int(x), int(y))))

    def create_edges(self, filename):
        """ Create edges from a given file. This expects the file to have each
         edge on its own line, in the format
         <node_1_id>, <node_2_id>, <weight> """
        # Load lines in
        lines = get_lines_of_file(filename)

        self.track_thicknesses = {}

        # Process lines
        for node_1_str, node_2_str, weight_str, num_tracks in [line.split(', ') for line in lines]:
            node_1 = int(node_1_str)
            node_2 = int(node_2_str)
            weight = float(weight_str)
            # Validate input
            assert len(self.nodes) > max(node_1, node_2)
            if node_1 not in self.adj_list:
                self.adj_list[node_1] = []
            if node_2 not in self.adj_list:
                self.adj_list[node_2] = []
            self.adj_list[node_1].append((node_2, weight))
            self.adj_list[node_2].append((node_1, weight))
            self.track_thicknesses[(node_1, node_2)] = num_tracks
    
    def add_edge(self, n_1, n_2, weight):
        node_1 = self.nodes.index(n_1)
        node_2 = self.nodes.index(n_2)
        self.adj_list[node_1].append((node_2, weight))
        self.adj_list[node_2].append((node_1, weight))
    
    def remove_edge(self, n_1, n_2, weight):
        node_1 = self.nodes.index(n_1)
        node_2 = self.nodes.index(n_2)
        self.adj_list[node_1].remove((node_2, weight))
        self.adj_list[node_2].remove((node_1, weight))
    
    def get_all_edges(self):
        """ Don't do this repeatedly, it's not that necessary """
        edges = []
        for node_1, adjacencies in self.adj_list.items():
            for (node_2, weight) in adjacencies:
                if (self.nodes[node_2], self.nodes[node_1], weight) not in edges:
                    edges.append((self.nodes[node_1], self.nodes[node_2], weight))
        return edges

    def paths_to_node(self, start_node, end_node):
        """ Get all paths between the two nodes. """
        # Start with end node
        # Talk to neighbours
        # Update their paths with yours
        # Add them to the queue

        paths = {end_node: [[]]}
        visited = []
        queue = deque([end_node])
        while len(queue) > 0:
            current = queue.popleft()
            visited.append(current)
            if current != start_node:
                for (neighbour, weight) in self.adj_list[current]:
                    # all combinations from current
                    neighbour_updated = False
                    for path in paths[current]:
                        if neighbour not in path:
                            path_for_neighbour = path + [current]
                            if len(path_for_neighbour) > 30:
                                break
                            if neighbour not in paths:
                                paths[neighbour] = [path_for_neighbour]
                                neighbour_updated = True
                            elif path_for_neighbour not in paths[neighbour]:
                                paths[neighbour] += [path_for_neighbour]
                                neighbour_updated = True
                    if neighbour_updated or (neighbour not in visited and neighbour not in queue):
                        queue.append(neighbour)
        try:
            return paths[start_node]
        except KeyError:
            return []
    
    def shortest_path_between(self, node_1, node_2):
        """ An implementation of djikstra's algorithm using heapq to create a priority queue.
         It sounds more impressive than it is, I've just done this a bunch in class (this is at least my third time doing it) """
        D = [inf] * len(self.nodes)
        D[node_2] = 0
        visited = []
        paths = {node_2: []}

        pq = PriorityQueue()
        pq.push(node_2)     # Default priority is 0

        while not pq.empty():
            (current, _) = pq.pop()
            visited.append(current)

            for (neighbour, weight) in self.adj_list[current]:
                if neighbour not in visited:
                    new_cost = D[current] + weight
                    if new_cost < D[neighbour]:
                        paths[neighbour] = paths[current] + [current]
                        pq.push(neighbour, new_cost)
                        D[neighbour] = new_cost
        try:
            paths[node_1].reverse()
            return paths[node_1]
        except KeyError:
            return []

    def edge_length(self, node_1, node_2):
        """ Get the distance between the two nodes. If they are not adjacent, return inf """
        for (node, weight) in self.adj_list[node_1]:
            if node == node_2:
                return weight
        return inf
    
    def passing_possible(self, node_1, node_2):
        """ Returns a boolean value of whether trains can pass each other on the specified track """
        if (node_1, node_2) in self.track_thicknesses.keys():
            return self.track_thicknesses[(node_1, node_2)] > 1
        return self.track_thicknesses[(node_2, node_1)] > 1

class Train:
    def __init__(self, init_list, out_of_range):
        self.number = init_list[0]
        self.name = init_list[1]
        self.colour = COLOURS[init_list[2]]
        self.speed = float(init_list[3])
        self.home_station = int(init_list[4])
        self.last_station = int(init_list[4])

        self.distance_from_last_station = 0
        self.max_range = float(init_list[5])
        self.remaining_range = float(init_list[5])
        self.facing = None
        self.played = False

        self.out_of_range = out_of_range
    
    def get_usual_distance(self):
        return self.speed * AVERAGE_TRACK_LENGTH

    def move(self, stuck_behind=[]):
        """
         Move the train in the direction it is facing according to its speed 
         :param stuck_behind: a list of tuples of (distance, top_speed)
         :param callback: a function to update the distances
        """
        assert self.facing is not None

        distance_travelled = 0
        time_stuck = 0

        # Accomodate for any time spent stuck behind a slower train
        if len(stuck_behind) > 0:
            for distance, top_speed in stuck_behind:
                duration = distance / (top_speed * AVERAGE_TRACK_LENGTH)
                if time_stuck + duration <= 1:
                    # If less than an hour
                    distance_travelled += distance
                    time_stuck += duration
                else:
                    # Stuck behind at end of hour
                    duration = 1 - time_stuck
                    covered_distance = duration * (top_speed * AVERAGE_TRACK_LENGTH)

                    distance_travelled += covered_distance
                    time_stuck = 1
                    break
        if time_stuck < 1:
            duration = 1 - time_stuck
            
            distance_travelled += duration * (self.speed * AVERAGE_TRACK_LENGTH)

        # Add the distance travelled
        self.distance_from_last_station += distance_travelled

    def visit_station(self, station_id, distance):
        """ Set the train's location to the given station (removes its facing) """
        self.last_station = station_id
        self.distance_from_last_station = 0
        self.facing = None
        self.remaining_range -= distance
    
    def pass_station(self, station_id, distance):
        """ Set the train's last station passed to this (removes its facing) """
        self.last_station = station_id
        self.distance_from_last_station -= distance
        self.facing = None
        self.remaining_range -= distance

def get_lines_of_file(filename):
    """ A utility function which returns a list of the file's lines """
    src_file = open(filename, "r")
    lines = [line.rstrip() for line in src_file.readlines()]
    src_file.close()
    return lines

def test():
    """ Test the graph's construction """
    g = Model("./data/stations.txt", "./data/tracks.txt")

    # Check that adjacency list is working as expected
    assert g.edge_length(53, 57) == 57.0
    assert g.edge_length(0, 48) == 4.5
    assert g.edge_length(0, 1) == inf

    # Check all-edge retrieval
    assert len(g.get_all_edges()) == 95   # No less than 1 per edge

    # Check that path generation works
    assert len(g.paths_to_node(14, 15)) == 1
    assert len(g.paths_to_node(0, 48)) < 50

    # Check djikstra
    assert len(g.shortest_path_between(48, 0)) == 1
    assert len(g.shortest_path_between(0, 1)) != 1

    # The average edge length (excluding the express route)
    assert round(((sum([edge[2] for edge in g.get_all_edges()])-57)/94), 2) == AVERAGE_TRACK_LENGTH

    # Let user know of our success!
    print("All tests passed with flying scotsman!")

# Only run tests if this is not imported
if __name__ == "__main__":
    test()