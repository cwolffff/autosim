import os

import utils
from solver import Solver


EXEPATH = "C:/PioSOLVER/PioSOLVER2-pro.exe"
ROOTDIR = "C:/Users/christopher/Documents/autosim"


def solve_full_tree(tree_setup, board, outdir, outname="full.cfr", timeout=600):
    solver = Solver(EXEPATH)
    solver.wait_for_ready()
    solver.set_board(BOARD)
    solver.run_script(tree_setup)
    solver.build_tree()
    solver.go(timeout)
    solver.dump_tree(f"{outdir}/{outname}")
    solver.exit()


def solve_flop_lines(tree_setup, bet_sizes, position, board, outdir, timeout=600):
    # TODO: parallelize
    for size in bet_sizes:
        solver = Solver(EXEPATH)
        solver.wait_for_ready()
        solver.set_board(BOARD)
        solver.run_script(tree_setup)
        to_remove = [s for s in bet_sizes if s != size]
        for s in to_remove:
            cmd = f"remove_line {s}" if position == "OOP" else f"remove_line 0 {s}"
            solver.run(cmd)
            solver.add_info_line(f"#FlopConfig{POSITION}.BetSize#{size}")
        solver.build_tree()
        solver.go(timeout)
        solver.dump_tree(f"{outdir}/flop{size}.cfr")
        solver.exit()


if __name__ == "__main__":
    SPOT = "test"
    POSITION = "IP"
    BOARD = "As5h3d"
    OUTDIR = f"{ROOTDIR}/out/{SPOT}/{BOARD}"
    TREE_SETUP = f"{ROOTDIR}/data/test.txt"

    os.makedirs(OUTDIR, exist_ok=True)

    tree_data = utils.get_tree_data(TREE_SETUP, POSITION)
    solve_full_tree(
        tree_setup=TREE_SETUP,
        board=BOARD,
        outdir=OUTDIR,
        outname="full.cfr",
        timeout=600,
    )
    solve_flop_lines(
        tree_setup=TREE_SETUP,
        bet_sizes=tree_data["flop_sizes"],
        position=POSITION,
        board=BOARD,
        outdir=OUTDIR,
        timeout=600,
    )
