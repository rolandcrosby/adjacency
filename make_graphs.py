import csv
import sys
import json
from typing import Dict, List, Tuple, Callable
from pprint import pp


def load_tuples(filename) -> List[Tuple]:
    with open(filename) as f:
        return [tuple(r) for r in csv.reader(f, delimiter="\t")]

adjacencies = load_tuples("deduped_graph.tsv")
counties_by_fips = {}
states = {}
for (name, fips) in load_tuples("counties.tsv"):
    comma = name.index(",")
    state = name[comma + 2 :]
    counties_by_fips[fips] = {"name": name[0:comma], "state": state}
    if state not in states:
        states[state] = {"county_ids": set(), "fips_prefix": fips[0:2]}
    states[state]["county_ids"].add(fips)

def make_state_adjacencies():
    adjacent_states = {}
    for (c1, c2) in adjacencies:
        s1, s2 =c1[0:2], c2[0:2]
        if s1 != s2:
            if c1 not in adjacent_states:
                adjacent_states[c1] = []
            if s2 not in adjacent_states[c1]:
                adjacent_states[c1].append(s2)
            if c2 not in adjacent_states:
                adjacent_states[c2] = []
            if s1 not in adjacent_states[c2]:
                adjacent_states[c2].append(s1)
    with open('adjacent_states.json', 'w') as f:
        json.dump(adjacent_states, f, indent=4)

def make_graph(
    filter_fn: Callable[[str, str], bool],
    filename: str,
    title: str = "adjacency",
    fmt: Callable[[str], str] = None,
):
    nodes = set()
    with open(filename, "w") as f:
        f.write("graph {} {{\n".format(title))
        for (c1, c2) in adjacencies:
            if filter_fn(c1, c2):
                f.write('  "{}" -- "{}";\n'.format(c1, c2))
                nodes.add(c1)
                nodes.add(c2)
        f.write("\n")
        for n in nodes:
            f.write('  "{}" [label="{}"];\n'.format(n, fmt(n)))
        f.write("}\n")

def make_state_graph(state: str):
    prefix = states[state]["fips_prefix"]
    filename = "graphs/graph-{}.dot".format(state)
    filter_fn = lambda c1, c2: c1.startswith(prefix) and c2.startswith(prefix)
    make_graph(filter_fn, filename, state, lambda n: counties_by_fips[n]["name"])

def make_interstate_graph():
    border_counties = set()
    for c1, c2 in adjacencies:
        if c1[0:2] != c2[0:2]:
            border_counties.add(c1)
            border_counties.add(c2)
    make_graph(
        lambda a, b: (a in border_counties or b in border_counties),
        "graphs/interstate.dot",
        "interestate",
        lambda n: "{}, {}".format(
            counties_by_fips[n]["name"], counties_by_fips[n]["state"]
        ),
    )

if __name__ == "__main__":
    make_state_adjacencies()
    if len(sys.argv) > 1:
        make_state_graph(sys.argv[1])
    else:
        for state in states:
            make_state_graph(state)
    make_interstate_graph()
