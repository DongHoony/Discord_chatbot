import discord

async def avalon(client:discord.Client, channel:discord.TextChannel):
    participants = await avalon_get_participants(client, channel)


# returns set of participants
async def avalon_get_participants(client:discord.Client, channel:discord.TextChannel):
    participants = set()
    await channel.send("게임에 참여하시려면 `!참가`를 입력해주세요.")
    def check(m):
        if m.content == '!참가' and m.channel == channel and m.author not in participants:
            participants.add(m.author)
        if m.content == '!시작' and m.channel == channel:
            if 5 <= len(participants) <= 10:
                return True
            else:
                await channel.send(f"현재 참가하는 게임 인원 : `{len(participants)}명`이 적정인원 `5 - 10`명에 맞지 않습니다.")
    await client.wait_for('message', check=check)
    await channel.send(f"{len(participants)}명이 게임에 참여합니다.")
    return participants



