def retKey():
    lines = []
    with open("keys.txt") as f:
        for line in f:
            lines.append(line.strip('\n'))
    return lines