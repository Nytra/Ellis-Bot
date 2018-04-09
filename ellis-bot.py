import discord
import time
import datetime
import asyncio
import random
import sqlite3
from collections import namedtuple

# 4 clients
# across many servers
# with many members
# with many channels
# many stations
# many songs

# client.servers
# for server -> server.me returns member instance

with open("token.txt", "r") as f:
    tokens = list(line.strip() for line in f.readlines())
    f.close()

class StationBot:
    def __init__(self, client):
        self.client = client
        self.song = None
        self.channel = None

    def set_channel(self, channel):
        self.channel = channel

    def get_channel(self):
        return self.channel

    def set_voice_client(self, voice_client):
        self.voice_client = voice_client

    def get_voice_client(self):
        return self.voice_client

    def get_client(self):
        return self.client

    def set_song(self, song):
        self.song = song

    def get_song(self):
        return self.song

    def get_member(self):
        return self.channel.server.me


class Song:
    def __init__(self, title, uploader):
        self.title = title
        self.uploader = uploader

    def get_title(self):
        return self.title

    def get_uploader(self):
        return self.uploader

class Station:
    def __init__(self, server, channel):
        self.server = server
        self.channel = channel

    def set_active_dj(self, member):
        pass


repo = "https://github.com/Nytra/Ellis-Bot"
help_msg = "Not done yet."
app_name = "MyRadio"

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
station_bots = list(StationBot(entry.client) for entry in entries[1:])

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
        conn.close()
        quit(0)

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

    if args[0] == "!create":
        if len(args) == 2:
            station_name = args[1]
            c.execute("SELECT * FROM stations WHERE server_discord_id = ?", (message.server.id,))
            stations = c.fetchall()
            if len(stations) < 3:
                channel = await controller.create_channel(message.server, station_name, type=discord.ChannelType.voice)
                c.execute("INSERT INTO stations(server_discord_id, channel_discord_id) VALUES(?, ?)", (message.server.id, channel.id))
                conn.commit()
                await controller.send_message(message.channel, "The station has been created.")
            else:
                await controller.send_message(message.channel, "The maximum number of stations has been reached.")

    if args[0] == "!playlist":
        if len(args) == 2:
            station_name = args[1]
            station_channel = None
            station_server = message.server
            station_record = None

            # find channel
            for channel in message.server.channels:
                if channel.name == station_name:
                    station_channel = channel

            if not station_channel:
                await controller.send_message(message.channel, "That station does not exist.")
            else:

                #find record
                c.execute("SELECT * FROM stations WHERE server_discord_id = ? AND channel_discord_id = ?", (station_server.id, station_channel.id))
                station_record = c.fetchone()
                if not station_record:
                    await controller.send_message(message.channel, "That station does not exist in my database.")
                else:
                    raw_song_ids = station_record[3]
                    songs = parse_raw_song_ids(raw_song_ids)
                    for song in songs:

                        #c.execute("CREATE TABLE IF NOT EXISTS songs(song_id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, song_title TEXT, song_uploader TEXT)")
                        user_id = song[1]
                        song_url = song[2]
                        song_title = song[3]
                        song_uploader = song[4]
                        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                        user = c.fetchone()

                        if not user:
                            msg = "Title: {}\nUploader: {}\nAdded by: Unknown User\nURL: {}\n\n".format(song_title, song_uploader, song_url)
                        else:
                            user_id = user[0]
                            user_name = "Unknown User"
                            for member in message.server.members:
                                if member.id == user_id:
                                    user_name = member.name
                            msg = "Title: {}\nUploader: {}\nAdded by: {}\nURL: {}\n\n".format(song_title, song_uploader, user_name, song_url)
                        await controller.send_message(message.channel, msg)

    if args[0] == "!add":
        if len(args) == 3:
            station_name = args[1]
            station_channel = None
            station_server = message.server
            song_url = args[2]
            c.execute("SELECT * FROM users WHERE discord_id = ?", (message.author.id,))
            user_id = c.fetchone()[0]

            # find channel id
            for channel in message.server.channels:
                if channel.name == station_name:
                    station_channel = channel

            if not station_channel:
                await controller.send_message(message.channel, "That station does not exist.")
            else:
                c.execute("SELECT * FROM stations WHERE server_discord_id = ? AND channel_discord_id = ?", (station_server.id, station_channel.id))
                station_record = c.fetchone()

                if not station_record:
                    await controller.send_message(message.channel, "That channel is not registered as a station.")
                else:
                    await controller.send_message(message.channel, "Adding the song to the playlist...")
                    raw_song_ids = station_record[3]
                    if not raw_song_ids:
                        raw_song_ids = ""
                    if controller.is_voice_connected(message.server):
                        await controller.voice_client_in(message.server).disconnect()
                    voice_client = await controller.join_voice_channel(station_channel)
                    player = await voice_client.create_ytdl_player(song_url)
                    song_title = player.title
                    song_uploader = player.uploader
                    player.stop()
                    voice_client.disconnect()
                    c.execute("INSERT INTO songs(user_id, url, song_title, song_uploader) VALUES(?, ?, ?, ?)", (user_id, song_url, song_title, song_uploader))
                    c.execute("SELECT * FROM songs WHERE url = ?", (song_url,))
                    song_id = c.fetchone()[0]
                    if raw_song_ids == "":
                        c.execute(
                            "UPDATE stations SET song_ids = ? WHERE server_discord_id = ? AND channel_discord_id = ?",
                            (song_id, station_server.id, station_channel.id))
                    else:
                        c.execute("UPDATE stations SET song_ids = ? WHERE server_discord_id = ? AND channel_discord_id = ?",
                                  (raw_song_ids + "," + str(song_id), station_server.id, station_channel.id))
                    conn.commit()
                    await controller.send_message(message.channel, "The song has been added to the playlist.".format(station_name))

    if args[0] == "!start":
        if len(args) == 2:
            station_name = args[1]
            station_channel = None
            station_server = message.server
            for channel in message.server.channels:
                if channel.name == station_name:
                    station_channel = channel
            if station_channel:
                c.execute("SELECT * FROM stations WHERE server_discord_id = ? AND channel_discord_id = ?",
                      (station_server.id, station_channel.id))
                station_record = c.fetchone()
            else:
                station_record = None
            if not station_channel and not station_record:
                await controller.send_message(message.channel, "That station does not exist.")
            elif not station_channel and station_record:
                await controller.send_message(message.channel, "That station does not exist on the server, but its details are stored in my database. Recreating it...")
                station_channel = await controller.create_channel(message.server, station_name, type=discord.ChannelType.voice)
            elif station_channel and not station_record:
                await controller.send_message(message.channel, "That channel is not registered as a station.")

            if station_channel and station_record:
                #await controller.send_message(message.channel, "Starting station...")
                station_bot = None

                # check if any station bots are already active in the channel
                for bot in station_bots:
                    if bot.get_client().is_voice_connected(station_server) and bot.get_voice_client().channel == station_channel:
                        await controller.send_message(message.channel, "That station is already active.")
                        return
                for bot in station_bots:
                    bot_client = bot.get_client()
                    if not bot_client.is_voice_connected(message.server):
                        station_bot = bot
                        voice_client = await bot_client.join_voice_channel(station_channel)
                        station_member = station_server.me
                        #await controller.change_nickname(station_member, "MyRadio DJ")
                        bot.set_channel(station_channel)
                        bot.set_voice_client(voice_client)
                        break
                if station_bot is None:
                    await controller.send_message(message.channel, "All stations are active.")
                else:
                    raw_song_ids = station_record[3]
                    songs = parse_raw_song_ids(raw_song_ids)
                    for song in songs:
                        player = await station_bot.get_voice_client().create_ytdl_player(song[2])
                        print("Now playing \"{}\"".format(song[3]))
                        station_bot.set_song(Song(song[3], song[4]))
                        player.start()
                        while player.is_playing():
                            await asyncio.sleep(1)
                        player.stop()
                    station_bot.get_voice_client().disconnect()

    if args[0] == "!song":
        if len(args) == 2:
            song = None
            station_name = args[1]
            for bot in station_bots:
                channel = bot.get_channel()
                if channel is not None and channel.name == station_name:
                    song = bot.get_song()
            if song is not None:
                msg = "Title: " + song.get_title() + "\nUploaded by: " + song.get_uploader()
                await controller.send_message(message.channel, msg)
            else:
                await controller.send_message(message.channel, "No song is currently playing.")
        else:
            for bot in station_bots:
                channel = bot.get_channel()
                if message.author.voice.voice_channel is not None and channel is not None and channel.name == message.author.voice.voice_channel.name:
                    await controller.send_message(message.channel, "Title: " + bot.get_song().get_title() +
                                                  "\nUploaded by: " + bot.get_song().get_uploader())

    # if args[0] == "!skip":
    #     if controller.is_voice_connected(message.server) and current_player is not None:
    #         current_player.stop()
    #     if message.author.voice.voice_channel in list

def parse_raw_song_ids(raw_song_ids):
    songs = []
    song_ids = raw_song_ids.split(",")
    for id in song_ids:
        c.execute("SELECT * FROM songs WHERE song_id = ?", (id,))
        song = c.fetchone()
        songs.append(song)
    return songs

@controller.event
async def on_ready():
    print("Ready.")
    for member in list(m for m in controller.get_all_members() if "Bots" not in list(role.name for role in m.roles)):
        c.execute("SELECT * FROM users WHERE discord_id = ?", (member.id,))
        if not c.fetchone():
            c.execute("INSERT INTO users(discord_id) VALUES(?)", (member.id,))
    conn.commit()

    controller.edit_profile(username="MyRadio")

@controller.event
async def on_member_join(member):
    for user in list(entry.client.user for entry in entries[1:]):
        if member.id == user.id:
            await controller.change_nickname(member, "MyRadio DJ")

@controller.event
async def on_server_join(server):
    controller.change_nickname(server.me, "MyRadio Controller")

conn = sqlite3.connect("ellis.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, discord_id TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS stations(station_id INTEGER PRIMARY KEY, server_discord_id TEXT, channel_discord_id TEXT, song_ids TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS songs(song_id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, song_title TEXT, song_uploader TEXT)")
conn.commit()
print("Starting...")

loop = asyncio.get_event_loop()

async def login():
    n = 0
    for i, e in enumerate(entries):
        await e.client.login(tokens[i])
        n += 1
    print(n, "clients logged in.")

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