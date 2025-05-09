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

4) Turn on/off valgrind flag for testing with valgrind.

IMPORTANT: you need to have the same error messages as the example if you don't want stderr to
be flagged as different all the time.

ALSO NOTE: When using valgrind, it takes a LOOOONG time to initially start up. So it might
seem like your code is stuck in an infinite loop, but it just needs like 60 something seconds to
startup before EVENTUALLY outputting
"""
WIDTH = 100

VERBOSE_FILE_LOGGER = False # Writes out to a file in case you want to see the whole output
USE_VALGRIND = False # If you want to test with valgrind

inputs = []

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
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil


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

compile_command = f"{cc} -Wall -g {cflags} {ldflags} -o {output_binary} {source_file} -lm"
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
marks the whitespace before parsing string. allows for diff checking to visually represent
special space characters and make it easier to see the differences!
"""
def mark_whitespace(s: str) -> str:
    mapping = {
        ' ': '␣',    # space
        '\t': '⇥',   # tab
        '\r': '␍',   # carriage return
        '\v': '␋',   # vertical tab
        '\f': '␌',   # form feed
    }
    result = []
    for ch in s:
        if ch == '\n':
            # Instead of replacing newline with a marker and losing the break,
            # append a marker then the actual newline so it remains a line break.
            result.append('⏎')
            result.append('\n')
        else:
            result.append(mapping.get(ch, ch))
    return ''.join(result)


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
    # --- Determine the relative path of the script directory ---
    # This assumes the script is located in a folder like .../assgX/probY/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Split the directory path into parts
    parts = script_dir.split(os.sep)
    if len(parts) < 2:
        print(RED("Script directory does not have enough subdirectories to determine assignment and problem."))
        sys.exit(1)
    # Extract the last two directory names (assgX and probY)
    relative_path = os.path.join(parts[-2], parts[-1])

    # --- Build the source directory path ---
    assignments_base = '/home/cs352/spring25/assignments'
    source_dir = os.path.join(assignments_base, relative_path)
    if not os.path.exists(source_dir):
        print(RED("Source directory {} does not exist".format(source_dir)))
        sys.exit(1)

    print(GREEN("Copying contents from ") + BLUE(source_dir) + GREEN(" to the current directory"))

    # --- Copy contents from source_dir to the current directory ---
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(script_dir, item)
        try:
            if os.path.isdir(s):
                # For Python 3.8 and above, dirs_exist_ok=True allows copying into an existing directory.
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        except Exception as e:
            print(RED("Failed to copy {}: {}".format(s, e)))
            sys.exit(1)

    print(GREEN("Contents copied successfully"))
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


if VERBOSE_FILE_LOGGER:
    if os.path.exists(output_binary + "_verbose_output.txt"):
        os.remove(output_binary + "_verbose_output.txt")


###################################################################################################
###################################################################################################
###################################################################################################
fail_count = 0
valgrind_failures = []  # This list will collect the inputs that fail Valgrind

if USE_VALGRIND:
    """
    Runs in parallel, since valgrind is slow AF, and non-parallel takes AGES
    """
    max_workers = min(os.cpu_count(), len(inputs)) if inputs else 1
    results = []

    def run_single_test(count, i):
        result = {}
        result["count"] = count
        result["input"] = i

        myCode = Popen(f"./{output_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        correctCode = Popen(f"./{correct_code_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        my_stdout, my_stderr = myCode.communicate(input=i)
        correct_stdout, correct_stderr = correctCode.communicate(input=i)
        result["my_stdout"] = my_stdout
        result["my_stderr"] = my_stderr
        result["correct_stdout"] = correct_stdout
        result["correct_stderr"] = correct_stderr
        result["my_returncode"] = myCode.returncode
        result["correct_returncode"] = correctCode.returncode

        stdout_diff = diff(
            mark_whitespace(my_stdout).split("\n"),
            mark_whitespace(correct_stdout).split("\n"),
            "STDOUT"
        )
        stderr_diff = diff(
            my_stderr.split("\n"),
            correct_stderr.split("\n"),
            "STDERR"
        )
        return_code_diff = diff(
            [f"{myCode.returncode}"],
            [f"{correctCode.returncode}"],
            "RETURN CODE"
        )
        result["stdout_diff"] = stdout_diff
        result["stderr_diff"] = stderr_diff
        result["return_code_diff"] = return_code_diff

        valgrind_proc = subprocess.run(
            ["valgrind", "--leak-check=full", "--show-leak-kinds=all", "--track-origins=yes", "--verbose", f"./{output_binary}"],
            input=i, capture_output=True, text=True
        )
        valgrind_error = valgrind_proc.stderr
        if re.search(r"ERROR SUMMARY:\s*0 errors", valgrind_error):
            result["valgrind_result"] = GREEN("Valgrind: you passed (does not mean there isn't memory error)")
            result["valgrind_passed"] = True
        else:
            result["valgrind_result"] = RED("Valgrind error detected.")
            result["valgrind_passed"] = False

        result["passed"] = (my_stdout == correct_stdout) and \
                           (my_stderr.strip() == correct_stderr.strip()) and \
                           (myCode.returncode == correctCode.returncode)
        return result

    completed_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_test, count, i): count for count, i in enumerate(inputs)}
        for future in as_completed(futures):
            result = future.result()
            completed_count += 1
            results.append(result)
            # Check if diff passed...
            if result["passed"]:
                # ...but Valgrind failed:
                if not result.get("valgrind_passed", True):
                    fail_count += 1
                    print(RED(f"Test {result['count']} failed. [{completed_count}/{len(inputs)}]"))
                    print(RED("Input:\n" + repr(result["input"])))
                    print(BLUE("~" * WIDTH))
                    print(GREEN("OUTPUT MATCHES CORRECTLY"))
                    print(BLUE("~" * WIDTH))
                    print(BLUE("Valgrind Check:"))
                    print(result["valgrind_result"])
                    print(BLUE("~" * WIDTH))
                else:
                    print(GREEN(f"Test {result['count']} passed. [{completed_count}/{len(inputs)}]"))
            else:
                fail_count += 1
                print(RED(f"Test {result['count']} failed. [{completed_count}/{len(inputs)}]"))
                # Use repr() here so that special characters remain escaped
                print(RED("Input:\n" + repr(result["input"])))
                print(BLUE("~" * WIDTH))
                print(result["stdout_diff"])
                print(BLUE("~" * WIDTH))
                print(result["stderr_diff"])
                print(BLUE("~" * WIDTH))
                print(result["return_code_diff"])
                print(BLUE("~" * WIDTH))
                print(BLUE("Valgrind Check:"))
                print(result["valgrind_result"])
                print(BLUE("~" * WIDTH))
            # Collect inputs that failed the Valgrind check.
            if not result.get("valgrind_passed", True):
                valgrind_failures.append(result["input"])
            sys.stdout.flush()

    # Write verbose log file if enabled.
    if VERBOSE_FILE_LOGGER:
        with open(output_binary + "_verbose_output.txt", "a") as f:
            for res in sorted(results, key=lambda r: r["count"]):
                f.write(GREEN(f"\n\n\n\nInput:\n{repr(res['input'])}\n"))
                f.write(BLUE("#" * WIDTH) + "\n")
                f.write(res["stdout_diff"] + "\n")
                f.write(res["stderr_diff"] + "\n")
                f.write(res["return_code_diff"] + "\n")
                f.write("Valgrind Output:\n" + res["valgrind_result"] + "\n")
                f.write(BLUE("#" * WIDTH) + "\n")

    if fail_count == 0:
        print(GREEN(f"\nPASSED ALL {len(inputs)} TESTS!"))
    else:
        print(RED(f"\nFAILED {fail_count} OUT OF {len(inputs)} TESTS! (see above for diff)."))

    # At the end, print the collected inputs that failed the Valgrind check.
    if valgrind_failures:
        print(RED(f"\nThe following {len(valgrind_failures)} inputs failed the Valgrind check:"))
        for inp in valgrind_failures:
            print(RED(repr(inp)))
        print(RED("To debug, run: " + BLUE(f"valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./{output_binary}") +
                                            RED("\nThen inspect the output for errors and leaks!")))
else:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # This function runs a single test and returns a result dictionary.
    def run_single_test(count, test_input):
        result = {}
        result["count"] = count
        result["input"] = test_input

        myCode = Popen(f"./{output_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        correctCode = Popen(f"./{correct_code_binary}", stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        my_stdout, my_stderr = myCode.communicate(input=test_input)
        correct_stdout, correct_stderr = correctCode.communicate(input=test_input)

        result["my_stdout"] = my_stdout
        result["my_stderr"] = my_stderr
        result["correct_stdout"] = correct_stdout
        result["correct_stderr"] = correct_stderr
        result["my_returncode"] = myCode.returncode
        result["correct_returncode"] = correctCode.returncode

        result["stdout_diff"] = diff(
            mark_whitespace(my_stdout).split("\n"),
            mark_whitespace(correct_stdout).split("\n"),
            "STDOUT"
        )
        result["stderr_diff"] = diff(
            my_stderr.split("\n"),
            correct_stderr.split("\n"),
            "STDERR"
        )
        result["return_code_diff"] = diff(
            [f"{myCode.returncode}"],
            [f"{correctCode.returncode}"],
            "RETURN CODE"
        )

        result["passed"] = (my_stdout == correct_stdout) and \
                           (my_stderr.strip() == correct_stderr.strip()) and \
                           (myCode.returncode == correctCode.returncode)
        return result

    fail_count = 0
    failed_tests = []
    futures = []
    results = []

    # Use up to as many workers as CPU cores or tests
    max_workers = min(os.cpu_count(), len(inputs)) if inputs else 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for count, test_input in enumerate(inputs):
            futures.append(executor.submit(run_single_test, count, test_input))

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result["passed"]:
                print(GREEN(f"\nYOU PASSED TEST {result['count']}"))
            else:
                fail_count += 1
                failed_tests.append((result["count"], result["input"]))
                print(BLUE("\n" * 4 + "~" * WIDTH))
                print(RED(f"Input:\n{repr(result['input'])}"))
                print(BLUE("~" * WIDTH))
                print(result["stdout_diff"])
                print(BLUE("~" * WIDTH))
                print(result["stderr_diff"])
                print(BLUE("~" * WIDTH))
                print(result["return_code_diff"])
                print(BLUE("~" * WIDTH))

            sys.stdout.flush()

            if VERBOSE_FILE_LOGGER:
                with open(output_binary + "_verbose_output.txt", "a") as f:
                    f.write(GREEN(f"\n\n\n\nInput:\n{repr(result['input'])}\n"))
                    f.write(BLUE("#" * WIDTH) + "\n")
                    f.write(result["stdout_diff"] + "\n")
                    f.write(result["stderr_diff"] + "\n")
                    f.write(result["return_code_diff"] + "\n")
                    f.write(BLUE("#" * WIDTH) + "\n")

    if fail_count == 0:
        print(GREEN(f"\nPASSED ALL {len(inputs)} TESTS!"))
    else:
        print(RED(f"\nFAILED {fail_count} OUT OF {len(inputs)} TESTS! (see above for diff)."))
        print(RED("\nThe following test(s) failed:"))
        for idx, inp in failed_tests:
            print(RED(f"  Test {idx}: Input={repr(inp)}"))