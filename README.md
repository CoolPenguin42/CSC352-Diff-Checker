<h1 align="center">
  CSC352-Diff-Checker
</h1>
<p align="center">
  handy diff checker util for comparing the expected vs actual outputs
</p>
<p align="center">
  code was written pretty quickly, so it has not been super thoroughly tested and is likely very janky
</p>


## Contributing:
If you would like to help fix up the code or add features, feel free to branch and pull request your fixes! Just make sure to test well
before doing so

## KNOWN ISSUES
- **Color Bug:** The way it is currently implemented, the ANSII escape sequences for the coloring will get text wrapped.
unsure how to fix atm, but it is a minor issue that does not really impact performance when width is high.

## USAGE
- **1)** put this script in the folder with the c file UUT. Copy the expceted version into the same folder from lectura (this
is not done for you in case you use this locally)
  - **CONSIDERATIONS:** The script assumes the format of the example test file is the same as assg1 (ex isFib.c -> esIsFib for example file)

- **2)** edit the inputs array to hold the input strings you put to c file stdin. You can modify the script however you like to achieve this. Write
some loops that fill the array with testable inputs... readlines a pre-made file into input array... etc.

- **3)** Turn on/off verbose file logger flag. It will (when enabled) write all testcase outputs to a file for reference in full.

- **4)** Run the script

## Compatibility
Works on lectura with gcc. Should probably work with clang and other c compiler but I have not personally tested that. If it does not work, try
fixing and pull requesting. Otherwise you can hard code the compile command in the script

## SOURCES
Diff output and formatter code: https://gist.github.com/jlumbroso/3ef433b4402b4f157728920a66cc15ed#file-diff_side_by_side-py
