import json
import os.path
import sys
import time
import uuid

import requests

api_endpoint = "https://api.mojang.com/users/profiles/minecraft/"
wait_time = 10
settings: dict = json.load(open("whitelist_settings.json"))
whitelist_location = settings.get("whitelist_location")

if not os.path.isfile(whitelist_location):
	print("Could not locate whitelist.json")
	sys.exit()
data: list = json.load(open(whitelist_location))


def get_key(uuid_: str) -> int | None:
	uuid_ = str(uuid.UUID(uuid_))
	i = 0
	for player in data:
		if player["uuid"] == uuid_:
			return i
		i += 1

	return None


def already_whitelisted(uuid_: str) -> bool:
	# Most epic line of code
	uuid_ = str(uuid.UUID(uuid_))
	for player in data:
		if player["uuid"] == uuid_:
			return True
	return False


def data_from_name(username: str) -> dict:
	resp = requests.get(api_endpoint + username)
	if resp.status_code == 429:
		print(f"We are rate-limited! Retrying in {wait_time} seconds")
		time.sleep(wait_time)
		data_from_name(username)

	try:
		if resp.json().get("path") is not None:
			print(f"Error: {resp.json()['errorMessage']}")
			sys.exit()
	except requests.exceptions.JSONDecodeError as err:
		print(f"Error found with response: {resp}\nrequest.exceptions.JSONDecodeError: {err}")
		sys.exit()

	return resp.json()


if len(sys.argv) < 3:
	print("Invalid arguments! Use 'add', 'remove' or 'info' and then a player name")
	sys.exit()
elif len(sys.argv) > 3:
	print("Too many arguments! Use 'add', 'remove' or 'info' and then a player name")
	sys.exit()

args = sys.argv

if args[1] == "add":
	udat = data_from_name(args[2])
	if already_whitelisted(udat['id']):
		print("User is already whitelisted!")
		sys.exit()

	user_obj = {
		"uuid": str(uuid.UUID(udat["id"])),
		"name": udat["name"]
	}
	data.append(user_obj)
	json.dump(data, open(whitelist_location, "w"), indent=2)
	print(f"Added {udat['name']} (uuid) to the whitelist")
elif args[1] == "info":
	udat = data_from_name(args[2])

	print(f"Whitelist info for {udat['name']}:")
	print(f"Trimmed UUID: {udat['id']}")
	print(f"Full UUID: {uuid.UUID(udat['id'])}")
	print(f"Already whitelisted: {already_whitelisted(udat['id'])}")
elif args[1] == "remove":
	udat = data_from_name(args[2])

	if not already_whitelisted(udat['id']):
		print("User is not whitelisted")
		sys.exit()

	data.pop(get_key(udat['id']))
	json.dump(data, open(whitelist_location, "w"), indent=2)
	print(f"Removed {udat['name']} from the whitelist")
else:
	print("Invalid arguments! Use 'add', 'remove' or 'info' and then a player name")
