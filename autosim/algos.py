import csv
import logging
import os
from functools import partial
from joblib import Parallel, delayed

import utils
from solver import Solver


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def solve(
    spot: str,
    tree_setup: str,
    position: str,
    boards: list,
    rootdir: str,
    exepath: str,
    timeout: int,
    n_jobs: int = 2,
):
    """
    Run the simplification algorithm for a list of boards.

    Args:
        spot: The name of the spot. This will be the name of the output directory.
        tree_setup: A path to a PIO script for setting up the tree. This script should
            set the desired accuracy, set preflop ranges, set stack and pot sizes, add
            the lines for the game tree, and add information about the game tree. See
            the data/ folder for examples.
        position: "OOP" or "IP".
        boards: A list of boards to run. E.g. ["As5h3s", "Ks7s4h", "Qs5h2s"].
        rootdir: The root directory of this package.
        exepath: An absolute path to a PIO 2.0 executable.
        timeout: The maximum amount of time to spend on each board. If None, this solves
            until the desired accuracy is reached.

    """
    tree_data = utils.get_tree_data(tree_setup, position)
    solve_board_ = partial(
        solve_board,
        spot=spot,
        tree_setup=tree_setup,
        tree_data=tree_data,
        position=position,
        rootdir=rootdir,
        exepath=exepath,
        timeout=timeout,
    )
    Parallel(n_jobs=n_jobs)(delayed(solve_board_)(board) for board in boards)


def solve_board(
    board: str,
    spot: str,
    tree_setup: str,
    tree_data: dict,
    position: str,
    rootdir: str,
    exepath: str,
    timeout: int,
):
    outdir = f"{rootdir}/out/sims/{spot}/{board}"
    datapath = f"{outdir}/data.csv"
    os.makedirs(outdir, exist_ok=True)
    utils.write_datafile_header(datapath)
    solve_full_tree(
        tree_setup=tree_setup,
        position=position,
        board=board,
        outdir=outdir,
        outname="full",
        datapath=datapath,
        exepath=exepath,
        timeout=timeout,
    )
    solve_flop_lines(
        tree_setup=tree_setup,
        tree_data=tree_data,
        position=position,
        board=board,
        outdir=outdir,
        datapath=datapath,
        exepath=exepath,
        timeout=timeout,
    )


def solve_full_tree(
    tree_setup, position, board, outdir, datapath, exepath, outname="full", timeout=None
):
    """
    Solve a single tree.
    """
    # logger.info(f"Started running full tree for board {board}...")
    print(f"Started running full tree for board {board}...")
    solver = Solver(exepath)
    solver.wait_for_ready()
    solver.set_board(board)
    solver.run_script(tree_setup)
    solver.build_tree()
    solver.go(timeout)
    solver.dump_tree(f"{outdir}/{outname}.cfr")
    results = solver.calc_results()
    utils.write_results(
        datapath,
        strategy=f"full",
        results=results,
        position=position,
        fname=f"{outname}.cfr",
    )
    solver.exit()
    # logger.info(f"Finished running full tree for board {board}.")
    print(f"Finished running full tree for board {board}.")


def solve_flop_lines(
    tree_setup, tree_data, position, board, outdir, datapath, exepath, timeout=None
):
    """
    Solve all variants of a big tree where the flop strategy of {position} is replaced
    by a single bet size. E.g. if the original tree setup contains b30, b75, and b150
    options, this method would run 3 sims.
    """
    bet_sizes = tree_data["flop_sizes"]
    for size in bet_sizes:
        perc = int(size / tree_data["pot_size"] * 100)
        # logger.info(f"Started running strategy b{perc} for board {board}...")
        print(f"Started running strategy b{perc} for board {board}...")
        solver = Solver(exepath)
        solver.wait_for_ready()
        solver.set_board(board)
        solver.run_script(tree_setup)
        to_remove = [s for s in bet_sizes if s != size]
        for s in to_remove:
            bet_line = f"{s}" if position == "OOP" else f"0 {s}"
            solver.remove_line(bet_line)
            # TODO: Implement this correctly. Account for all-in bets.
            # perc = int(size / pot_size)
            # solver.add_info_line(f"#FlopConfig{POSITION}.BetSize#{perc}")
        solver.build_tree()
        solver.go(timeout)
        solver.dump_tree(f"{outdir}/flop{size}.cfr")
        results = solver.calc_results()
        utils.write_results(
            datapath,
            strategy=f"{size}",
            results=results,
            position=position,
            fname=f"flop{size}.cfr",
        )
        solver.exit()
        # logger.info(f"Finished running strategy b{perc} for board {board}.")
        print(f"Finished running strategy b{perc} for board {board}.")


if __name__ == "__main__":
    ROOTDIR = "C:/Users/christopher/Documents/autosim"
    SPOT = "3b_CO_BTN_mk2"
    # TODO: log inputs/settings, maybe in solve
    solve(
        spot=SPOT,
        tree_setup=f"{ROOTDIR}/data/3b_CO_BTN.txt",
        position="IP",
        boards=utils.load_boards(
            "C:/PioSOLVER/preflop_subsets/PioSOLVER_2016_24_flops.txt"
        ),
        rootdir=ROOTDIR,
        exepath="C:/PioSOLVER/PioSOLVER2-pro.exe",
        timeout=None,
    )
