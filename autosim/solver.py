import os
from pexpect.popen_spawn import PopenSpawn


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

        self.hand_order = self._get_hand_order()

    def _sendline(self, line):
        if "\n" in line:
            print(f">> {line.encode('utf-8')}")
        else:
            print(f">> {line}")
        self._process.sendline(line)

    def _expect(self, expr):
        if "\n" in expr:
            print(f"DEBUG: Expecting {expr.encode('utf-8')}")
        else:
            print(f"DEBUG: Expecting {expr}")
        self._process.expect(expr)

    def _read_output(self):
        """
        Read the solver processes' text up to the string pattern matched by the last
        call to self._process.expect.
        """
        return self._process.before.decode().strip()

    def _print_output(self):
        output = self._read_output()
        if "\n" in output:
            print("<<")
            for line in output.split("\n"):
                print(line)
        else:
            print(f"<< {output}")

    def _wait_for_startup_msg(self):
        msg_ending = "\r\n\r\n"
        self._expect(msg_ending)

    def _set_end_string(self, s):
        """
        Tell the PioSolver process to terminate every response with the string {s}.
        """
        self._sendline(f"set_end_string {s}")
        self._expect(END_STRING)
        self._print_output()

    def _get_hand_order(self):
        self._sendline("show_hand_order")
        self._expect(END_STRING)
        hand_order = self._read_output()
        return hand_order.split(" ")

    def is_ready(self):
        self._sendline("is_ready")
        self._expect(END_STRING)
        self._print_output()

    def exit(self):
        print("Killing solver process...")
        self._sendline("exit")

    def bench(self):
        self._sendline("bench")
        self._expect(END_STRING)
        self._print_output()

    def load_script(self, filename):
        """
        Reads commands from a file line after line and executes them as if they were
        inserted in stdin. After reaching EOF, go back to receiving input from stdin.

        WARNING: it's not recommended to run this command from another program. Use
        load_script_silent or manually execute commands one after another.

        """
        self._sendline(f"load_script {filename}")
        self._expect(END_STRING)
        self._print_output()

    def load_script_silent(self, filename):
        """
        Like self.load_script but acts as a single command and returns only one END
        string at the very end.
        """
        self._sendline(f"load_script_silent {filename}")
        self._expect(END_STRING)
        self._print_output()


if __name__ == "__main__":
    # Test. TODO: remove later.
    solver = Solver("C:/PioSOLVER/PioSOLVER2-pro.exe")
    solver.is_ready()
    solver.bench()
