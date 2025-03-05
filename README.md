# CSC352-Diff-Checker

A handy diff checker utility for comparing the expected vs. actual outputs of your C programs. This tool automatically compiles your source file, runs tests using provided inputs, and compares the standard output, standard error, and return codes against a reference executable. It also offers optional Valgrind integration for memory leak and error checking.

## Features

- **Automated Compilation:**  
  The script searches for a single C file in the directory, compiles it using the system’s C compiler (gcc/clang), and produces an executable.

- **Side-by-Side Diff Output:**  
  Displays color-coded differences for stdout, stderr, and return codes to help pinpoint discrepancies quickly.

- **Valgrind Integration:**  
  When enabled, the tool runs tests under Valgrind to check for memory issues. Note that Valgrind tests run in parallel to reduce overall execution time, although the initial startup may be slow.

- **Verbose Logging:**  
  Optionally logs full test outputs (including diff results) to a file for in-depth debugging and record keeping.

## Setup & Usage

1. **Place the Script:**  
   Put the script in the folder containing your C source file (the Unit Under Test). Also, ensure that the reference executable is present in the folder.  
   > The script expects the reference binary to follow a naming convention: it should start with "`ex`" followed by the source file’s name (with the first letter capitalized).

2. **Edit Test Inputs:**  
   Open the script and locate the `inputs` array. Populate this array with the test input strings you wish to use. Use `\n` to denote newlines (simulating console input).

3. **Configure Flags:**  
   - **Verbose File Logger:**  
     Set `VERBOSE_FILE_LOGGER` to `True` if you want all test outputs to be logged to a file.
   - **Valgrind Testing:**  
     Set `USE_VALGRIND` to `True` to enable memory checking via Valgrind.  
     > *Tip:* Valgrind may take around 60 seconds to start up, but tests run in parallel once initiated.

4. **Run the Script:**  
   Execute the script from the terminal. It will compile the C source, run tests using your inputs, and print the diff results. If enabled, it will also perform Valgrind checks and produce a verbose log file.

## Compatibility

- **Compilers:**  
  Designed for gcc (as used on lectura), but it should also work with clang or other C compilers. If necessary, adjust the compile command in the script.

- **Platforms:**  
  Primarily intended for Unix-like environments. Windows users might need to modify commands or use a compatible shell.

## Contributing

Contributions are welcome! If you’d like to fix bugs or add new features, please fork the repository and open a pull request. Make sure to test your changes thoroughly before submitting.

## Known Issues

- **None Currently**

## Sources

- Diff output and formatter code adapted from [this gist](https://gist.github.com/jlumbroso/3ef433b4402b4f157728920a66cc15ed#file-diff_side_by_side-py).
