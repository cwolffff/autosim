import csv
import os

import utils
from solver import Solver


EXEPATH = "C:/PioSOLVER/PioSOLVER2-pro.exe"
ROOTDIR = "C:/Users/christopher/Documents/autosim"


def solve_full_tree(
    tree_setup, position, board, outdir, datapath, outname="full", timeout=None
):
    solver = Solver(EXEPATH)
    solver.wait_for_ready()
    solver.set_board(BOARD)
    solver.run_script(tree_setup)
    solver.build_tree()
    solver.go(timeout)
    solver.dump_tree(f"{outdir}/{outname}.cfr")
    results = solver.calc_results()
    utils.write_results(datapath, strategy=f"full", results=results, position=position)
    solver.exit()


def solve_flop_lines(
    tree_setup, bet_sizes, position, board, outdir, datapath, timeout=None
):
    # TODO: parallelize
    for size in bet_sizes:
        solver = Solver(EXEPATH)
        solver.wait_for_ready()
        solver.set_board(BOARD)
        solver.run_script(tree_setup)
        to_remove = [s for s in bet_sizes if s != size]
        for s in to_remove:
            bet_line = f"{s}" if position == "OOP" else f"0 {s}"
            solver.remove_line(bet_line)
            solver.add_info_line(f"#FlopConfig{POSITION}.BetSize#{size}")
        solver.build_tree()
        solver.go(timeout)
        solver.dump_tree(f"{outdir}/flop_{size}.cfr")
        results = solver.calc_results()
        utils.write_results(
            datapath, strategy=f"b{size}", results=results, position=position
        )
        solver.exit()


def analyze_flop():
    pass


if __name__ == "__main__":
    SPOT = "3b_CO_BTN"
    POSITION = "IP"
    BOARD = "As5h3d"
    OUTDIR = f"{ROOTDIR}/out/{SPOT}/{BOARD}"
    TREE_SETUP = f"{ROOTDIR}/data/3b_IP_big.txt"
    DATAPATH = f"{OUTDIR}/data.csv"
    TIMEOUT = None

    os.makedirs(OUTDIR, exist_ok=True)
    utils.write_datafile_header(DATAPATH)

    tree_data = utils.get_tree_data(TREE_SETUP, POSITION)
    solve_full_tree(
        tree_setup=TREE_SETUP,
        position=POSITION,
        board=BOARD,
        outdir=OUTDIR,
        outname="full",
        datapath=DATAPATH,
        timeout=TIMEOUT,
    )
    solve_flop_lines(
        tree_setup=TREE_SETUP,
        bet_sizes=tree_data["flop_sizes"],
        position=POSITION,
        board=BOARD,
        outdir=OUTDIR,
        datapath=DATAPATH,
        timeout=TIMEOUT,
    )
    analyze_flop()
