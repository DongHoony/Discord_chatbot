import asyncio
import discord
import random as r
from collections import deque

async def get_participants(game_name:str, client:discord.Client, channel:discord.TextChannel, author:discord.Member, min_player, max_player):
    msg = await channel.send(f"{game_name}에 참여하시려면 하단 이모지를 추가해주세요. 시작하시려면 `!시작`을 입력해주세요.\n`제한시간 60초, 주최자 {author.nick}`")
    await msg.add_reaction("\U0001F534")
    cached_msg = [x for x in client.cached_messages if x.id == msg.id][0]
    def check(m):
        return m.content == '!시작' and m.channel == channel and m.author == author
    already_noticed = False
    while 1:
        participants = set()
        try:
            start_message = await client.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await channel.send("게임 모집 시간이 초과되었습니다. 진행을 취소합니다.")
            await msg.delete()
            return None
        await start_message.delete()
        async for user in cached_msg.reactions[0].users():
            if user.bot == False:
                participants.add(user)
        if not min_player <= len(participants) <= max_player:
            lack_message_new = await channel.send(f"플레이어가 부족합니다. `5 ~ 10명`의 플레이어가 필요합니다. (현재 `{len(participants)}`명)")
            if already_noticed:
                await lack_message_old.delete()
            lack_message_old = lack_message_new
            already_noticed = True
            continue
        await channel.send(f"아래 {len(participants)}명이 게임에 참여합니다.\n`{', '.join([x.nick for x in participants])}`")
        participants = deque(participants)
        r.shuffle(participants)
        return participants

