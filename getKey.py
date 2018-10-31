import sys

def retKey():
    lines = ""
    with open("config.txt", "r") as f:
        lines = f.readlines()
        lines = [x.strip('\n') for x in lines]
    return [lines[0], lines[1]]
