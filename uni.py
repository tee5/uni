#!/usr/bin/env python
# coding: utf-8

import re
import logging
import json
import requests
import discord
import ssml
import mstts
import datetime

# setup logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# load settings.json
with open("settings.json") as f:
    try:
        settings = json.load(f)
    except Exception as e:
        logger.fatal()

# define globals
client = discord.Client()
text_channel = None
voice_channel = None
voice_client = None
voice_name = ""

def is_connected():
    print(f"is_connected() S: voice_client={voice_client}")
    if voice_client is None:
        print(f"is_connected() E: False")
        return False
    else:
        print(f"is_connected() E: {voice_client.is_connected()}")
        return voice_client.is_connected()

@client.event
async def on_ready():
    print(f"on_ready() S")
    print(f"Logged in as [{client.user.name}][{client.user.id}]")
    print(f"on_ready() E")

@client.event
async def on_message(message):
    print(f"on_message() S")
    print("client:", type(client), client, dir(client))
    print("client.user:", type(client.user), client.user)
    print("client.user.name:", type(client.user), client.user.name)
    print(dir(client.user))

    print("message:", type(message), message)
    print("message.author:", type(message.author), message.author)
    print("message.author:", type(message.author.name), message.author.name)
    print("message.content:", type(message.content), message.content)
    print(dir(message.author))
    print("message.guild:", message.guild)
    print("message.guild.voice_channels:", message.guild.voice_channels)

    s = format_log_message(message)
    #post_slack(s)
    write_message_log(s)
    global text_channel
    global voice_channel
    global voice_client
    global voice_name

    adjustesd_content = re.sub(" +", " ", message.content)

    # ignore message when auther is me
    if message.author == client.user:
        print(f"message.author == client.user({client.user.name})")
        return
    #
    if client.user not in message.mentions:
        if message.channel != text_channel:
            print("message.channel is not target text_channel")
            return

        print("client.user not in message.mentions")
        #
        if is_connected():
            print("connect status: connected")
            voice = mstts.TextToSpeech(settings["azure"]["subscription_key"])
            filename = voice.save_audio(adjustesd_content, settings["application"]["voice_font"])
            source = discord.FFmpegPCMAudio(filename)
            message.guild.voice_client.play(source)
        else:
            print("connect status: not connected")
            return

    words = adjustesd_content.split(" ")
    print(f"words: {words}")

    #
    if client.user in message.mentions:
        await message.channel.send("調子悪いので調査中⚠️")
        """ CONNECT """
        if words[1].lower() in ("summon", "s"):
            text_channel = message.channel
            voice_channel = None
            for ch in message.guild.voice_channels:
                if message.author in ch.members:
                    voice_channel = ch
                    break
            print(f"text_channel: {text_channel}")
            print(f"voice_channel: {voice_channel}")
            if voice_channel is None:
                await message.channel.send("voice channel not found.")
                return
            voice_client = await voice_channel.connect()
            print(f"voice_client: {voice_client}")
            print(f"is_connected: {is_connected()}")
            await message.channel.send(f"{client.user.name} join to voice channel")
        """ DISCONNECT """
        if words[1].lower() in ("b", "bye"):
            if is_connected():
                await voice_client.disconnect()
                await message.channel.send(f"{client.user.name} leave from voice channel")
            else:
                await message.channel.send(f"{client.user.name} already leaved voice channel.")
        """ LEAVE GUILD """
        if words[1].lower() in ("!leave",):
            await message.channel.send("bye bye")
            await message.guild.leave()
        """ SHOW HELP """
        if words[1].lower() in ("help", "h"):
            s = get_help_message(client)
            await message.channel.send(s)
    print(f"on_message() E")

@client.event
async def on_reaction_add(parameter_list):
    print(f"on_reaction_add() S")
    print("params:", params)
    print(f"on_reaction_add() E")

@client.event
async def on_member_join(member):
    print(f"on_member_join() S")
    print("member:", member.display_name)
    print(f"on_member_join() E")

@client.event
async def on_voice_state_update(member, before, after):
    """ メンバーのボイスチャンネル出入り時に実行されるイベントハンドラ
    """
    print(f"on_voice_state_update() S")
    print("member joined:", member, before, after)
    print(f"on_voice_state_update() E")

def post_slack(message):
    url = "https://hooks.slack.com/services/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"
    payload = {
        "text": message
    }
    requests.post(url, data=json.dumps(payload))

def write_message_log(message):
    with open("message.log", "a") as f:
        f.write(message)

def format_log_message(message):
    s = f"""===============
TIMESTAMP: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
GUILD    : {message.guild.name}
CHANNEL  : {message.channel.name}
AUTHOR   : {message.author.name}
CONTENT  : {message.content}
===============\n"""
    return s

def get_help_message(client):
    s =  """\
```markdown
`@{0} help` or `@{0} h`
    このヘルプを出力

`@{0} s` or `@{0} summon` or `@{0}come` or `@{0} c`
    ボイスチャンネルに接続

`@{0} b` or `@{0} bye` or `@{0} dc`
    ボイスチャンネルから切断
```
""".format(client.user.name)
    return s

client.run(settings["discord"]["access_token"])
