import json

with open('config.json') as f:
    data = json.load(f)

#updating wifi
for wifi in data["user1"]["wifi"]:
	print("network={\n\tssid=\"" + wifi["ssid"] + "\"\n\tpsk=\"" + wifi["psk"] + "\"\n}")
