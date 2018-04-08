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

Entry = namedtuple("Entry", "client event")
entries = [
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event()),
    Entry(client=discord.Client(), event=asyncio.Event())
]

controller = entries[0].client
station_bots = list(entry.client for entry in entries[1:])
help_msg = "Not done yet."

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

class StationBot:
    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.station_name = ""
        self.song_name = ""
        self.channel = None

    def set_channel(self, channel):
        self.channel = channel
        self.station_name = channel.name

    def get_channel(self):
        return self.channel

    def set_voice_client(self, voice_client):
        self.voice_client = voice_client

    def get_voice_client(self):
        return self.voice_client

    def get_bot_client(self):
        return self.bot_client

    def set_song_name(self, song_name):
        self.song_name = song_name

    def get_song_name(self):
        return self.song_name

temp = []
for bot in station_bots:
    station_bot = StationBot(bot)
    temp.append(station_bot)

station_bots = temp

@controller.event
async def on_message(message):
    global debug, current_song, current_player

    args = message.content.split()

    if len(args) == 0:
        return

    if message.author == controller.user:
        return

    if debug == True:
        msg = "Received message from " + message.author.mention + " in channel " + message.channel.mention
        await controller.send_message(message.channel, msg)

    if args[0] == "!hello":
        msg = "Hello, {}".format(message.author.mention)
        await controller.send_message(message.channel, msg)

    if args[0] == "!debug":
        if debug == True:
            debug = False
            msg = "Debugging disabled."
        else:
            debug = True
            msg = "Debugging enabled."

        await controller.send_message(message.channel, msg)

    if args[0] == "!uptime":
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
            msg = "Ellis has been online for {} days, {} hours, {} minutes and {} seconds.".format(days, hours, minutes, seconds)
        elif hours > 0:
            msg = "Ellis has been online for {} hours, {} minutes and {} seconds.".format(hours, minutes, seconds)
        elif minutes > 0:
            msg = "Ellis has been online for {} minutes and {} seconds.".format(minutes, seconds)
        elif seconds > 0:
            msg = "Ellis has been online for {} seconds.".format(seconds)
        await controller.send_message(message.channel, msg)

    if args[0] == "!source":
        msg = repo
        await controller.send_message(message.channel, msg)

    if args[0] == "!help":
        await controller.send_message(message.channel, help_msg)

    if args[0] == "!kill":
        await controller.send_message(message.channel, ":dizzy_face:")
        for e in entries:
            e.client.logout()
        on_kill()

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

    if args[0] == "!create_station":
        if len(args) == 2:
            station_name = args[1]
            c.execute("SELECT * FROM stations")
            stations = list(station for station in c.fetchall() if station[1] == message.server.id)
            if len(stations) < 3:
                await controller.create_channel(message.server, station_name, type=discord.ChannelType.voice)
                c.execute("INSERT INTO stations(server_discord_id, station_name) VALUES(?, ?)", (message.server.id, station_name))
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
            c.execute("SELECT * FROM stations WHERE server_discord_id = ? AND station_name = ?", (message.server.id, station_name))
            station = c.fetchone()
            if not station:
                await controller.send_message(message.channel, "That station does not exist.")
            else:
                await controller.send_message(message.channel, "Starting station...")
                voice_client = None
                voice_channel = None
                for channel in message.server.channels:
                    if channel.name == station_name:
                        voice_channel = channel
                if not voice_channel:
                    await controller.send_message(message.channel, "That station does not exist on the server, but its details are stored in my database. Recreating it...")
                    voice_channel = await controller.create_channel(message.server, station_name, type=discord.ChannelType.voice)
                station_bot = None
                for bot in station_bots:
                    bot_client = bot.get_bot_client()
                    if not bot_client.is_voice_connected(message.server):
                        station_bot = bot
                        voice_client = await bot_client.join_voice_channel(voice_channel)
                        bot.set_channel(voice_channel)
                        bot.set_voice_client(voice_client)
                        break
                if not station_bot.get_voice_client():
                    await controller.send_message(message.channel, "All stations are active.")
                else:
                    song_ids = station[2]
                    songs = parse_raw_song_ids(song_ids)
                    for song in songs:
                        player = await voice_client.create_ytdl_player(song[2])
                        print("Now playing \"{}\"".format(song[3]))
                        station_bot.set_song_name(song[3])
                        player.start()
                        while player.is_playing():
                            await asyncio.sleep(1)
                        player.stop()

    if args[0] == "!song":
        if len(args) == 2:
            song_name = None
            station_name = args[1]
            for bot in station_bots:
                if bot.station_name == station_name:
                    song_name = bot.get_song_name()
            if song_name is not None:
                await controller.send_message(message.channel, song_name)
            else:
                await controller.send_message(message.channel, "No song is currently playing.")

    # if args[0] == "!skip":
    #     if controller.is_voice_connected(message.server) and current_player is not None:
    #         current_player.stop()
    #     if message.author.voice.voice_channel in list

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
c.execute("CREATE TABLE IF NOT EXISTS stations(station_id INTEGER PRIMARY KEY, server_discord_id TEXT, station_name TEXT, song_ids TEXT)")
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