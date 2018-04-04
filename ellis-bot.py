import discord
import time
import datetime
import threading
import random

TOKEN = "NDMwNzA2NzQ4ODUzMTkwNjU2.DaUJSw.1GOfezdHzVV5ARD1DRLpniLyZZw"
repo = r"https://github.com/Nytra/Ellis-Bot"

client = discord.Client()

debug = False
start_time = int(time.time())
timers = []

help_msg = """!hello - Ellis will greet you.
!pig - Tells you who the Fortnite Pig currently is.
!poke [target] - Ellis will poke the target.
!debug - Enables debugging mode.
!datetime - Displays the current date and time.
!dumpvars - Displays a list of all of Ellis's variables and their respective values.
!uptime - Tells you how long Ellis has been online for.
!source - Provides you with a link to this project's GitHub repository.
!help - Displays this message.
!kill - Kills the bot."""

class Timer:
    def __init__(self, unix, member, channel):
        self.unix = unix
        self.member = member
        self.channel = channel
        self.done = False

    def get_unix(self):
        return self.unix

    def get_member(self):
        return self.member

    def get_channel(self):
        return self.channel

    def is_done(self):
        return self.done

    def set_done(self):
        self.done = True

def timer_thread():
    while True:
        for timer in timers:
            if int(time.time()) > timer.get_unix():
                client.send_message(timer.get_channel(), "Timer set by " + timer.get_member().mention + " has been activated.")
                timers.remove(timer)

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

    for role in message.author.roles:
        if role.name == "Fortnite Pig":
            msg = "OINK " + message.author.mention
            await client.send_message(message.channel, msg)

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

    if message.content.startswith("!datetime"):
        dt = datetime.datetime.now()
        msg = "[{}/{}/{}] [{}:{}:{}]".format(dt.day,
                                             dt.month,
                                             dt.year,
                                             dt.hour,
                                             dt.minute,
                                             dt.second)
        await client.send_message(message.channel, msg)

    if debug and message.content.startswith("!dumpvars"):
        msg = "Dumping vars..."
        await client.send_message(message.channel, msg)
        msg = ""
        for var in globals():
            msg += str(var) + " = " + str(globals()[var]) + "\n"
        await client.send_message(message.channel, msg)

    if message.content.startswith("!uptime"):
        msg = "Ellis has been online for " + str(int(time.time()) - start_time) + " seconds."
        await client.send_message(message.channel, msg)

    if message.content.startswith("!source"):
        msg = repo
        await client.send_message(message.channel, msg)

    if message.content.startswith("!help"):
        await client.send_message(message.channel, help_msg)

    if message.content.startswith("!kill"):
        await client.send_message(message.channel, "Shutting down...")
        client.logout()

    if message.content.startswith("!timer"):
        dur = int(message.content.split()[1])
        timers.append(Timer(int(time.time()) + dur, message.author, message.channel))
        msg = "Timer set for " + str(dur) + " seconds."
        await client.send_message(message.channel, msg)

    if message.content.startswith("!flip"):
        n = random.randint(0, 1)
        if n == 0:
            msg = "Heads!"
        else:
            msg = "Tails!"
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print("Logged in successfully.")

@client.event
async def on_member_remove(member):
    print(member.name, "has logged out.")

t1 = threading.Thread(target=timer_thread)
t1.start()
client.run(TOKEN)