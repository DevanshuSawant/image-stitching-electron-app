import sys
import stitch_connect as stcu
import time
import os
import shutil

start_time = time.time()

file_paths = []

if os.path.exists("result-images"):
    shutil.rmtree("result-images")
os.makedirs("result-images")

# Read input from stdin until an empty line is encountered
while True:
    line = sys.stdin.readline().rstrip()
    if line == "":
        break
    file_paths.append(line)

fileArray = file_paths[0].split(",")
stcu.getStitchResult(fileArray)

print("s:%s" % (time.time() - start_time))
