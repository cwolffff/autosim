import logging
import os
from pexpect.popen_spawn import PopenSpawn


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


END_STRING = "END"


class Solver:
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
        self._print_output()
        self._set_end_string(END_STRING)

    def _sendline(self, line):
        logger.debug(f"Sending line: {line}")
        self._process.sendline(line)

    def _expect(self, expr):
        logger.debug(f"Expecting {expr}")
        self._process.expect(expr)

    def _set_end_string(self, s):
        """
        Tell the PioSolver process to terminate every response with the string {s}.
        """
        self._sendline(f"set_end_string {s}")

    def _read_output(self):
        """
        Read the solver processes' text up to the string pattern matched by the last
        call to self._process.expect.
        """
        return self._proc.before.decode().strip()

    def _print_output(self):
        print(self._read_output())

    def _wait_for_startup_msg(self):
        msg_ending = "\r\n\r\n"
        self._expect(msg_ending)

    def is_ready(self):
        self._sendline("is_ready")
        self._expect(END_STRING)
        logger.info(self._read_output())

    def exit(self):
        logger.info("Killing solver process...")
        self._sendline("exit")
