import discord

async def rsp_dm(member:discord.Member, is_draw:bool):
    channel = await member.create_dm()
    message = await channel.send(("비겼습니다. " if is_draw else "") + "`가위`, `바위`, `보` 중 하나를 선택해주세요. 선택 후 메시지가 사라지지 않는다면 다시 선택해 주세요.")
    await message.add_reaction("\u270A")
    await message.add_reaction("\u270C")
    await message.add_reaction("\u270B")
    return message

async def rsp_get_hand(client:discord.Client, p1:discord.Member, p2:discord.member, m1:discord.Message, m2:discord.Message):
    rsp_list = ["\u270A", "\u270C", "\u270B"]
    def check(reaction, user):
        return reaction.emoji in rsp_list and user in (p1, p2)
    reaction, user = await client.wait_for("reaction_add", check=check)
    reaction_idx = rsp_list.index(reaction.emoji)
    message = m1 if user == p1 else m2
    await message.delete()
    await message.channel.send(f"{['주먹', '가위', '보'][reaction_idx]}를 선택하셨습니다.")
    return [reaction_idx, user]

async def rsp_judge(hand_1, hand_2):
    p1_hand, p2_hand = hand_1[0], hand_2[0]
    #주먹가위보 -> 012
    if p1_hand == p2_hand:
        return None
    elif (p1_hand, p2_hand) in ((0, 1), (1, 2), (2, 0)):
        return hand_1, hand_2
    else:
        return hand_2, hand_1

async def rsp(client:discord.Client, channel):
    rsp_list = ["\u270A", "\u270C", "\u270B"]
    participants = set()
    await channel.send("게임에 참여하시려면 `!참가` 를 입력해주세요.")
    def check(m):
        if m.content == '!참가' and m.channel == channel:
            participants.add(m.author)
        return len(participants) == 2
    # player1_message = await client.wait_for('message', check=check)
    # while 1:
    #     player2_message = await client.wait_for('message', check=check)
    #     if player1_message.author != player2_message.author:
    #         break
    #     print("Same player is going to play.. ignoring it")
    await client.wait_for('message', check=check)
    player1, player2 = list(participants)
    await channel.send("게임을 시작합니다. 개인 메시지를 확인해 주세요.")
    # player1 = player1_message.author
    # player2 = player2_message.author
    is_draw = False
    while 1:
        player1_info_message = await rsp_dm(player1, is_draw)
        player2_info_message = await rsp_dm(player2, is_draw)
        hand_1 = await rsp_get_hand(client, player1, player2, player1_info_message, player2_info_message)
        hand_2 = await rsp_get_hand(client, player1, player2, player1_info_message, player2_info_message)
        result = await rsp_judge(hand_1, hand_2)
        if result == None:
            is_draw = True
            continue
        winner, loser = result
        winner_hand, winner_id = winner[0], winner[1].id
        loser_hand, loser_id = loser[0], loser[1].id
        break
    embed = discord.Embed(
        title="가위바위보 결과",
        colour=discord.Colour.purple()
    )
    embed.add_field(name="승자", value=f"<@{winner_id}>", inline=True)
    embed.add_field(name="패자", value=f"<@{loser_id}>", inline=True)
    embed.add_field(name="손", value=f"{rsp_list[winner_hand]} : {rsp_list[loser_hand]}", inline=False)
    await channel.send(embed=embed)
    await channel.send(f"<@{winner_id}> 승!")
    return
