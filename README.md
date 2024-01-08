# MCWhitelistFix
Fix the currently broken /whitelist command

## How to use
1. Put the script into your Minecraft folder
2. Make sure to install all requirements with `pip install -r requirements.txt`
3. Execute following command:
`python3 whitelist.py <add|remove|info> <username>`
4. After you're done whitelisting, go to Minecraft and run `whitelist reload`

## Common issues
**Question:** I can't whitelist people! It says `Could not locate whitelist.json`\
**Answer:** Make sure you have the correct path to the whitelist.json in your `whitelist_settings.json`!

**Question:** I get the `We are rate-limited! Retrying in (time) seconds` error.\
**Answer:** This is not a bug but rather a problem on Mojang's side which only allows a specific amount of requests per minute