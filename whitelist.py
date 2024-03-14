import argparse
import json
import os.path
import sys
import time
import uuid

import requests

args: argparse.Namespace
VALID_OPERATIONS = ["add", "remove", "info"]

api_endpoint = "https://api.mojang.com/users/profiles/minecraft/"
settings: dict = json.load(open("whitelist_settings.json"))
wait_time = settings.get("rate_limit_wait_time")
whitelist_location = settings.get("whitelist_location")

if not os.path.isfile(whitelist_location):
    print("Could not locate whitelist.json")
    sys.exit(1)
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
        return data_from_name(username) # Recursively

    try:
        if resp.json().get("path") is not None:
            print(f"Error: {resp.json()['errorMessage']}")
            sys.exit(1)
    except requests.exceptions.JSONDecodeError as err:
        print(f"Error found with response: {resp}\nrequest.exceptions.JSONDecodeError: {err}")
        sys.exit(1)

    return resp.json()


def operation(the_op: str) -> str:
    """ ArgumentParser validator for the positional parameter operation.
        Valid operations are in VALID_OPERATIONS.
        We raise a ValueError for anything else.
    """
    if the_op in VALID_OPERATIONS:
        return the_op

    raise ValueError(f"invalid operation {the_op}, valid operations are {VALID_OPERATIONS}")


def get_opts():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument("operation", type=operation, help="one of 'add', 'remove', 'info'")
    parser.add_argument("player", type=str, help="A player name")

    parser.add_argument("-d", "--debug", action="count", help="enable debug logging", default=0)

    args = parser.parse_args()


def main():
    get_opts()

    if args.operation == "add":
        udat = data_from_name(args.player)
        if already_whitelisted(udat['id']):
            print("User is already whitelisted!")
            sys.exit(1)

        user_obj = {
            "uuid": str(uuid.UUID(udat["id"])),
            "name": udat["name"]
        }
        data.append(user_obj)
        json.dump(data, open(whitelist_location, "w"), indent=2)
        print(f"Added {udat['name']} (uuid) to the whitelist")
        sys.exit(0)

    if args.operation == "info":
        udat = data_from_name(args.player)

        print(f"Whitelist info for {udat['name']}:")
        print(f"Trimmed UUID: {udat['id']}")
        print(f"Full UUID: {uuid.UUID(udat['id'])}")
        print(f"Already whitelisted: {already_whitelisted(udat['id'])}")
        sys.exit(0)

    if args.operation == "remove":
        udat = data_from_name(args.player)

        if not already_whitelisted(udat['id']):
            print("User is not whitelisted")
            sys.exit(1)

        data.pop(get_key(udat['id']))
        json.dump(data, open(whitelist_location, "w"), indent=2)
        print(f"Removed {udat['name']} from the whitelist")
        sys.exit(0)

if __name__ == "__main__":
    main()
