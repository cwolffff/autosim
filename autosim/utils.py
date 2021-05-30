def get_tree_data(tree_setup, position):
    assert position in ["OOP", "IP"]
    with open(tree_setup, "r") as f:
        lines = f.readlines()
    pot_size = _get_pot_size(lines)
    flop_sizes = _get_flop_sizes(lines, position)
    return {"pot_size": pot_size, "flop_sizes": flop_sizes}


def _get_pot_size(lines):
    relevant_lines = [line for line in lines if line.startswith("set_pot")]
    assert (
        len(relevant_lines) == 1
    ), "Tree setup script should call set_pot exactly once."
    line = relevant_lines[0]
    parts = line.split(" ")
    pot_size = int(parts[3])
    return pot_size


def _get_flop_sizes(lines, position):
    sizes = set()
    setup_lines = [line for line in lines if line.startswith("add_line")]
    for line in setup_lines:
        parts = line.split(" ")
        if position == "IP" and int(parts[1]) != 0:  # donk bet
            continue
        cbet = int(parts[1]) if position == "OOP" else int(parts[2])
        sizes.add(cbet)
    sizes = sizes - {0}
    return sorted(list(sizes))
