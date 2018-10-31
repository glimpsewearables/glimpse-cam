import sys

def decode(str):
    ret = ""
    for s in str:
        num = ord(s)
        num -= 1
        ret += chr(num)
    return ret

def retKey():
    lines = ""
    with open("code.txt", "r") as f:
        lines = f.readlines()
        lines = [x.strip('\n') for x in lines]
    access = lines[0]
    secret = lines[1]
    access_encode = decode(access)
    secret_encode = decode(secret)
    return [access_encode, secret_encode]
