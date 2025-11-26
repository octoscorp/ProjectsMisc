"""
For generating a script with the maximum number of Jinxes.
"""
import signal

from data import characters, jinxes

from datetime import datetime
from itertools import combinations


TOWN_DISTRIBUTION = {
    "townsfolk": 13,
    "outsiders": 4,
    "minions": 4,
    "demons": 4,
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
          to be present, but will not be used.)
        """
        # Create adjacency list
        self.adj_list = {}
        for char_name in jinx_dict.keys():
            for jinxed_char_name in jinx_dict[char_name].keys():
                dict_member_append(self.adj_list, char_name, jinxed_char_name)

    def is_jinxed_char(self, char_name):
        """Return bool of whether a jinx exists for char_name"""
        return self.adj_list.get(char_name) is not None

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

        # Sort alphabetically (half adjacency list)
        search_space = sorted(search_space)

        # For each remaining character, only check the characters after it in the list
        for i in range(len(search_space)):
            char_name = search_space[i]
            for j in range(i + 1, len(search_space)):
                jinxed_char_name = search_space[j]
                if jinxed_char_name in self.adj_list[char_name]:
                    count += 1
        return count


class Search:
    EXHAUSTION = 1
    EXHAUSTION_REDUCED = 2

    def __init__(self, search_type=EXHAUSTION):
        """Search type: One of Search.* enum, or a callable search func"""
        self.search_type = search_type

    def output_scripts(self, solutions):
        """
        TODO: Write to script file
        """
        print(solutions)

    def run(self):
        global start_time
        graph = _JinxGraph(jinxes)

        signal.signal(signal.SIGINT, sigint_handler)
        start_time = datetime.now()

        # Determine which search to run
        search_func = None
        match self.search_type:
            case Search.EXHAUSTION_REDUCED:
                search_func = self._reduced_space_exhaustion_search
            case Search.EXHAUSTION:
                search_func = self._exhaustion_search
            case _:
                search_func = self.search_type

        solutions = search_func(graph)

        elapsed_time = datetime.now() - start_time
        print(f"Took {elapsed_time} seconds to complete")

        self.output_scripts(solutions)

    def _get_reduced_search_space(self, graph):
        """Remove non-jinxed characters"""
        return {
            "townsfolk": [c for c in characters["townfolk"].keys() if graph.is_jinxed_char(c)],
            "outiders": [c for c in characters["outsiders"].keys() if graph.is_jinxed_char(c)],
            "minions": [c for c in characters["minions"].keys() if graph.is_jinxed_char(c)],
            "demons": [c for c in characters["demons"].keys() if graph.is_jinxed_char(c)],
        }

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
            for outsiders in combinations(search_space["outsiders"].keys(),
                                            TOWN_DISTRIBUTION["outsiders"]):
                for minions in combinations(search_space["minions"].keys(),
                                                TOWN_DISTRIBUTION["minions"]):
                    for demons in combinations(search_space["demons"].keys(),
                                                    TOWN_DISTRIBUTION["demons"]):
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
            for outsiders in combinations(space["outsiders"], TOWN_DISTRIBUTION["outsiders"]):
                for minions in combinations(space["minions"], TOWN_DISTRIBUTION["minions"]):
                    for demons in combinations(space["demons"], TOWN_DISTRIBUTION["demons"]):
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


def main():
    search = Search(Search.EXHAUSTION_REDUCED)
    search.run()


if __name__ == "__main__":
    main()
