"""
The Controller module of the SODOR project

Goal: "I'm heading to here from here" - how many kilometres, how much fuel - how many stops?

Remaining:
- Train data tracking
- Time stepping (train shows last station)
- Overtaking based on lines

Author: G Hampton
Last Edited: 25/07/23
"""
from Model import Model, Train
from View import View

class Controller:
    # Setup
    def __init__(self):
        self.model = Model("./data/stations.txt", "./data/tracks.txt")
        self.edge_list = self.model.get_all_edges()
        self.edge_map = {}
        self.trains = []
        self.awaiting_answer = False

        self._get_trains()
        self.view = View(self, self.model.nodes, self.edge_list)
    
    def _get_trains(self):
        f = open("./data/trains.txt", "r")
        lines = [line.rstrip() for line in f.readlines()]
        f.close()
        for line in lines:
            train = Train(line.split(','), self.run_out)
            self.trains.append(train)

    def start_gui(self):
        self.view.start()
    
    # Actions
    def find_edge_index_from_nodes(self, node_1, node_2):
        """ Use some dynamic programming (big air quotes) """
        goal = (self.model.nodes[node_1], self.model.nodes[node_2])
        if goal in self.edge_map:
            return self.edge_map[goal]
        i = 0
        for (n1, n2, w) in self.edge_list:
            if n1 in goal and n2 in goal:
                self.edge_map[goal] = i
                return i
            i += 1
        raise KeyError
    
    def get_train_by_name(self, name):
        for train in self.trains:
            if train.name == name:
                return train
        return None
    
    def get_train_names(self):
        return [train.name for train in self.trains]
    
    def get_active_trains(self):
        return [train for train in self.trains if train.played]
    
    def step(self, error_callback):
        """ Step forward by one time increment. ONLY call in a new thread. """
        # Check all trains have a facing set
        trains = self.get_active_trains()
        error_callback("-")
        for train in trains:
            if train.facing is None:
                error_callback("Not all trains have directions")
                return None
        trains.sort(key=lambda x: x.speed)

        # Identify stuck/pass trains
        events = []
        stuck_lists, pass_times = self.identify_stuck_pass(trains)
        for passing in pass_times:
            events.append((passing[0], "TRAIN", self.trains.index(passing[1]), self.trains.index(passing[2])))

        # Move trains (slowest first)
        for i in range(len(trains)):
            trains[i].move(stuck_lists[i])
            to_next_station = self.model.edge_length(trains[i].last_station, trains[i].facing)
            if trains[i].distance_from_last_station > to_next_station:
                time_of_passing = to_next_station / trains[i].get_usual_distance()
                events.append((time_of_passing, "STATION", self.trains.index(trains[i]), trains[i].facing))
        
        events.sort(key=lambda x: x[0])
        return events
            
    def identify_stuck_pass(self, active_trains):
        """ Identify which trains are stuck and for what distance """
        stuck_lists = [[] * len(active_trains)]
        pass_times = []
        return stuck_lists, pass_times
    
    def get_adjacent_nodes(self, station):
        return [stat[0] for stat in self.model.adj_list[station]]

    # Callbacks
    def train_pass_station(self, train, station, stop):
        """ Set whether a train stops at a station based on the parameter stop """
        if stop:
            self.trains[train].visit_station(station)
        else:
            dist = self.model.edge_length(self.trains[train].last_station, station)
            self.trains[train].pass_station(station, dist)
    
    # def set_train_facing(self, train, station):
    #     self.trains[train].facing = station
    
    def run_out(self, train):
        """ When a train has run out of coal/water """
        pass

    def all_paths_between(self, node_1, node_2, path_receiver):
        paths = self.model.paths_to_node(node_1, node_2)
        indexed_paths = []
        # Need to enumerate 
        for path in paths:
            path.reverse()
            prev_node = node_1
            ind_path = []
            for curr_node in path:
                ind_path.append(self.find_edge_index_from_nodes(prev_node, curr_node))
                prev_node = curr_node
            indexed_paths.append(ind_path)
        path_receiver(indexed_paths)
    
    def shortest_path_between(self, node_1, node_2, path_receiver):
        path = self.model.shortest_path_between(node_1, node_2)
        prev_node = node_1
        ind_path = []
        for curr_node in path:
            ind_path.append(self.find_edge_index_from_nodes(prev_node, curr_node))
            prev_node = curr_node
        path_receiver([ind_path])
    
    def deactivate_track(self, track_id, callback):
        node_1, node_2, weight = self.edge_list[track_id]
        self.model.remove_edge(node_1, node_2, weight)
        callback(track_id)
    
    def activate_track(self, track_id, callback):
        node_1, node_2, weight = self.edge_list[track_id]
        self.model.add_edge(node_1, node_2, weight)
        callback(track_id)
    
    def crane_puzzle_numbers(self, start_point, rotation_left, rotation_right, callback):
        """ Calculates the GCD and minimum number of steps using Extended Euclidean Algorithm """
        goal, steps_left, steps_right = extended_euclidean(rotation_left, rotation_right)

        # Process the result
        if steps_left > 0:
            goal -= start_point
        else:
            goal += start_point
        steps_left = abs(steps_left)
        steps_right = abs(steps_right)
        goal %= 360

        description = f'Starting at {start_point}, reaching {goal} requires {steps_left} step(s) of {rotation_left} ' + \
                      f'degrees anti-clockwise and {steps_right} step(s) of {rotation_right} degrees clockwise.'
        callback(description)

def extended_euclidean(a, b):
    """
    Performs extended euclidean algorithm and 
    returns the gcd and the coefficients of Bézout's identity
    """
    if a == 0:
        return b, 0, 1
    gcd, s, t = extended_euclidean(b%a, a)
    return gcd, t - (b//a) * s, s

def main():
    c = Controller()
    c.start_gui()

def test():
    assert extended_euclidean(25,10) == (5, 1, -2)
    assert extended_euclidean(10,25) == (5, -2, 1)
    assert extended_euclidean(35,7) == (7, 0, 1)
    assert extended_euclidean(300,90) == (30, 1, -3)
    assert extended_euclidean(300,200) == (100, 1, -1)

    print("Tests pass")

if __name__ == "__main__":
    # test()
    main()