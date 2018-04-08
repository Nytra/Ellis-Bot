import discord
import time
import datetime
import asyncio
import random
import sqlite3
from collections import namedtuple

with open("token.txt", "r") as f:
    tokens = list(line.strip() for line in f.readlines())
    f.close()

repo = "https://github.com/Nytra/Ellis-Bot"

debug = False
start_time = int(time.time())
timers = []
current_song = None
current_player = None

Entry = namedtuple("Entry", "client event")
entries = [
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event())
]

controller = entries[0].client
radio_1 = entries[1].client
radio_2 = entries[2].client
radio_3 = entries[3].client

station_bots = radio_1, radio_2, radio_3

players = {radio_1:None,
           radio_2:None,
           radio_3:None}

songs = {radio_1:None,
         radio_2:None,
         radio_3:None}

stations = {radio_1:None,
            radio_2:None,
            radio_3:None}

help_msg = "none"

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

@controller.event
async def on_message(message):
    global debug, current_song, current_player

    args = message.content.split()

    if len(args) == 0:
        return

    if message.author == controller.user:
        return

    for role in message.author.roles:
        if role.name == "Fortnite Pig":
            msg = "OINK " + message.author.mention
            await controller.send_message(message.channel, msg)

    if debug == True:
        msg = "Received message from " + message.author.mention + " in channel " + message.channel.mention
        await controller.send_message(message.channel, msg)

    if message.content.startswith("!hello"):
        msg = "Hello {0.author.mention}".format(message)
        await controller.send_message(message.channel, msg)

    if message.content.startswith("!pig"):
        msg = "The Fortnite Pig is "
        members = controller.get_all_members()
        for member in members:
            for role in member.roles:
                if role.name == "Fortnite Pig":
                    msg += member.mention
        await controller.send_message(message.channel, msg)

    if message.content.startswith("!poke"):
        parts = message.content.split()
        if len(parts) > 1:
            for member in controller.get_all_members():
                if len(parts) > 1 and member.mention == parts[1]:
                    msg = "*" + message.author.mention + " pokes " + member.mention + "*"
        else:
            msg = "Please provide a target."

        await controller.send_message(message.channel, msg)

    if message.content.startswith("!debug"):
        if debug == True:
            debug = False
            msg = "Debugging disabled."
        else:
            debug = True
            msg = "Debugging enabled."

        await controller.send_message(message.channel, msg)

    if message.content.startswith("!datetime"):
        dt = datetime.datetime.now()
        msg = "[{}/{}/{}] [{}:{}:{}]".format(dt.day,
                                             dt.month,
                                             dt.year,
                                             dt.hour,
                                             dt.minute,
                                             dt.second)
        await controller.send_message(message.channel, msg)

    if debug and message.content.startswith("!dumpvars"):
        msg = "Dumping vars..."
        await controller.send_message(message.channel, msg)
        msg = ""
        for var in globals():
            msg += str(var) + " = " + str(globals()[var]) + "\n"
        await controller.send_message(message.channel, msg)

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
        await controller.send_message(message.channel, msg)

    if message.content.startswith("!source"):
        msg = repo
        await controller.send_message(message.channel, msg)

    if message.content.startswith("!help"):
        await controller.send_message(message.channel, help_msg)

    if message.content.startswith("!kill"):
        await controller.send_message(message.channel, ":dizzy_face:")
        controller.logout()
        on_kill()

    if message.content.startswith("!flip"):
        n = random.randint(0, 1)
        if n == 0:
            msg = "Heads!"
        else:
            msg = "Tails!"
        await controller.send_message(message.channel, msg)

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
        await controller.send_message(message.channel, msg)

    if args[0] == "!hat":
        done = False
        n = 0
        while not done:
            n += 1
            done = True
            m = random.choice(list(ellis.get_all_members()))
            for role in m.roles:
                if role.name == "Bots":
                    done = False
        if debug:
            await controller.send_message(message.channel, str(n) + " iterations")
        msg = m.mention
        await controller.send_message(message.channel, msg)

    if args[0] == "!idiot":
        await controller.send_message(message.channel, "I am an idiot.")

    if args[0] == "!server":
        msg = ""
        for server in controller.servers:
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
            await controller.send_message(message.channel, msg)

    if args[0] == "!timer":
        if len(args) == 2:
            t = int(time.time()) + int(args[1])
            timers.append(Timer(t, message.author, message.channel))
            await controller.send_message(message.channel, "Timer set.")

    if args[0] == "!challenge":
        if len(args) == 2:
            opponent = None
            for user in controller.get_all_members():
                if user.mention == args[1]:
                    opponent = user
            if not opponent:
                await controller.send_message(message.channel, "Opponent not found.")
            else:
                await controller.send_message(message.channel, "{} has challenged {}!".format(message.author.mention, opponent.mention))
                await controller.send_message(message.channel, "{}, do you accept this challenge? [y/n]".format(opponent.mention))
                response = await controller.wait_for_message(timeout=60*3, author=opponent, channel=message.channel)
                if response.content.lower() == "y":
                    await controller.send_message(message.channel, "Challenge accepted!")
                    await rockpaperscissors(message.channel, message.author, opponent)
                elif response == None:
                    await controller.send_message(message.channel, "Opponent did not respond in time.")

    if args[0] == "!leaderboard":
        msg = ""
        c.execute("SELECT * FROM scores ORDER BY num_wins DESC")
        for record in c.fetchall():
            user_id = record[1]
            num_wins = record[2]
            c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            discord_id = c.fetchone()[1]
            for m in controller.get_all_members():
                if m.id == discord_id:
                    msg += "{} : {}\n".format(m.name, num_wins)
        await controller.send_message(message.channel, msg)

    if args[0] == "!tts":
        if len(args) > 1:
            text = " ".join(s for s in args[1:])
            await controller.send_message(message.channel, text, tts=True)

    if args[0] == "!purge":
        if len(args) == 2:
            try:
                int(args[1])
                await controller.send_message(message.channel, "Deleting {} messages...".format(args[1]))
                await asyncio.sleep(2)
                await controller.purge_from(message.channel, limit=int(args[1]))
            except ValueError:
                await controller.send_message(message.channel, "The purge limit must be an integer.")
        else:
            await controller.send_message(message.channel, "Deleting 100 messages...")
            await asyncio.sleep(2)
            await controller.purge_from(message.channel)

    if args[0] == "!create_station":
        if len(args) == 2:
            station_name = args[1]
            c.execute("SELECT * FROM stations")
            stations = c.fetchall()
            if len(stations) < 3:
                await controller.create_channel(message.server, station_name, type=discord.ChannelType.voice)
                c.execute("INSERT INTO stations(station_name) VALUES(?)", (station_name,))
                conn.commit()
                await controller.send_message(message.channel, "The station has been created.")
            else:
                await controller.send_message(message.channel, "The maximum number of stations has been reached.")

    if args[0] == "!playlist":
        if len(args) == 2:
            station_name = args[1]
            c.execute("SELECT * FROM stations WHERE station_name = ?", (station_name,))
            station = c.fetchone()
            if not station:
                await controller.send_message(message.channel, "That station does not exist.")
            else:
                song_ids = station[2]
                msg = ""
                for char in song_ids:
                    try:
                        int(char)
                        c.execute("SELECT * FROM songs WHERE song_id = ?", (char,))
                        song = c.fetchone()
                        song_name = song[3]
                        song_uploader = song[4]
                        song_url = song[2]
                        user_id = song[1]
                        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                        discord_id = c.fetchone()[1]
                        for member in message.server.members:
                            if member.id == discord_id:
                                name = member.name
                        msg += "Title: {}\nUploader: {}\nAdded by: {}\nURL: {}\n\n".format(song_name, song_uploader, name, song_url)
                    except:
                        pass
                await controller.send_message(message.channel, msg)

    if args[0] == "!add_song":
        if len(args) == 3:
            station_name = args[1]
            url = args[2]
            c.execute("SELECT * FROM users WHERE discord_id = ?", (message.author.id,))
            user_id = c.fetchone()[0]

            c.execute("SELECT * FROM stations WHERE station_name = ?", (station_name,))
            #print(c.fetchone())
            station = c.fetchone()
            if not station:
                await controller.send_message(message.channel, "Station \"{}\" does not exist.".format(station_name))
            else:
                await controller.send_message(message.channel, "Adding the song to the playlist...")
                song_ids = station[2]
                if not song_ids:
                    song_ids = ""
                if controller.is_voice_connected(message.server):
                    voice_client = controller.voice_client_in(message.server)
                    voice_client.disconnect()
                else:
                    for channel in message.server.channels:
                        if channel.name == station_name:
                            voice_channel = channel
                            voice_client = await controller.join_voice_channel(voice_channel)
                player = await voice_client.create_ytdl_player(url)
                song_name = player.title
                song_artist = player.uploader
                player.stop()
                voice_client.disconnect()
                c.execute("INSERT INTO songs(user_id, url, song_title, song_artist) VALUES(?, ?, ?, ?)", (user_id, url, song_name, song_artist))
                c.execute("SELECT * FROM songs WHERE url = ?", (url,))
                song_id = c.fetchone()[0]
                c.execute("UPDATE stations SET song_ids = ? WHERE station_name = ?", (song_ids + ",{}".format(song_id), station_name))
                conn.commit()
                await controller.send_message(message.channel, "The song has been added to the playlist.".format(station_name))

    if args[0] == "!start_station":
        if len(args) == 2:
            station_name = args[1]
            c.execute("SELECT * FROM stations WHERE station_name = ?", (station_name,))
            station = c.fetchone()
            if not station:
                await controller.send_message(message.channel, "That station does not exist.")
            else:
                await controller.send_message(message.channel, "Starting station...")
                voice_client = None
                for channel in message.server.channels:
                    if channel.name == station_name:
                        voice_channel = channel
                station_bot = None
                for bot in station_bots:
                    if not bot.is_voice_connected(message.server):
                        voice_client = await bot.join_voice_channel(voice_channel)
                        station_bot = bot
                        stations[station_bot] = voice_channel
                        break
                if not voice_client:
                    await controller.send_message(message.channel, "All stations are active.")
                else:
                    song_ids = station[2]
                    songs = parse_raw_song_ids(song_ids)
                    for song in songs:
                        player = await voice_client.create_ytdl_player(song[2])
                        songs[station_bot] = song[3]
                        players[station_bot] = player
                        print("Now playing \"{}\"".format(song[3]))
                        player.start()
                        while player.is_playing():
                            await asyncio.sleep(1)
                        player.stop()
                    songs[station_bot] = None
                    players[station_bot] = None
                    stations[station_bot] = None

    if args[0] == "!song":
        if len(args) == 2:
            station_name = args[1]
        if current_song is not None:
            await controller.send_message(message.channel, current_song[3])
        else:
            await controller.send_message(message.channel, "No song is currently playing.")

    if args[0] == "!skip":
        if controller.is_voice_connected(message.server) and current_player is not None:
            current_player.stop()

async def rockpaperscissors(channel, member, opponent):
    rules = {"r": "s",
             "s": "p",
             "p" : "r"}
    done = False
    turn = random.choice((0, 1))
    participants = member, opponent
    choices = [None, None]
    while not done:
        # [r, p]
        if choices[0] is not None and choices[1] is not None:
            # r -> s
            # p -> r
            if choices[0] == rules[choices[1]]:
                await controller.send_message(channel, opponent.mention + " wins!")
                discord_id = opponent.id
                c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
                user_id = c.fetchone()[0]
                c.execute("SELECT * FROM scores WHERE user_id = ?", (user_id,))
                num_wins = c.fetchone()[2]
                c.execute("UPDATE scores SET num_wins = ? WHERE user_id = ?", (num_wins + 1, user_id))
                conn.commit()
                return
            elif choices[0] == rules[choices[0]]:
                await controller.send_message(channel, member.mention + " wins!")
                discord_id = member.id
                c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
                user_id = c.fetchone()[0]
                c.execute("SELECT * FROM scores WHERE user_id = ?", (user_id,))
                num_wins = c.fetchone()[2]
                c.execute("UPDATE scores SET num_wins = ? WHERE user_id = ?", (num_wins + 1, user_id))
                conn.commit()
                return
            else:
                await controller.send_message(channel, "It's a draw.")
            choices = [None, None]

        dest = participants[turn]
        # if turn == 0:
        #     await ellis.send_message(participants[1], "Waiting for opponent...")
        # else:
        #     await ellis.send_message(participants[0], "Waiting for opponent...")
        pm = await controller.send_message(dest, "r, p or s?")
        valid = False
        while not valid:
            response = await controller.wait_for_message(author=dest, channel=pm.channel)
            if response.content.lower() in ("r", "p", "s"):
                valid = True
            else:
                await controller.send_message(dest, "Please select from 'r', 'p' or 's'")
        n = len(list(choice for choice in choices if choice is not None))
        if n == 0:
            await controller.send_message(dest, "Waiting for opponent...")
        choices[turn] = response.content.lower()
        if turn == 0:
            turn = 1
        else:
            turn = 0

def parse_raw_song_ids(song_ids):
    songs = []
    for char in song_ids:
        try:
            int(char)
            c.execute("SELECT * FROM songs WHERE song_id = ?", (char,))
            song = c.fetchone()
            songs.append(song)
        except:
            pass
    return songs

@controller.event
async def on_ready():
    print("Ready.")
    for member in list(m for m in controller.get_all_members() if "Bots" not in list(role.name for role in m.roles)):
        c.execute("SELECT * FROM users WHERE discord_id = ?", (member.id,))
        if not c.fetchone():
            c.execute("INSERT INTO users(discord_id) VALUES(?)", (member.id,))
    c.execute("SELECT * FROM users")
    for user in c.fetchall():
        c.execute("SELECT * FROM scores WHERE user_id = ?", (user[0],))
        if not c.fetchone():
            c.execute("INSERT INTO scores(user_id) VALUES(?)", (user[0],))
    conn.commit()
    await ticker()

async def ticker():
    while True:
        await asyncio.sleep(1)
        if timers:
            for t in timers:
                if t.is_done():
                    await controller.send_message(t.get_channel(), "Timer set by " + t.get_member().mention + " is done.")
                    timers.remove(t)

@controller.event
async def on_member_remove(member):
    print(member.name, "has been removed.")

@controller.event
async def on_client_join(member):
    await controller.send_message(list(channel for channel in controller.get_all_channels() if channel.name == "general"),
                              "Welcome, {}!".format(member.mention))

def on_kill():
    conn.close()
    quit(0)

conn = sqlite3.connect("ellis.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, discord_id TEXT);")
c.execute("CREATE TABLE IF NOT EXISTS scores(score_id INTEGER PRIMARY KEY, user_id INTEGER, num_wins INTEGER DEFAULT 0);")
c.execute("CREATE TABLE IF NOT EXISTS stations(station_id INTEGER PRIMARY KEY, station_name TEXT, song_ids TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS songs(song_id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, song_title TEXT, song_artist TEXT)")
conn.commit()
print("Starting...")

loop = asyncio.get_event_loop()

async def login():
    i = 0
    for e in entries:
        await e.client.login(tokens[i])
        i += 1
    print(i, "clients logged in.")

async def wrapped_connect(entry):
    try:
        await entry.client.connect()
    except Exception as e:
        await entry.client.close()
        print("Error: ", e.__class__.__name__, e)
        entry.event.set()

async def check_close():
    futures = [e.event.wait() for e in entries]
    await asyncio.wait(futures)

print("Logging in...")

loop.run_until_complete(login())

print("Connecting...")

for entry in entries:
    loop.create_task(wrapped_connect(entry))

loop.run_until_complete(check_close())

print("Loop complete.")

loop.close()