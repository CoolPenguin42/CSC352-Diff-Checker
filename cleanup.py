import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import glob
for file_path in glob.glob("./**/*_verbose_output.txt", recursive=True):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed {file_path}")