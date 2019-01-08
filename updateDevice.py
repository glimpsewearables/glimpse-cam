import json

with open('config.json') as f:
    data = json.load(f)

#updating wifi
for wifi in data["user1"]["wifi"]:
	print(wifi["name"] + ", " + wifi["password"])
