import discord
import asyncio
from avalon_character import *
from collections import deque
import random as r

async def avalon_setup_characters(participants):
    # Players: 5 6 7 8 9 10
    # Goods  : 3 4 4 5 6 6
    # Evils  : 2 2 3 3 3 4

    players_count = len(participants)
    good_count = [0, 1, 0, 0, 2, 3, 4, 4, 5, 6, 6]
    evil_count = [0, 0, 2, 3, 2, 2, 2, 3, 3, 3, 4]

    good_players = []
    evil_players = []

    for i in range(good_count[players_count]):
        current_player = participants.popleft()
        if i == 0:
            good_players.append([current_player, Merlin()])
        else:
            good_players.append([current_player, ArthursServants(i-1)])

    for i in range(evil_count[players_count]):
        current_player = participants.popleft()
        if i == 0:
            evil_players.append([current_player, Assassin()])
        else:
            evil_players.append([current_player, MinionsOfMordred(i-1)])

    return good_players, evil_players

# announce type_cards by dm message
async def avalon_setup_announce(global_channel:discord.TextChannel, good_players:list, evil_players:list):
    for i in good_players:
        channel = await i[0].create_dm()
        embed = discord.Embed(
            title = i[1].name_kr,
            description = i[1].description,
            colour = discord.Colour.blue()
        )
        embed.set_thumbnail(url=i[1].url)
        embed.add_field(name="선악 여부", value='악선'[i[1].side], inline=True)
        await channel.send("당신의 역할 카드입니다.", embed=embed)
    visible_evil_names = [i[0].nick for i in evil_players if type(i[1]) != Oberon]
    for i in evil_players:
        channel = await i[0].create_dm()
        embed = discord.Embed(
            title=i[1].name_kr,
            description=i[1].description,
            colour=discord.Colour.red()
        )
        embed.set_thumbnail(url=i[1].url)
        embed.add_field(name="선악 여부", value='악선'[i[1].side], inline=True)
        visible_evil_names.remove(i[0].nick)
        embed.add_field(name="다른 악 플레이어", value = ", ".join(visible_evil_names))
        visible_evil_names.append(i[0].nick)
        await channel.send("당신의 역할 카드입니다.", embed=embed)

    message = await global_channel.send("역할 카드를 나눠드렸습니다. 3초 후 게임을 시작합니다.")
    # await asyncio.sleep(1)
    # for i in range(2, -1, -1):
    #     await message.edit(content=f"역할 카드를 나눠드렸습니다. {i}초 후 게임을 시작합니다.")
    #     if i == 0:
    #         break
    #     await asyncio.sleep(1)
    await message.edit(content="게임을 시작합니다.")

async def avalon_setup_turn_announce(channel:discord.TextChannel, participants:deque):
    msg = " -> ".join([x.nick for x in participants]) + " -> " + participants[0].nick
    await channel.send("게임 진행 순서는 다음과 같습니다.\n```" + msg + "```")

async def avalon_setup(channel:discord.TextChannel, participants:deque):
    """ DO NOT THROW PARTICIPANTS FOR ARGUMENTS BY RAW """
    good_players, evil_players = await avalon_setup_characters(deque([x for x in participants]))
    await avalon_setup_announce(channel, good_players, evil_players)
    await avalon_setup_turn_announce(channel, participants)
    participants = deque(good_players + evil_players)
    return participants

async def avalon_build_quest_team(players:deque):
    leader = players[0]
    players.rotate(-1)


async def avalon_vote(client:discord.Client, voters:list):
    "voters contains Members"
    UP_EMOJI = "\U0001F44D"
    DOWN_EMOJI = "\U0001F44E"
    msgs = []
    channels = []
    max_voters = len(voters)
    up = down = 0
    users_id = []

    for i in voters:
        channel = await i.create_dm()
        channels.append(channel)
        users_id.append(channel.recipient.id)
        message = await channel.send("투표를 진행합니다. 투표 이후 메시지가 사라지지 않으면 다시 투표해 주세요.")
        await message.add_reaction(UP_EMOJI)
        await message.add_reaction(DOWN_EMOJI)
        msgs.append(message)

    def check(reaction, user):
        if reaction.emoji in [UP_EMOJI, DOWN_EMOJI] and reaction.message.channel in channels and user.id in users_id:
            channels.remove(reaction.message.channel)
            return True
        return False

    for i in range(max_voters):
        reaction, user = await client.wait_for("reaction_add", check=check)
        message = msgs[users_id.index(user.id)]
        await message.delete()
        if reaction.emoji == UP_EMOJI:
            up += 1
            await message.channel.send("투표에 찬성하셨습니다.")
        if reaction.emoji == DOWN_EMOJI:
            down += 1
            await message.channel.send("투표에 반대하셨습니다.")
    return (up, down)

async def avalon(client:discord.Client, channel:discord.TextChannel):
    # type(participants) -> collections.Deque (RANDOMLY SHUFFLED)
    participants = await avalon_get_participants(client, channel)
    if participants == None:
        return
    print(participants)

    "Setup phase"
    participants = await avalon_setup(channel, deque([x for x in participants]))

    "===== repeat below ====="
    "team_building phase"
    await avalon_build_quest_team(participants)

    votes = await avalon_vote(client, [x[0] for x in participants])
    "Quest phase"

# returns set of participants
async def avalon_get_participants(client:discord.Client, channel:discord.TextChannel):
    participants = set()
    game_valid = True
    await channel.send("게임에 참여하시려면 60초 이내로 `!참가`를 입력해주세요.")
    def check(m):
        if m.content == '!참가' and m.channel == channel and m.author not in participants:
            participants.add(m.author)
        return m.content == '!시작' and m.channel == channel and 1 <= len(participants) <= 10
    try:
        await client.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await channel.send("게임 모집 시간이 초과되었습니다. 진행을 취소합니다.")
        game_valid = False

    if game_valid:
        await channel.send(f"{len(participants)}명이 게임에 참여합니다.")
        temp = list(participants)
        r.shuffle(temp)
        return deque(temp)

    else:
        return None

"""
총 5 라운드로 진행하며, 각 라운드는 < 원정대 구성 > -> <원정 진행> 단계로 이루어진다.

<원정대 구성>
대표가 원정대를 구성할 기사를 지목
모든 플레이어가 투표를 통해 찬/반, 찬성이 과반수이면 통과. 동수면 부결. 
-> 투표 한 번 하면 다음 사람이 대표(찬/반 관계없이)
>> 5번 거부되면 악이 즉시 승리 <<


<원정 진행>
원정대에 소속된 플레이어들이 원정의 성공/실패 여부 결정
모두 성공을 내야 성공. 한 장이라도 실패가 섞여 있으면 원정 실패
>> 원정을 3번 실패하면 즉시 악의 승리 <<

3회 원정 성공 시, 최후의 발악으로 멀린 암살 시도
>> 멀린이 지목되면 악의 승리 <<
>> 멀린이 지목되지 않으면 선의 승리 <<


"""
