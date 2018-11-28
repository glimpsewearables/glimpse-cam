# Michael Fang
# to use it
# call retKey() which will return a list [access, secret]

def retKey():
    lines = ""
    access = ""
    secret = ""

    with open("/home/pi/glimpse-cam/access.txt", "r") as f:
        lines = f.readlines()
        lines = [x.strip('\n') for x in lines]

    for line in lines:
        num = int(line) # get the distance
        num += ord("F")
        access += chr(num)

    with open("/home/pi/glimpse-cam/secret.txt", "r") as f:
        lines = f.readlines()
        lines = [x.strip('\n') for x in lines]

    for line in lines:
        num = int(line) # get the distance
        num += ord("F")
        secret += chr(num)

    return [access, secret]
