###################################################################################################
###################################################################################################
###################################################################################################
########### DIFF CHECKER CODE INPUT STUFF IS AT THE BOTTOM! CHANGE TO TEST YOUR PROGRAM ###########
###################################################################################################
###################################################################################################
###################################################################################################
from subprocess import Popen, PIPE
import os
import glob
import sys
import subprocess
import sysconfig
import difflib
import itertools
import textwrap
import typing
import re

def GREEN(string):
    return "\033[92m" + string + "\033[00m"

def RED(string):
    return "\033[91m" + string + "\033[00m"

def BLUE(string):
    return "\033[94m" + string + "\033[00m"


"""
Change directory to the directory of this script. This is important because the c file should be in the same directory as this script.
"""
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)



"""
This script assumes you only have one c file in this directory. You would need to change if there are more than one
"""
file_pattern = "*.c"
try:
    file = glob.glob(file_pattern)[0]
except:
    print(RED("No c file found!"))
    sys.exit(1)
print(GREEN("File ") + BLUE(file) + GREEN(" found. Compiling..."))


"""
Compiles the found file
"""
# Get the compiler (e.g., 'gcc' or 'clang')
cc = sysconfig.get_config_var('CC')  
if not cc:
    print(RED("No compiler found!"))
    sys.exit(1)

# Get the default C flags and linker flags
cflags = sysconfig.get_config_var('CFLAGS')  
ldflags = sysconfig.get_config_var('LDFLAGS')


source_file = file
output_binary = file[:-2] # Remove the '.c' extension to get the binary name

compile_command = f"{cc} -Wall {cflags} {ldflags} -o {output_binary} {source_file} -lm"
try:
    subprocess.run(compile_command, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(RED(f"Compilation failed!\nError Output:\n{e.stderr}"))
    sys.exit(1)
print(GREEN("Compiled " + BLUE(source_file) + GREEN(" into ") + BLUE(output_binary)))



"""
Copied & pasted + modified code from https://gist.github.com/jlumbroso/3ef433b4402b4f157728920a66cc15ed
"""
# Helper function to remove ANSI escape codes -> gets lengths correct this time
def strip_ansi_codes(s: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s)



def side_by_side(
    left: typing.List[str],
    right: typing.List[str],
    width: int = 78,
    as_string: bool = False,
    separator: typing.Optional[str] = " | ",
    left_title: typing.Optional[str] = None,
    right_title: typing.Optional[str] = None,
) -> typing.Union[str, typing.List[str]]:

    DEFAULT_SEPARATOR = " | "
    separator = separator or DEFAULT_SEPARATOR
    mid_width = (width - len(separator) - (1 - width % 2)) // 2
    tw = textwrap.TextWrapper(
        width=mid_width,
        break_long_words=False,
        replace_whitespace=False
    )

    def reflow(lines):
        stripped_lines = [strip_ansi_codes(line) for line in lines]  # Remove ANSI codes for wrapping
        wrapped_lines = list(map(tw.wrap, stripped_lines))
        colored_wrapped_lines = []

        for i, wls in enumerate(wrapped_lines):
            if not wls:
                wls = [""]
            original_color = re.match(r"(\033\[[0-9;]*m)?", lines[i])  # Extract ANSI color
            original_color = original_color.group(0) if original_color else ""
            colored_wrapped_lines.extend([original_color + w + "\033[00m" for w in wls])  # Restore color

        return colored_wrapped_lines

    left = reflow(left)
    right = reflow(right)
    zip_pairs = itertools.zip_longest(left, right)

    if left_title or right_title:
        left_title = left_title or ""
        right_title = right_title or ""
        zip_pairs = [(left_title, right_title), ("-" * mid_width, "-" * mid_width)] + list(zip_pairs)

    lines = []
    for l, r in zip_pairs:
        l = l or ""
        r = r or ""
        
        l_stripped = strip_ansi_codes(l)
        r_stripped = strip_ansi_codes(r)

        line = "{}{}{}{}".format(
            l,
            " " * max(0, mid_width - len(l_stripped)),
            separator,
            r
        )
        lines.append(line)

    if as_string:
        return "\n".join(lines)
    return lines



def better_diff(
    left: typing.List[str],
    right: typing.List[str],
    width: int = 78,
    as_string: bool = False,
    separator: typing.Optional[str] = None,
    left_title: typing.Optional[str] = None,
    right_title: typing.Optional[str] = None,
) -> typing.Union[str, typing.List[str]]:

    differ = difflib.Differ()
    left_side = []
    right_side = []

    difflines = list(differ.compare(left, right))
    
    for line in difflines:
        op = line[0]
        tail = line[2:]

        if op == " ":
            left_side.append("\033[92m" + tail + "\033[00m")   # Green for matching lines
            right_side.append("\033[92m" + tail + "\033[00m")
        elif op == "-":
            left_side.append("\033[91m" + tail + "\033[00m")   # Red for removed lines
            right_side.append("")
        elif op == "+":
            left_side.append("")
            right_side.append("\033[91m" + tail + "\033[00m")  # Red for added lines

    return side_by_side(
        left=left_side,
        right=right_side,
        width=width,
        as_string=as_string,
        separator=separator,
        left_title=left_title,
        right_title=right_title,
    )



"""
find the correct code files. 
IMPORTANT: assumes the formatting of each example one is the same as assg1, may need to change
this SHOULD work as long as this pattern match holds lol
"""
correct_code_binary = "ex" + output_binary[0].upper() + output_binary[1:]
try:
    file = glob.glob(correct_code_binary)[0]
except:
    print(RED("No file matching the pattern (ex + filename) found!"))
    sys.exit(1)
print(GREEN("Executable ") + BLUE(correct_code_binary) + GREEN(" found"))

def diff(my_arr, correct_arr, title):
    return better_diff(
        my_arr,
        correct_arr,
        width=WIDTH,
        as_string=True,
        left_title=f"MY {title}",
        right_title=f"CORRECT {title}" 
    )

def diff_print(my_arr, correct_arr, title):
    print(better_diff(
        my_arr,
        correct_arr,
        width=WIDTH,
        as_string=True,
        left_title=f"MY {title}",
        right_title=f"CORRECT {title}" 
    ))


###################################################################################################
###################################################################################################
###################################################################################################
"""
Use guide:
1) put this into the folder with your c code and the copied test file. If no copied test file then
make sure to get it. When you run this, it will compare the stdout, stderr, and err code
of yours agains the example.

2) edit the below inputs array to contain inputs you would like to try. The strings are essentially
1:1 like you would type in the console as stdin, but use \n for newlines instead of hitting enter.

3) turn on verbose file logger if you want the whole thing written out to a txt file. Has colored
ANSII excapes so you can view that with a good txt viewer.

IMPORTANT: you need to have the same error messages as the example if you don't want stderr to
be flagged as different all the time.
"""
WIDTH = 100

VERBOSE_FILE_LOGGER = False

inputs = []
###################################################################################################
###################################################################################################
###################################################################################################

failed = False # print flag

if VERBOSE_FILE_LOGGER:
    if os.path.exists(output_binary + "_verbose_output.txt"):
        os.remove(output_binary + "_verbose_output.txt")

for i in inputs:
    myCode = Popen(f"./{output_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
    correctCode = Popen(f"./{correct_code_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)

    my_stdout, my_stderr = myCode.communicate(input=i)
    correct_stdout, correct_stderr = correctCode.communicate(input=i)

    stdout_diff = diff(my_stdout.split("\n"), correct_stdout.split("\n"), "STDOUT")
    stderr_diff = diff(my_stderr.split("\n"), correct_stderr.split("\n"), "STDERR")
    return_code_diff = diff([f"{myCode.returncode}"], [f"{correctCode.returncode}"], "RETURN CODE")

    if VERBOSE_FILE_LOGGER:
        f = open(output_binary + "_verbose_output.txt", "a")
        f.write(GREEN(f"\n\n\n\nInput:\n{i}\n"))
        f.write(BLUE("#"*WIDTH) + "\n")
        f.write(stdout_diff + "\n")
        f.write(stderr_diff + "\n")
        f.write(return_code_diff + "\n")
        f.write(BLUE("#"*WIDTH) + "\n")
        f.close()

    if (my_stdout != correct_stdout) or (my_stderr.strip() != correct_stderr.strip()) or (myCode.returncode != correctCode.returncode):
        failed = True
        print(BLUE("\n"*4 + "~"*WIDTH))
        print(RED(f"Input:\n{i}"))
        print(BLUE("~"*WIDTH))
        print(stdout_diff)
        print(BLUE("~"*WIDTH))
        print(stderr_diff)
        print(BLUE("~"*WIDTH))
        print(return_code_diff)
        print(BLUE("~"*WIDTH))

if not failed:
    print("\033[1;32;40m\nYou passed the tests!\033[0m\n")
else:
    print("\033[1;31;40m\nYou failed some tests (see above for diff).\033[0m\n")
