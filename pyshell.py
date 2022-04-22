#!/usr/bin/env python3

"""pysh: a shell written in Python"""

import os
import subprocess
import platform

def execute_command(command):
    """execute commands and handle piping"""
    try:
        if "|" in command:
            # save for restoring later on
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # first command takes commandut from stdin
            fdin = os.dup(s_in)

            # iterate over all the commands that are piped
            for cmd in command.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last command
                if cmd == command.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    subprocess.run(cmd.strip().split())
                except Exception:
                    print("pysh: command not found: {}".format(cmd.strip()))

            # restore stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)
        else:
            subprocess.run(command.split(" "))
    except Exception:
        print("pysh: command not found: {}".format(command))


def pysh_cd(path):
    """convert to absolute path and change directory"""
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))


def pysh_help():
    print("""PySH or PythonShell v1.0.0
Licensed under the GNU General Public License version 3 (GNU GPLv3)
PySH supports all basic shell commands.
Some commands:
ls [-lh]
cd [dir]
touch [filename]
mkdir (dirname)
rmdir (dirname)
rm [filename]
ping (ipaddrorfqdn)
sudo (cmd)
exit
logout
""")


def main():
    user = os.getlogin()
    hostname = platform.node()
    pwddir = os.getcwd()
    while True:
        inp = input(user+"@"+hostname+":"+pwddir+"$ ")
        if inp == "exit" or inp == "logout":
            break
        elif inp[:3] == "cd ":
            pysh_cd(inp[3:])
        elif inp == "help":
            pysh_help()
        elif inp == "" or inp == "\n":
            continue
        else:
            execute_command(inp)


if '__main__' == __name__:
    main()
