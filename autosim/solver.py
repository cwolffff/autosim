import logging
import os
import sys
from enum import Enum

import pexpect
from pexpect.popen_spawn import PopenSpawn


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


END_STRING = "END"


class Solver:
    """
    An interface for a PioSolver 2.0 process.

    Logging: All I/O is logged to sys.stdout. All commands sent to the solver process
    are prefaced by ">>" and all solver responses are prefaced by "<<".

    Example usage:
    ```
    solver = Solver(EXEPATH)
    solver.wait_for_ready()
    solver.set_board(BOARD)
    solver.run_script(SCRIPT)
    solver.build_tree()
    solver.go(TIMEOUT)
    solver.dump_tree(outpath)
    solver.exit()
    ```

    """

    def __init__(self, exe: str, cwd: str = None):
        """
        Args:
            exe: A path to a PioSolver 2.0 executable.
            cwd: The current working directory.

        """
        self.exe = exe
        self.cwd = cwd if cwd is not None else os.path.dirname(exe)

        self._process = PopenSpawn(exe, cwd=os.path.dirname(exe))
        self._wait_for_startup_msg()
        self._read_output()

        self.run("set_end_string", END_STRING)
        self.run("set_algorithm", "auto")
        self.run("set_threads", 0)
        self.run("set_isomorphism", 1, 0)  # 1st arg: flop; 2nd arg: turn

    def _sendline(self, line: str) -> None:
        if "\n" in line:
            logger.debug(f">> {line.encode('utf-8')}")
        else:
            logger.debug(f">> {line}")
        self._process.sendline(line)

    def _expect(self, expr, timeout=30) -> int:
        """
        Wait for the solver process to output some expression.

        expr can either be a string or a list of strings. If it's a list, wait for one
        of the strings in the list and return its index.

        """
        if isinstance(expr, list):
            logger.debug(f"Expecting one of {expr}")
        elif "\n" in expr:
            logger.debug(f"Expecting {expr.encode('utf-8')}")
        else:
            logger.debug(f"Expecting {expr}")
        return self._process.expect(expr, timeout)

    def _read_output(self):
        """
        Read the solver processes' text up to the string pattern matched by the last
        call to self._process.expect.
        """
        output = self._process.before.decode().strip()
        if "\n" in output:
            logger.debug("<<")
            for line in output.split("\n"):
                logger.debug(line)
        else:
            logger.debug(f"<< {output}")
        return output

    def _clear_output(self, timeout=1):
        """
        If we there's additional output after the last expect call, it will be included
        in the next _read_output() response. This method clears the output so that this
        doesn't happen.

        This method assumes that the process doesn't produce more output after `timeout`
        seconds have passed.

        """
        while self._process.expect([".+", pexpect.TIMEOUT], timeout) == 0:
            pass

    def _wait_for_startup_msg(self):
        msg_ending = "\r\n\r\n"
        self._expect(msg_ending)

    def run(self, cmd: str, *args, timeout=30):
        """
        Run a command, wait for the solver to respond with END_STRING, and return the
        solver's response text.

        This is ONLY meant to be used with commands for which the solver responds with a
        single message. DON'T use this method with commands that result in multiple
        return messages, such as "go".

        List of commands: https://piofiles.com/docs/upi_documentation/

        TODO: Maybe change name to _run. It's not clear whether this should be part of
        the API.

        """
        strargs = (str(arg) for arg in args)
        msg = " ".join([cmd, *strargs])
        self._sendline(msg)
        self._expect(END_STRING, timeout)
        return self._read_output()

    def run_script(self, script):
        self.run("load_script_silent", script)

    def wait_for_ready(self):
        self.run("is_ready")

    def set_board(self, board):
        self.run("set_board", board)

    def build_tree(self):
        self.run("build_tree")

    def remove_line(self, line):
        self.run("remove_line", line)

    def add_info_line(self, line):
        self.run("add_info_line", line)

    def go(self, n=None, unit="seconds"):
        if n is not None:
            self._sendline(f"go {n} {unit}")
        else:
            self._sendline("go")
        self._sendline("wait_for_solver")
        while True:
            self._expect("END", timeout=None)
            output = self._read_output()
            if "wait_for_solver ok!" in output:
                break

    def calc_results(self):
        response = self.run("calc_results").split("\n")
        assert len(response) == 5, "Unexpected response to calc_results"
        return {
            "ev_oop": float(response[0].split(" ")[-1]),
            "ev_ip": float(response[1].split(" ")[-1]),
            "mes_oop": float(response[2].split(" ")[-1]),
            "mes_ip": float(response[3].split(" ")[-1]),
            "exploitability": float(response[4].split(" ")[-1]),
        }

    def dump_tree(self, outpath: str, mode: str = "no_rivers") -> None:
        """
        Args:
            outpath: Where to save the tree to.
            mode: "full" or "no_turns" or "no_rivers".
        """
        self.run("dump_tree", outpath, mode)

    def exit(self):
        self._sendline("exit")


if __name__ == "__main__":
    # Test. TODO: remove later.
    EXEPATH = "C:/PioSOLVER/PioSOLVER2-pro.exe"
    ROOTDIR = "C:/Users/christopher/Documents/autosim"
    SCRIPT = f"{ROOTDIR}/data/test.txt"
    OUTDIR = f"{ROOTDIR}/out"
    BOARD = "As5h3d"
    TIMEOUT = 600

    os.makedirs(OUTDIR, exist_ok=True)
    # outpath = f"{OUTDIR}/{BOARD}.cfr"
    outpath = f"{OUTDIR}/test_big.cfr"

    solver = Solver(EXEPATH)
    solver.wait_for_ready()
    solver.set_board(BOARD)
    solver.run_script(SCRIPT)
    solver.build_tree()
    solver.go(TIMEOUT)
    solver.dump_tree(outpath)
    solver.exit()
