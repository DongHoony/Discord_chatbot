#-*- coding: utf-8 -*-

import rsp_advanced.rsp_db, rsp_advanced.rsp
from avalon.avalon import *
import economy

client = discord.Client()
TOKEN = "NjYwNDk2NjQwNTc0MDk1NDI2.XgnvHQ.zkFv6_akDO4k4GqX1rPlDXun1dA"

async def add_reaction_outsider(message, name_only=False):
    await message.add_reaction(":rla:636572608896172042")
    await message.add_reaction(":ru:636572608917274634")
    await message.add_reaction(":fp:636572608887914513")
    if not name_only:
        await message.add_reaction(":dk:636575955472744468")
        await message.add_reaction(":Tk:640180152994627624")

async def clear(message):
    try:
        cnt = int(message.content.split(" ")[1]) + 1
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
    alert = await message.channel.send(f"{len(deleted)-1}개의 메시지를 삭제했습니다.")
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

    if len(re.findall("겨[^겨레]*레", message.content)) != 0:
        msg = f"<@{message.author.id}> : " + re.sub("겨[^겨레]*레", "아싸", message.content)
        await message.delete()
        message = await message.channel.send(msg)
        await add_reaction_outsider(message)

    if "아싸" in message.content:
        await add_reaction_outsider(message, True)

    if message.content.startswith("!avl"):
        if message.content == "!avl help":
            await avalon_help(message.channel)

        elif message.content == "!avl":
            await avalon(client, message.channel, message.author)

    if message.content.startswith("!rsp"):
        if message.content == ("!rsp init"):
            await rsp_advanced.rsp_db.init(message.guild, message.channel)
        if message.content == ("!rsp"):
            await rsp_advanced.rsp.rsp_cycle(client, message.channel)


    if message.content.startswith("!e"):
        await economy.init(message.guild, message.channel)

client.run(TOKEN)

