def retKey():
    lines = []
    with open("/home/pi/glimpse-cam/keys.txt") as f:
        for line in f:
            lines.append(line.strip())
    return lines
