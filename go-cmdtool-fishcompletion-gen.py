#!/usr/bin/env python3

import sys
import os
import locale
import subprocess
import re

def parse_options(help_msg):
    options = []

    for line in help_msg.split("\n"):
        # New option
        if line.startswith("  -"):
            option = line.strip("  -").split("\t")
            option[0] = option[0].split(" ")
            options.append(option)

        # Description of the last option
        else:
            try:
                description = line.split("\t")[1]
                options[-1].append(description)
            except IndexError:
                pass

    return options

def gen_fish_complete(options, cmd):
    res = ""

    for opt in options:
        op = opt[0]

        # Shorten the description and format it
        # ex: `some (kind of) description; more "text"; even more`
        #      becomes `some (kind of) description`
        desc = opt[1].replace('\\','\\\\').replace('"','\"').capitalize().split(";")[0]

        # Remove the last part of the description between parentheses
        # ex: "Some (kind of) description (text in parentheses)"
        #      becomes "Some (kind of) description"
        m = re.search(" \(.*\)$", desc)
        if m != None:
            desc = desc[:m.start()] + desc[m.end():]


        complete_args = ""

        if len(op) > 1:
            if op[1] == "int" or op[1] == "float":
                complete_args += " -x"
            elif op[1] == "string":
                complete_args += " -r"
            elif op[1] == "bool":
                complete_args += ' -x -a "true false"'


        if len(op[0]) == 1:
            res += 'complete -c {} -s {} -d "{}"{}\n'.format(cmd, op[0], desc, complete_args)
        else:
            res += 'complete -c {0} -l {1} -o {1} -d "{2}"{3}\n'.format(cmd, op[0], desc, complete_args)

    res += 'complete -c {} -l help -o help -s h -d "Show help"'.format(cmd)

    return res

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: {} COMMAND".format(sys.argv[0]))
        sys.exit()

    cmd_name = sys.argv[1]

    encoding = locale.getpreferredencoding()
    help_cmd_res = subprocess.run([cmd_name, '-h'], stderr=subprocess.PIPE)
    help_msg = help_cmd_res.stderr.decode(encoding)

    print(gen_fish_complete(parse_options(help_msg), cmd_name))

