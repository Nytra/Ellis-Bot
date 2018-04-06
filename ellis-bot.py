import discord
import time
import datetime
import threading
import time
import asyncio
import random
import sqlite3

TOKEN = "NDMwNzA2NzQ4ODUzMTkwNjU2.DaUJSw.1GOfezdHzVV5ARD1DRLpniLyZZw"
repo = "https://github.com/Nytra/Ellis-Bot"

client = discord.Client()

debug = False
start_time = int(time.time())
messages = []
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

    def is_done(self):
        if int(time.time()) > self.unix:
            return True
        return False

    def get_member(self):
        return self.member

    def get_channel(self):
        return self.channel

@client.event
async def on_message(message):
    global debug

    messages.append(message)
    args = message.content.split()

    if len(args) == 0:
        return

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
        t = int(time.time()) - start_time
        days = 0
        hours = 0
        minutes = 0
        seconds = 0
        while t >= 3600 * 24:
            days += 1
            t -= 3600 * 24
        while t >= 3600:
            hours += 1
            t -= 3600
        while t >= 60:
            minutes += 1
            t -= 60
        while t > 0:
            seconds += 1
            t -= 1
        if days > 0:
            msg = "Ellis has been online for {} days {} hours {} minutes {} seconds.".format(days, hours, minutes, seconds)
        elif hours > 0:
            msg = "Ellis has been online for {} hours {} minutes {} seconds.".format(hours, minutes, seconds)
        elif minutes > 0:
            msg = "Ellis has been online for {} minutes {} seconds.".format(minutes, seconds)
        elif seconds > 0:
            msg = "Ellis has been online for {} seconds.".format(seconds)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!source"):
        msg = repo
        await client.send_message(message.channel, msg)

    if message.content.startswith("!help"):
        await client.send_message(message.channel, help_msg)

    if message.content.startswith("!kill"):
        await client.send_message(message.channel, ":dizzy_face:")
        client.logout()
        on_kill()

    if message.content.startswith("!flip"):
        n = random.randint(0, 1)
        if n == 0:
            msg = "Heads!"
        else:
            msg = "Tails!"
        await client.send_message(message.channel, msg)

    if message.content.startswith("!rand"):
        args = message.content.split()
        if len(args) == 3:
            n = random.randint(int(args[1]), int(args[2]))
            msg = str(n)
        elif len(args) == 2:
            n = random.randint(0, int(args[1]))
            msg = str(n)
        elif len(args) == 1:
            n = random.randint(0, 10)
            msg = str(n)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!hat"):
        done = False
        n = 0
        while not done:
            n += 1
            done = True
            m = random.choice(list(client.get_all_members()))
            for role in m.roles:
                if role.name == "Bots":
                    done = False
        if debug:
            await client.send_message(message.channel, str(n) + " iterations")
        msg = m.mention
        await client.send_message(message.channel, msg)

    if args[0] == "!idiot":
        await client.send_message(message.channel, "I am an idiot.")

    if args[0] == "!server":
        msg = ""
        for server in client.servers:
            msg += "ID: " + server.id + "\n"
            msg += "Name: " + server.name + "\n"
            dt = server.created_at
            msg += "Created: " + "[{}/{}/{}] [{}:{}:{}]".format(dt.day,
                                                                dt.month,
                                                                dt.year,
                                                                dt.hour,
                                                                dt.minute,
                                                                dt.second) + "\n"
            msg += "Region: " + str(server.region) + "\n"
            msg += "Owner: " + server.owner.mention + "\n"
            msg += "Roles: " + str(len(server.roles)) + "\n"
            msg += "Members: " + str(len(list(member for member in server.members if not member.bot))) + "\n"
            msg += "Bots: " + str(len(list(member for member in server.members if member.bot))) + "\n"
            msg += "Channels: " + str(len(list(channel for channel in server.channels
                                               if channel.type == discord.ChannelType.text
                                               or channel.type == discord.ChannelType.voice)))
            await client.send_message(message.channel, msg)

    if args[0] == "!timer":
        if len(args) == 2:
            t = int(time.time()) + int(args[1])
            timers.append(Timer(t, message.author, message.channel))
            await client.send_message(message.channel, "Timer set.")

    if args[0] == "!game":
        if len(args) == 2:
            word_count = int(args[1])
        else:
            word_count = 3
        await spelling_test(message.author, message.channel, word_count)

    if args[0] == "!challenge":
        if len(args) == 2:
            opponent = None
            for user in client.get_all_members():
                if user.mention == args[1]:
                    opponent = user
            if not opponent:
                await client.send_message(message.channel, "Opponent not found.")
            else:
                await client.send_message(message.channel, "{} has challenged {}!".format(message.author.mention, opponent.mention))
                await client.send_message(message.channel, "{}, do you accept this challenge? [y/n]".format(opponent.mention))
                response = await client.wait_for_message(author=opponent, channel=message.channel)
                if response.content.lower() == "y":
                    await client.send_message(message.channel, "Challenge accepted!")
                    await rockpaperscissors(message.channel, message.author, opponent)

    if args[0] == "!leaderboard":
        msg = ""
        c.execute("SELECT * FROM scores")
        for record in c.fetchall():
            score = record[1]
            c.execute("SELECT discord_id FROM users WHERE user_id = ?", (int(record[0]),))
            discord_id = c.fetchone()[0]
            for m in client.get_all_members():
                if m.id == discord_id:
                    msg += "{} : {}".format(m.name, score)
        await client.send_message(message.channel, msg)

async def rockpaperscissors(channel, member, opponent):
    rules = {"r": "s",
             "s": "p",
             "p" : "r"}
    done = False
    turn = 0
    participants = member, opponent
    choices = [None, None]
    while not done:
        # [r, p]
        if choices[0] is not None and choices[1] is not None:
            # r -> s
            # p -> r
            if choices[0] == rules[choices[1]]:
                await client.send_message(channel, opponent.mention + " wins!")
                discord_id = opponent.id
                c.execute("SELECT user_id FROM users WHERE discord_id = ?", (discord_id,))
                user_id = int(c.fetchone()[0])
                c.execute("SELECT wins FROM scores WHERE user_id = ?", (user_id,))
                wins = int(c.fetchone()[0])
                c.execute("UPDATE scores(wins) VALUES(?) WHERE user_id = ?", (wins + 1, user_id))
                conn.commit()
                return
            elif choices[0] == rules[choices[0]]:
                await client.send_message(channel, member.mention + " wins!")
                discord_id = member.id
                c.execute("SELECT user_id FROM users WHERE discord_id = ?", (discord_id,))
                user_id = int(c.fetchone()[0])
                c.execute("SELECT wins FROM scores WHERE user_id = ?", (user_id,))
                wins = int(c.fetchone()[0])
                c.execute("UPDATE scores(wins) VALUES(?) WHERE user_id = ?", (wins + 1, user_id))
                conn.commit()
                return
            else:
                await client.send_message(channel, "It's a draw.")
            choices = [None, None]

        dest = participants[turn]
        # if turn == 0:
        #     await client.send_message(participants[1], "Waiting for opponent...")
        # else:
        #     await client.send_message(participants[0], "Waiting for opponent...")
        pm = await client.send_message(dest, "r, p or s?")
        valid = False
        while not valid:
            response = await client.wait_for_message(author=dest, channel=pm.channel)
            if response.content.lower() in ("r", "p", "s"):
                valid = True
            else:
                await client.send_message(dest, "Please select from 'r', 'p' or 's'")
        n = len(list(choice for choice in choices if choice is not None))
        if n == 0:
            await client.send_message(dest, "Waiting for opponent...")
        choices[turn] = response.content.lower()
        if turn == 0:
            turn = 1
        else:
            turn = 0

async def spelling_test(member, channel, word_count):
    words = ["horse", "dog", "pig", "cat", "antelope", "whale", "fox", "kangaroo", "giraffe"]
    attempts = 0
    for count in range(word_count):
        word = random.choice(words)
        words.remove(word)
        word = word.lower()
        await client.send_message(channel, word)
        correct = False
        while not correct:
            attempts += 1
            msg = await client.wait_for_message(author=member)
            if msg.content.lower() == word:
                correct = True
    await client.send_message(channel, "Attempts: {}".format(attempts))

@client.event
async def on_ready():
    print("Logged in successfully.")
    print("-"*10)
    #await client.send_message(list(channel for channel in client.get_all_channels() if channel.name == "bot-testing")[0], "Bot started.")
    for member in client.get_all_members():
        c.execute("INSERT INTO IF NOT EXISTS users(discord_id) VALUES(?)", (member.id,))
        c.execute("SELECT * FROM users WHERE discord_id = ?", (member.id,))
        print(c.fetchone())
        user_id = c.fetchone()[0]
        c.execute("INSERT INTO IF NOT EXISTS scores(user_id, wins) VALUES(?, ?)", (user_id, 0))
    await ticker()

async def ticker():
    while True:
        await asyncio.sleep(1)
        if timers:
            for t in timers:
                if t.is_done():
                    await client.send_message(t.get_channel(), "Timer set by " + t.get_member().mention + " is done.")
                    timers.remove(t)

@client.event
async def on_member_remove(member):
    print(member.name, "has logged out.")

@client.event
async def on_client_join(member):
    await client.send_message(list(channel for channel in client.get_all_channels() if channel.name == "general"),
                              "Welcome, {}!".format(member.mention))

@client.event
async def on_error(event, *args, **kwargs):
    global debug
    if debug:
        await client.send_message(messages[-1].channel, "Error occurred in coroutine " + str(event))

def on_kill():
    conn.close()
    quit(0)

conn = sqlite3.connect("ellis.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY, discord_id TEXT);")
c.execute("CREATE TABLE IF NOT EXISTS scores(score_id INT PRIMARY KEY, user_id INT, num_wins INT DEFAULT 0);")
conn.commit()
client.run(TOKEN)
