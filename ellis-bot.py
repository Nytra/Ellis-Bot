import discord

TOKEN = "NDMwNzA2NzQ4ODUzMTkwNjU2.DaUJSw.1GOfezdHzVV5ARD1DRLpniLyZZw"

client = discord.Client()

def get_mention(username):
	members = client.get_all_members()
	for member in members:
		if member.name.lower() == username.lower():
			return member.mention

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!hello"):
        msg = "Hello {0.author.mention}".format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!pig"):
    	msg = "The Fortnite Pig is "
    	members = client.get_all_members()
    	for member in members:
    		for role in member.roles:
    			if role.name == "Fortnite Pig":
    				msg += member.mention
    	await client.send_message(message.channel, msg)

    if message.content.startswith("!rape"):
    	parts = message.content.split()
    	if len(parts) == 1:
    		msg = "*Ellis rapes " + message.author.mention + "*"
    	elif len(parts) == 2:
    		msg = "*Ellis rapes " + get_mention(parts[1]) + "*"

    	await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-----")

client.run(TOKEN)
