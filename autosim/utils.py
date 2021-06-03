import csv
import os


DATAHEADER = ["strategy", "ev", "exploitability", "fname"]


def get_tree_data(tree_setup, position):
    assert position in ["OOP", "IP"]
    with open(tree_setup, "r") as f:
        lines = f.readlines()
    return {
        "pot_size": _get_pot_size(lines),
        "flop_sizes": _get_flop_sizes_chips(lines, position),
        "flop_sizes_perc": _get_flop_sizes_perc(lines, position),
    }


def _get_pot_size(lines):
    relevant_lines = [line for line in lines if line.startswith("set_pot")]
    assert (
        len(relevant_lines) == 1
    ), "Tree setup script should call set_pot exactly once."
    line = relevant_lines[0]
    parts = line.split(" ")
    pot_size = int(parts[3])
    return pot_size


def _get_flop_sizes_chips(lines, position):
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


def _get_flop_sizes_perc(lines, position):
    relevant_lines = [line for line in lines if f"FlopConfig{position}.BetSize" in line]
    assert (
        len(relevant_lines) == 1
    ), f"Tree setup script should have a line specifying FlopConfig{position}.BetSize"
    line = relevant_lines[0]
    sizes = line.split("#")[2][:-1].split(",")
    return sizes


def write_datafile_header(path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DATAHEADER)
        writer.writeheader()


def write_results(path, strategy, results, position, fname):
    assert position in ["OOP", "IP"]
    row = {
        "strategy": strategy,
        "ev": results["ev_oop"] if position == "OOP" else results["ev_ip"],
        "exploitability": results["exploitability"],
        "fname": fname,
    }
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DATAHEADER)
        writer.writerow(row)


def load_boards(path):
    with open(path, "r") as f:
        lines = f.readlines()
    lines = [line.split(":")[0] for line in lines]
    return lines
