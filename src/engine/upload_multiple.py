import sys
import stitch_connect as stcu


file_paths = []

# Read input from stdin until an empty line is encountered
while True:
    line = sys.stdin.readline().rstrip()
    if line == "":
        break
    file_paths.append(line)

fileArray = file_paths[0].split(',')
stcu.getStitchResult(fileArray)
