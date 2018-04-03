import discord
import time
import datetime

TOKEN = "NDMwNzA2NzQ4ODUzMTkwNjU2.DaUJSw.1GOfezdHzVV5ARD1DRLpniLyZZw"

client = discord.Client()

debug = False
start_time = int(time.time())

class Timer:
    def __init__(self, unix, member):
        self.unix = unix
        self.member = member

    def get_unix(self):
        return self.unix

    def get_member(self):
        return self.member


def get_mentions(message):
    mentions = []
    parts = list(part.lower for part in message.split())
    members = client.get_all_members()
    for member in members:
        if member.mention.lower() in parts:
            mentions.append(member)
    return mentions

@client.event
async def on_message(message):
    global debug

    if message.author == client.user:
        return

    if debug == True:
        msg = "Received message from " + message.author.mention + " in channel " + message.channel.mention
        await client.send_message(message.channel, msg)

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

    if message.content.startswith("!poke"):
        parts = message.content.split()
        if len(parts) > 1:
            for member in client.get_all_members():
                if len(parts) > 1 and member.mention == parts[1]:
                    msg = "*" + message.author.mention + " pokes " + member.mention + "*"
        else:
            msg = "Please provide a target."

        await client.send_message(message.channel, msg)

    if message.content.startswith("!debug"):
        if debug == True:
            debug = False
            msg = "Debugging disabled."
        else:
            debug = True
            msg = "Debugging enabled."

        await client.send_message(message.channel, msg)

    if message.content.startswith("!time"):
        dt = datetime.datetime.now()
        msg = "[{}/{}/{}] [{}:{}:{}]".format(dt.day,
                                             dt.month,
                                             dt.year,
                                             dt.hour,
                                             dt.minute,
                                             dt.second)
        await client.send_message(message.channel, msg)

    if debug and message.content.startswith("!dumpvars"):
        msg = ""
        for var in globals():
            msg += str(var) + " " + str(globals()[var]) + "\n"
        await client.send_message(message.channel, msg)

    if message.content.startswith("!uptime"):
        msg = "Ellis has been online for " + str(int(time.time()) - start_time) + " seconds."
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("-----")

client.run(TOKEN)