"""
For generating a script with the maximum number of Jinxes.
"""
import signal

from data import characters, jinxes

from datetime import datetime
from itertools import combinations
from copy import deepcopy


TOWN_DISTRIBUTION = {
    "townsfolk": 13,
    "outsider": 4,
    "minion": 4,
    "demon": 4,
}


start_time = 0
checked_solns = 0
last_soln = []
last_interrupt = datetime.now()


def dict_member_append(dictionary, key, value):
    """Append to a list which is a member of a dict. If it doesn't exist, create the list"""
    if dictionary.get(key) is None:
        dictionary[key] = []
    dictionary[key].append(value)


def transpose_dict(dictionary):
    output = {}
    for key, val in dictionary.items():
        dict_member_append(output, val, key)
    return output


def concat_lists(categorised):
    """Concatenate lists from categorised dict"""
    output = []
    for category in categorised.keys():
        output += categorised[category]
    return output


def sigint_handler(_signum, _frame):
    """Update on status. Should be SIGINFO, but no library support"""
    global last_interrupt
    curr_time = datetime.now()
    elapsed_time = curr_time - start_time
    print(f'SIGINT: checked {checked_solns} in {elapsed_time}s. Last seen:\n  {last_soln}')
    if (curr_time - last_interrupt).total_seconds() < 5:
        raise KeyboardInterrupt("")
    last_interrupt = curr_time


class _JinxGraph():
    def __init__(self, jinx_dict):
        """
        Create a new JinxGraph.
        @param jinx_dict dictionary of jinxes in format:
        {
            <char_name>: {
                <jinxed_char_name>: <jinx_description>,
                ...
            }, ...
        }
        NOTE: It is assumed that jinx_dict stores jinxes such that <char_name> is alphabetically
          before <jinxed_char_name>. Otherwise, get_num_jinxes will not work. This is because the
          adjacency list does not currently create reverse adjacencies. (The other order is allowed
          to be present, but may not be the only ordering.)
        """
        # Create adjacency list
        self.adj_list = {}
        self.total_edges = 0

        for char_name in jinx_dict.keys():
            for jinxed_char_name in jinx_dict[char_name].keys():
                dict_member_append(self.adj_list, char_name, jinxed_char_name)
                dict_member_append(self.adj_list, jinxed_char_name, char_name)
                self.total_edges += 1

        self.total_nodes = len(list(self.adj_list.keys()))

    def get_total_num_jinxes(self):
        return self._total_edges

    def get_num_jinxed_chars(self):
        return self.total_nodes

    def get_highest_num_jinxes(self):
        best = 0
        for char_name in self.adj_list.keys():
            current = len(self.adj_list[char_name])
            if current > best:
                best = current
        return best

    def get_degree(self, char_name):
        if self.adj_list.get(char_name) is None:
            return 0
        return len(self.adj_list[char_name])

    def get_num_jinxes(self, char_list):
        """
        Returns number of jinxes obtained by having the character set in play.
        Uses the fact that jinxes are stored under the character which is first alphabetically.
        """
        count = 0
        search_space = char_list[:]
        # Remove unjinxed characters
        for i in range(len(search_space) - 1, -1, -1):
            if self.adj_list.get(search_space[i]) is None:
                del search_space[i]

        # Sort alphabetically (expects that half of the adjacency list)
        search_space = sorted(search_space)

        # For each remaining character, only check the characters after it in the list
        for i in range(len(search_space)):
            char_name = search_space[i]
            for j in range(i + 1, len(search_space)):
                jinxed_char_name = search_space[j]
                if jinxed_char_name in self.adj_list[char_name]:
                    count += 1
        return count

    def get_num_jinxes_per_character(self, char_list):
        """
        Returns a dict of the count of jinxes which apply to the character when chars are
        limited to what is in char_list
        """
        counts = {char_name: 0 for char_name in char_list}
        search_space = char_list[:]
        # Remove unjinxed characters
        for i in range(len(search_space) - 1, -1, -1):
            if self.adj_list.get(search_space[i]) is None:
                del search_space[i]

        # Expects bidirectional adjacency list
        for char_name in search_space:
            for jinxed_char_name in self.adj_list[char_name]:
                if jinxed_char_name in search_space:
                    counts[char_name] += 1

        return counts


class Search:
    MANUAL = 0
    EXHAUSTION = 1
    EXHAUSTION_REDUCED = 2
    PEELING_GREEDY = 3
    CONSTRUCTION_GREEDY = 4
    CONSTRUCTION_GREEDY_ALL_STARTS = 5

    def __init__(self, search_type=EXHAUSTION):
        """Search type: One of Search.* enum, or a callable search func"""
        self.search_type = search_type

        self.types = {}
        for category in characters.keys():
            for char_name in characters[category].keys():
                self.types[char_name] = category

    def output_scripts(self, solutions, graph, skip_input=False):
        """
        TODO: Write to script file
        """
        solutions[0].sort()
        print(solutions[0])
        print(f"This has {graph.get_num_jinxes(solutions[0])} jinxes.")
        print()
        if not skip_input and ("y" == input(f"See all {len(solutions)} solutions? [y/N] ")):
            for i in range(1, len(solutions)):
                print(f"===== {graph.get_num_jinxes(solutions[i])} jinxes ====")
                solutions([i]).sort()
                print(solutions[i])
                print()

    def run(self):
        global start_time
        graph = _JinxGraph(jinxes)

        signal.signal(signal.SIGINT, sigint_handler)
        start_time = datetime.now()

        # Determine which search to run
        search_func = None
        match self.search_type:
            case Search.CONSTRUCTION_GREEDY_ALL_STARTS:
                search_func = self._greedy_construction_all_starts
            case Search.CONSTRUCTION_GREEDY:
                search_func = self._greedy_construction
            case Search.PEELING_GREEDY:
                search_func = self._greedy_peeling
            case Search.EXHAUSTION_REDUCED:
                search_func = self._reduced_space_exhaustion_search
            case Search.EXHAUSTION:
                search_func = self._exhaustion_search
            case Search.MANUAL:
                search_func = self._manual_answer
            case _:
                search_func = self.search_type

        solutions = search_func(graph)

        elapsed_time = datetime.now() - start_time
        print(f"Took {elapsed_time} seconds to complete")

        self.output_scripts(solutions, graph)

    def _get_reduced_search_space(self, graph):
        """Remove non-jinxed characters"""
        THRESHOLD = 0
        return {
            "townsfolk": [c for c in characters["townsfolk"].keys()
                          if graph.get_degree(c) >= THRESHOLD],
            "outsider": [c for c in characters["outsider"].keys()
                         if graph.get_degree(c) >= THRESHOLD],
            "minion": [c for c in characters["minion"].keys()
                       if graph.get_degree(c) >= THRESHOLD],
            "demon": [c for c in characters["demon"].keys()
                      if graph.get_degree(c) >= THRESHOLD],
        }

    def _get_reduced_counts(self, counts, char_name):
        """Remove char_name's contribution to categorised counts"""
        output = counts.copy()
        problem = False
        output[self.types[char_name]] -= 1
        if output[self.types[char_name]] < TOWN_DISTRIBUTION[self.types[char_name]]:
            problem = True
        return output, problem

    def _manual_answer(self, graph):
        """
        Return my manually-curated answer
        """
        return [[
            "mathematician",
            "king",
            "innkeeper",
            "monk",
            "exorcist",
            "soldier",
            "alchemist",
            "ravenkeeper",
            "sage",
            "banshee",
            "mayor",
            "magician",
            "poppygrower",
            "lunatic",
            "hatter",
            "plaguedoctor",
            "zealot",
            "spy",
            "marionette",
            "wraith",
            "summoner",
            "lilmonsta",
            "legion",
            "riot",
            "leviathan",
        ]]

    def _exhaustion_search(self, graph):
        """
        Naively check all combinations of characters.
        - Search space: 2.3281309e25 [69C13*23C4*27C4*19C4]
        - Complexity: O(n!) [of some complicated flavour]
        - Time estimate: 8,858,945,580,000 years [at 5 million checks/min]
        """
        global checked_solns, last_soln

        max_jinxes = 0
        optimal_solutions = []
        search_space = characters
        # Try every combination!
        for townsfolk in combinations(search_space["townsfolk"].keys(),
                                        TOWN_DISTRIBUTION["townsfolk"]):
            for outsiders in combinations(search_space["outsider"].keys(),
                                            TOWN_DISTRIBUTION["outsider"]):
                for minions in combinations(search_space["minion"].keys(),
                                                TOWN_DISTRIBUTION["minion"]):
                    for demons in combinations(search_space["demon"].keys(),
                                                    TOWN_DISTRIBUTION["demon"]):
                        chars = list(townsfolk + outsiders + minions + demons)
                        # The magic check
                        num_jinxes = graph.get_num_jinxes(chars)
                        if num_jinxes > max_jinxes:
                            max_jinxes = num_jinxes
                            optimal_solutions = []
                        if num_jinxes == max_jinxes:
                            optimal_solutions.append(chars)

                        # Update for SIGINFO
                        checked_solns += 1
                        last_soln = chars
        return optimal_solutions

    def _reduced_space_exhaustion_search(self, graph):
        """
        Exhaustion search with non-jinxed characters removed
        - Search space: 2.032366e18 [34C13*13C4*18C4*14C4]
        - Complexity: O(n!)
        - Time estimate: 773,350 years [at 5 million checks/min]
        """
        global checked_solns, last_soln

        max_jinxes = 0
        optimal_solutions = []

        # Remove non-jinxed characters
        space = self._get_reduced_search_space(graph)

        # Try every remaining combination
        for townsfolk in combinations(space["townsfolk"], TOWN_DISTRIBUTION["townsfolk"]):
            for outsiders in combinations(space["outsider"], TOWN_DISTRIBUTION["outsider"]):
                for minions in combinations(space["minion"], TOWN_DISTRIBUTION["minion"]):
                    for demons in combinations(space["demon"], TOWN_DISTRIBUTION["demon"]):
                        chars = list(townsfolk + outsiders + minions + demons)
                        # The magic check
                        num_jinxes = graph.get_num_jinxes(chars)
                        if num_jinxes > max_jinxes:
                            max_jinxes = num_jinxes
                            optimal_solutions = []
                        if num_jinxes == max_jinxes:
                            optimal_solutions.append(chars)

                        # Update for SIGINFO
                        checked_solns += 1
                        last_soln = chars
        return optimal_solutions

    def _greedy_peeling(self, graph):
        """
        Attempts to construct an optimal solution by removing the least-connected node at each
        chance.
        Complexity: O(n^2*d) [Getting jinxes per character, recursing on n-1]
        """
        max_jinxes = 0
        optimal_solutions = []

        # Remove non-jinxed characters
        space = self._get_reduced_search_space(graph)
        counts = {key: len(vals) for key, vals in space.items()}
        # Collapse to list
        space = concat_lists(space)

        def _greedy_peeling_recursive(graph, counts, space, depth):
            global checked_solns, last_soln
            # Base case
            correct_size = True
            for category in TOWN_DISTRIBUTION.keys():
                if counts[category] > TOWN_DISTRIBUTION[category]:
                    correct_size = False
            if correct_size:
                checked_solns += 1
                last_soln = space
                return [space]
            # Find lowest degree to remove
            jinx_counts = transpose_dict(graph.get_num_jinxes_per_character(space))

            # Try each character with lowest degree
            solutions = []
            for count in sorted(list(jinx_counts)):
                for removed_char in jinx_counts[count]:
                    altered_counts, count_invalid = self._get_reduced_counts(counts, removed_char)
                    if count_invalid:
                        continue
                    # Remove/append likely inefficient
                    space.remove(removed_char)
                    solutions += _greedy_peeling_recursive(graph, altered_counts, space, depth + 1)
                    space.append(removed_char)
                if len(solutions) > 0:
                    break
            return solutions

        solutions = _greedy_peeling_recursive(graph, counts, space, 0)
        for soln in solutions:
            num_jinxes = graph.get_num_jinxes(soln)
            if num_jinxes > max_jinxes:
                max_jinxes = num_jinxes
                optimal_solutions = []
            if num_jinxes == max_jinxes:
                optimal_solutions.append(soln)

        return optimal_solutions

    def _get_most_jinxes(self, graph, space, counts, current_chars):
        # Char(s) adding the most jinxes to the script
        most_added = 0
        best_chars = []
        for char in space:
            char_type = self.types[char]
            if counts[char_type] >= TOWN_DISTRIBUTION[char_type]:
                continue
            num = graph.get_num_jinxes(current_chars + [char])
            if num > most_added:
                most_added = num
                best_chars = []
            if num == most_added:
                best_chars.append(char)
        return best_chars

    def _get_most_potential_jinxes(self, graph, chars):
        # Char(s) with most potential jinxes
        most = 0
        best_chars = []
        for char in chars:
            deg = graph.get_degree(char)
            if deg > most:
                best_chars = []
                most = deg
            if deg == most:
                best_chars.append(char)
        return best_chars

    def _greedy_construction_recursive(self, graph, space, counts, current_chars, depth):
        global checked_solns, last_soln
        if depth > 100:
            print("Depth limit exceeded")
            return [current_chars]

        candidates = self._get_most_jinxes(graph, space, counts, current_chars)
        candidates = self._get_most_potential_jinxes(graph, candidates)
        if len(candidates) == 0:
            # This is also the base case
            last_soln = current_chars
            checked_solns += 1
            return [current_chars]

        best_val = 0
        solutions = []
        for cand in candidates:
            new_space = space[:]
            new_space.remove(cand)
            new_counts = deepcopy(counts)
            new_counts[self.types[cand]] += 1
            new_chars = current_chars[:]
            new_chars.append(cand)

            subsolutions = self._greedy_construction_recursive(graph, new_space, new_counts,
                                                               new_chars, depth + 1)

            for soln in subsolutions:
                found_jinxes = graph.get_num_jinxes(soln)
                if found_jinxes > best_val:
                    solutions = []
                    best_val = found_jinxes
                if found_jinxes == best_val:
                    solutions.append(soln)

        return solutions

    def _greedy_construction(self, graph):
        """
        Attempts to construct an optimal solution by adding the character which adds most jinxes.
        Ties are resolved by adding character with most potential jinxes. If there's still a tie,
        splits into sub-searches.
        """
        # Remove non-jinxed characters
        space = self._get_reduced_search_space(graph)
        counts = {key: 0 for key in TOWN_DISTRIBUTION.keys()}
        # Collapse to list
        space = concat_lists(space)

        current_chars = []
        return self._greedy_construction_recursive(graph, space, counts, current_chars, 0)

    def _greedy_construction_all_starts(self, graph):
        """
        Attempt to dodge local optima by starting at any given character
        """
        # Remove non-jinxed characters
        space = self._get_reduced_search_space(graph)
        counts = {key: 0 for key in TOWN_DISTRIBUTION.keys()}
        # Collapse to list
        space = concat_lists(space)

        max_jinxes = 0
        optimal = []

        for char in space:
            # Seed start point
            current_chars = [char]
            given_space = space[:]
            given_space.remove(char)
            given_counts = deepcopy(counts)
            given_counts[self.types[char]] += 1

            char_solns = self._greedy_construction_recursive(graph, given_space, given_counts,
                                                             current_chars, 0)

            # Num jinxes is same for all returned
            char_max = graph.get_num_jinxes(char_solns[0])
            if char_max > max_jinxes:
                max_jinxes = char_max
                optimal = []
            if char_max == max_jinxes:
                optimal += char_solns
                self.output_scripts(optimal, graph, True)

        return optimal


def main():
    search = Search(Search.CONSTRUCTION_GREEDY_ALL_STARTS)
    search.run()


if __name__ == "__main__":
    main()
