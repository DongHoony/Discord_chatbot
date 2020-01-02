import discord
import asyncio
from avalon_character import *
from collections import deque
import random as r
import re

async def avalon_setup_characters(participants):
    # Players: 5 6 7 8 9 10
    # Goods  : 3 4 4 5 6 6
    # Evils  : 2 2 3 3 3 4

    players_count = len(participants)
    r.shuffle(participants)

    good_count = [0, 1, 1, 1, 2, 3, 4, 4, 5, 6, 6]
    evil_count = [0, 0, 1, 2, 2, 2, 2, 3, 3, 3, 4]

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
        embed.add_field(name="선악 여부", value='선', inline=True)
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
        embed.add_field(name="선악 여부", value='악', inline=True)
        visible_evil_names.remove(i[0].nick)
        embed.add_field(name="다른 악 플레이어", value = ", ".join(visible_evil_names) if visible_evil_names else '-')
        visible_evil_names.append(i[0].nick)
        await channel.send("당신의 역할 카드입니다.", embed=embed)

    message = await global_channel.send("역할 카드를 나눠드렸습니다. 3초 후 게임을 시작합니다.")
    await asyncio.sleep(1)
    for i in range(2, -1, -1):
        await message.edit(content=f"역할 카드를 나눠드렸습니다. {i}초 후 게임을 시작합니다.")
        if i == 0:
            break
        await asyncio.sleep(1)
    await message.edit(content="게임을 시작합니다.")

async def avalon_setup_turn_announce(channel:discord.TextChannel, participants:deque):
    msg = " -> ".join([x.nick for x in participants]) + " -> " + participants[0].nick
    await channel.send("게임 진행 순서는 다음과 같습니다.\n```" + msg + "```")

async def avalon_setup(channel:discord.TextChannel, participants:deque):
    """ DO NOT THROW PARTICIPANTS FOR ARGUMENTS BY RAW """
    good_players, evil_players = await avalon_setup_characters(deque([x for x in participants]))
    await avalon_setup_announce(channel, good_players, evil_players)
    await avalon_setup_turn_announce(channel, participants)
    participants = [x for x in good_players] + [y for y in evil_players]
    print(f"AFTER SETUP : {deque(participants)}")
    return deque(participants)

"RETURNS QUEST_MEMBER WHICH IS A LIST OF STRING"
async def avalon_build_quest_team(client:discord.Client, channel:discord.TextChannel, players:deque, quest_num):
    leader = players[0]
    print(type(players[0]))
    players.rotate(-1)
    players_id = [str(x[0].id) for x in players]
    quest_member = []
    quest_limit = [[0, 0, 0, 0, 0],
                 [1, 1, 1, 1, 1],
                 [2, 2, 2, 2, 2],
                 [2, 2, 2, 2, 2],
                 [2, 2, 2, 2, 2],
                 [2, 3, 2, 3, 3],
                 [2, 3, 4, 3, 4],
                 [2, 3, 3, 4, 4],
                 [3, 4, 4, 5, 5],
                 [3, 4, 4, 5, 5],
                 [3, 4, 4, 5, 5]]
    cur_quest_limit = quest_limit[len(players)][quest_num]
    await channel.send(f"현재 대표는 <@{leader[0].id}> 입니다. 원정단 {cur_quest_limit}명을 꾸려 주세요.")
    await channel.send("원정단을 선정할 때는 `!원정단 (@플레이어1) (@플레이어2) ...`를 사용합니다. 정확한 플레이어를 언급해주세요.")
    def check(message):
        if message.author.id == leader[0].id and (message.content.startswith("!출발") or message.content.startswith("!원정단")) and message.channel == channel:
            return True
        return False
    while 1:
        valid = True
        message = await client.wait_for("message", check=check)
        if message.content.startswith("!원정단"):

            if len(message.content.split(" "))-1 != cur_quest_limit:
                await channel.send(f"입력하신 원정단 구성원 수`({len(message.content.split(' '))-1})`와 현재 구성해야하는 원정단 구성원 수`({cur_quest_limit})`가 맞지 않습니다.")
                continue

            for raw_user_id in message.content.split(" ")[1:]:
                temp_quest_user_id = [x for x in re.findall("[0-9]*", raw_user_id) if x != '']
                print(temp_quest_user_id)
                if temp_quest_user_id == []:
                    await channel.send("원정단을 선정할 때는 `!원정단 (@플레이어1) (@플레이어2) ...`를 사용합니다. 정확한 플레이어를 언급해주세요.")
                    valid = False
                    break
                temp_quest_user_id = temp_quest_user_id[0]
                if temp_quest_user_id not in players_id:
                    await channel.send(f"언급한 플레이어 <@{temp_quest_user_id}>는 현재 게임에 참여하고 있지 않습니다.")
                    valid = False
                    break
                quest_member.append(temp_quest_user_id)
            if not valid:
                quest_member = []
                continue
            await channel.send(f"원정단을 꾸렸습니다. 표결을 진행하려면 `!출발`을 입력해주세요.\n{', '.join(['<@'+x+'>' for x in quest_member])} ")
            continue
        if message.content.startswith("!출발"):
            if len(quest_member) != cur_quest_limit:
                await channel.send(f"원정에 떠나기 위한 구성원의 수`({cur_quest_limit})`와 현재 구성원의 수`({len(quest_member)})`가 다릅니다.")
                continue
            else:
                break
    return quest_member
        # if message.content == '!출발':
        #     if len(quest_member) == cur_quest_limit:
        #         await channel.send("원정단이 대표에 의해 선정되었습니다. 투표를 통해 원정단을 확정합니다.")
        #     else:
        #         await channel.send(f"원정을 떠나기 위한 원정대 구성원의 수가 맞지 않습니다. {cur_quest_limit}명을 꾸려 주세요. (현재 {len(quest_member)}명)")
        #         continue
        # elif message.content.startswith("!원정단 추가") or message.content.startswith("!원정단 제거"):
        #     delete_member_state = True if message.content.startswith("!원정단 제거") else False
        #     temp_quest_member = message.content.split(" ")[2]
        #     t = re.fullmatch("<@![0-9]*>", str(temp_quest_member)).string
        #     if t == None:
        #         await channel.send("게임에 참여하지 않는 멤버이거나, 잘못 입력하셨습니다. ex) `!원정단 @플레이어`")
        #     else:
        #         temp_quest_member_id = t[3:-1]
        #         if delete_member_state:
        #             #제거
        #             if len(quest_member) == 0:
        #                 await channel.send("원정단에서 제거할 멤버가 존재하지 않습니다.")
        #                 continue
        #             else:
        #                 quest_member.remove(temp_quest_member_id)
        #                 await channel.send(f"원정단 구성원에서 <@{temp_quest_member_id}>를 제거했습니다. (현재 구성원 {len(quest_member)}명)")
        #         else:
        #             #추가
        #             if temp_quest_member_id not in players_id:
        #                 await channel.send("언급한 플레이어는 현재 게임에 참여하고 있지 않습니다.")
        #                 continue
        #             if temp_quest_member_id in quest_member:
        #                 await channel.send("언급한 플레이어는 이미 원정대에 포함돼 있습니다.")
        #                 continue
        #
        #             if (len(quest_member) == cur_quest_limit):
        #                 await channel.send("원정단 구성원이 최대치에 도달했습니다. `!원정단 제거 (@플레이어)`를 통해 구성원 수를 조절하세요.")
        #             else:
        #                 quest_member.append(temp_quest_member_id)
        #                 await channel.send(f"원정단에 <@{temp_quest_member_id}>를 추가합니다. (현재 {len(quest_member)}명)")
        #
        #

async def avalon_vote_quest_team(client:discord.Client, channel:discord.channel, quest_team:list, players:deque, vote_fail_cnt):
    message = await channel.send("원정대 구성에 관한 투표를 진행합니다.")
    if vote_fail_cnt:
        await channel.send(f"현재 투표가 총 `{vote_fail_cnt}회` 거부되었습니다. `5회` 투표가 거부되면 즉시 악이 승리합니다.")
    await asyncio.sleep(2)
    vote_yes, vote_no = await avalon_vote(client, [x[0] for x in players], True)
    vote_success = vote_yes > vote_no

    embed = discord.Embed(
        title="투표 결과",
        description="구성안이 통과되었습니다." if vote_success else "구성안이 거부되었습니다.",
        colour=discord.Colour.blue() if vote_success else discord.Colour.red()
    )
    embed.add_field(name="찬성", value=str(vote_yes), inline=True)
    embed.add_field(name="반대", value=str(vote_no))
    await channel.send("@here 투표 결과입니다.", embed=embed)
    if vote_success:
        return True
    else:
        return False

async def avalon_vote(client:discord.Client, voters:list, is_quest_team_vote:bool):
    "voters contains Members"
    UP_EMOJI = "\U0001F44D" if is_quest_team_vote else "\u2B55"
    DOWN_EMOJI = "\U0001F44E" if is_quest_team_vote else "\u274C"
    msgs = []
    channels = []
    max_voters = len(voters)
    up = down = 0
    users_id = []

    for i in voters:
        channel = await i.create_dm()
        channels.append(channel)
        users_id.append(channel.recipient.id)
        message = await channel.send(("원정대 구성에 관한 " if is_quest_team_vote else "원정 결과에 대한 ") + "투표를 진행합니다.\n투표 이후 메시지가 사라지지 않으면 다시 투표해 주세요.")
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
            await message.channel.send("투표에 찬성하셨습니다." if is_quest_team_vote else "원정 성공에 투표하셨습니다.")
        if reaction.emoji == DOWN_EMOJI:
            down += 1
            await message.channel.send("투표에 반대하셨습니다." if is_quest_team_vote else "원정 실패에 투표하셨습니다.")
    return (up, down)

async def avalon_quest(client:discord.Client, channel:discord.TextChannel, quest_team:list, players:deque):
    await channel.send("원정대에 한해, 원정 성공 여부 투표를 진행합니다.")
    quest_team_members = [x[0] for x in players if str(x[0].id) in quest_team]
    vote_yes, vote_no = await avalon_vote(client, quest_team_members, False)
    if len(quest_team) >= 7:
        vote_success = vote_no < 2
    else:
        vote_success = not vote_no
    embed = discord.Embed(
        title="원정 결과",
        description="원정 진행을 성공하였습니다." if vote_success else "원정 진행을 실패했습니다.",
        colour=discord.Colour.blue() if vote_success else discord.Colour.red()
    )
    embed.add_field(name="원정 성공 표", value=str(vote_yes), inline=True)
    embed.add_field(name="원정 실패 표", value=str(vote_no))
    await channel.send("@here 원정 결과입니다.", embed=embed)
    if vote_success:
        return True
    else:
        return False

async def avalon_board_embed(total_quest_stat):
    embed = discord.Embed(
        title="아발론: 원정 현황",
        description="",
        colour=discord.Colour.green()
    )
    embed.set_footer(text="원정을 세 번 실패하면 악의 승리입니다.")
    for i in range(5):
        embed.add_field(name=f"원정 {i+1}", value="\u2B55" if total_quest_stat[i] == 1 else "\u274C" if total_quest_stat[i] == 0 else "\u2753", inline=True)
    embed.add_field(name="-", value='-', inline=True)
    return embed

async def avalon_assassinate(client:discord.Client, channel:discord.TextChannel, players:deque):
    await channel.send("무사히 3번의 여정을 끝마쳤습니다.")
    assassin = [x[0] for x in players if type(x[1]) == Assassin][0]
    await channel.send(f"암살자 <@{assassin.id}>의 암살 계획이 남아 있습니다.\n멀린으로 의심되는 사람을 상의 후 지목해 주세요.\n`!암살 (@플레이어)`")
    user_id = [str(x[0].id) for x in players]

    def check(message):
        return message.author == assassin and message.content.startswith("!암살") and len(message.content.split(" ")) == 2
    while 1:
        message = await client.wait_for("message", check=check)
        target_id = [x for x in re.findall("[0-9]*", message.content.split(" ")[1]) if x != ""]
        print(target_id)
        if target_id == []:
            await channel.send("정확한 플레이어를 지목해주세요. `!암살 (@플레이어)`")
            continue
        else:
            target_id = target_id[0]
            if target_id not in user_id:
                await channel.send("해당 플레이어는 게임에 속해있지 않습니다.")
                continue
            break

    target = [x[0] for x in players if type(x[1]) == Merlin][0]
    return str(target.id) == target_id

async def avalon_end(channel:discord.TextChannel, players:deque, win_side):
    evil_players = [x for x in players if x[1].side == EVIL]
    good_players = [x for x in players if x[1].side == GOOD]
    print(f"EVIL : {evil_players}")
    print(f"GOOD : {good_players}")
    embed = discord.Embed(
        title="게임 종료",
        description=("선" if win_side == GOOD else "악") + "이 이겼습니다.",
        colour=discord.Colour.red() if win_side == EVIL else discord.Colour.blue()
    )
    for i in good_players:
        embed.add_field(name=i[1].name_kr, value=f"<@{i[0].id}>", inline=True)
    for i in evil_players:
        embed.add_field(name=i[1].name_kr, value=f"<@{i[0].id}>", inline=True)

    await channel.send("@here 게임이 종료되었습니다.", embed=embed)

async def avalon(client:discord.Client, channel:discord.TextChannel):
    # type(participants) -> collections.Deque (RANDOMLY SHUFFLED)
    participants = await avalon_get_participants(client, channel)
    if participants == None:
        return
    print(participants)

    "Setup phase"
    participants = await avalon_setup(channel, deque([x for x in participants]))
    total_quest_stat = [-1] * 5
    "===== repeat below - 5 times ====="

    for i in range(5):
        await channel.send(embed=await avalon_board_embed(total_quest_stat))
        if total_quest_stat.count(0) >= 3:
            await avalon_end(channel, participants, EVIL)
            return
        if total_quest_stat.count(1) == 3:
            result = await avalon_assassinate(client, channel, participants)
            if result:
                await avalon_end(channel, participants, EVIL)
            else:
                await avalon_end(channel, participants, GOOD)
        vote_fail_cnt = 0
        while 1:
            if vote_fail_cnt == 4:
                await avalon_end(channel, participants, EVIL)
                return
            "team_building phase"
            quest_member = await avalon_build_quest_team(client, channel, participants, 0)
            vote_success = await avalon_vote_quest_team(client, channel, quest_member, participants, vote_fail_cnt)
            if vote_success:
                break
            else:
                vote_fail_cnt += 1
        "Quest phase"
        quest_success = await avalon_quest(client, channel, quest_member, participants)
        total_quest_stat[i] = 1 if quest_success else 0

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