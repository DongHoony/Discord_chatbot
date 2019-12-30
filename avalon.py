import discord


# returns set of participants
async def avalon_get_participants(client:discord.Client, channel:discord.TextChannel):
    participants = set()
    await channel.send("게임에 참여하시려면 `!참가`를 입력해주세요.")
    def check(m):
        if m.content == '!참가' and m.channel == channel and m.author not in participants:
            participants.add(m.author)
        return m.content == '!시작' and m.channel == channel
    await client.wait_for('message', check=check)
    await channel.send(f"{len(participants)}명이 게임에 참여합니다.")
    return participants



