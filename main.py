#-*- coding:utf-8 -*-
import discord
from discord.ext import commands
client = discord.Client()
TOKEN = "NjYwNDk2NjQwNTc0MDk1NDI2.XgnrkQ.z7yXey59HcssAmV2_53rx9tfkfk"
from rsp import *
import re

async def add_reaction_outsider(message, name_only=False):
    await message.add_reaction(":rla:636572608896172042")
    await message.add_reaction(":ru:636572608917274634")
    await message.add_reaction(":fp:636572608887914513")
    if not name_only:
        await message.add_reaction(":dk:636575955472744468")
        await message.add_reaction(":Tk:640180152994627624")

async def display_embed(channel):
    embed = discord.Embed(
        title = "EMBEDTITLE",
        description="DESCRIPTION",
        colour=discord.Colour.blue()
    )
    embed.set_footer(text="FOOTER")
    embed.set_image(url="https://tenor.com/view/yuck-gross-disgust-eww-steve-carell-gif-3556274")
    embed.set_thumbnail(url="https://tenor.com/view/yuck-gross-disgust-eww-steve-carell-gif-3556274")
    embed.set_author(icon_url="https://tenor.com/view/yuck-gross-disgust-eww-steve-carell-gif-3556274",
                     name="AUTHOR NAME",
                     url="https://tenor.com/view/yuck-gross-disgust-eww-steve-carell-gif-3556274")
    embed.add_field(name="Field1", value="Value1", inline=False)
    embed.add_field(name="Field2", value="Value2", inline=True)
    embed.add_field(name="Field3", value="Value3", inline=True)
    await channel.send(embed=embed)

async def clear(message):
    try:
        cnt = int(message.content.split(" ")[1])
    except ValueError:
        await message.channel.send("정확한 숫자를 입력해주세요. ex)`!clr 5`")
        return
    except IndexError:
        await message.channel.send("제거할 메시지 개수를 입력해주세요. ex)`!clr 5`")
        return
    if len(message.content.rstrip().split(" ")) != 2:
        await message.channel.send("제거할 메시지의 개수를 한 개만 입력해주세요. ex)`!clr 5`")
        return

    deleted = await message.channel.purge(limit=cnt)
    alert = await message.channel.send(f"{len(deleted)}개의 메시지를 삭제했습니다.")
    await alert.delete(delay=1.5)


@client.event
async def on_ready():
    print(client.user.id)
    print("ready")
    game = discord.Game("이동훈이 봇 테스트")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author.bot:
        return None

    if message.content.startswith("!clr"):
        await clear(message)

    if (type(message.channel) != discord.channel.TextChannel and message.content.startswith("!")):
        await message.channel.send("봇 명령어는 서버 채팅 채널에서 이용해주세요.")
        return

    if message.content.startswith("!안녕"):
        await message.channel.send("안녕하세요")

    if len(re.findall("겨[^겨레]*레", message.content)) != 0:
        msg = f"<@{message.author.id}>" + re.sub("겨[^겨레]*레", "아싸", message.content)
        await message.delete()
        message = await message.channel.send(msg)
        await add_reaction_outsider(message)

    if "아싸" in message.content:
        await add_reaction_outsider(message, True)

    if message.content.startswith("!embed"):
        await display_embed(message.channel)


    if message.content.startswith("!가위바위보"):
        await rsp(client, message.channel)


client.run(TOKEN)

