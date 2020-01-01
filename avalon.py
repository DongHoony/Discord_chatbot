import discord
import asyncio

async def avalon(client:discord.Client, channel:discord.TextChannel):
    participants = await avalon_get_participants(client, channel)
    if participants == None:
        return
    print(participants)

# returns set of participants
async def avalon_get_participants(client:discord.Client, channel:discord.TextChannel):
    participants = set()
    game_valid = True
    await channel.send("게임에 참여하시려면 60초 이내로 `!참가`를 입력해주세요.")
    def check(m):
        if m.content == '!참가' and m.channel == channel and m.author not in participants:
            participants.add(m.author)
        return m.content == '!시작' and m.channel == channel and 5 <= len(participants) <= 10
    try:
        await client.wait_for('message', check=check, timeout=60)
    except asyncio.TimeoutError:
        await channel.send("게임 모집 시간이 초과되었습니다. 진행을 취소합니다.")
        game_valid = False

    if game_valid:
        await channel.send(f"{len(participants)}명이 게임에 참여합니다.")
        return list(participants)
    else:
        return None

"""
총 5 라운드로 진행하며, 각 라운드는 < 원정대 구성 > -> <원정 진행> 단계로 이루어진다.

<원정대 구성>
대표가 원정대를 구성할 기사를 지목
모든 플레이어가 투표를 통해 찬/반, 찬성이 과반수이면 통과. 동수면 부결. -> 투표 한 번 하면 다음 사람이 대표(찬/반 관계없이)
>> 5번 거부되면 악이 즉시 승리 <<


<원정 진행>
원정대에 소속된 플레이어들이 원정의 성공/실패 여부 결정
모두 성공을 내야 성공. 한 장이라도 실패가 섞여 있으면 원정 실패
>> 원정을 3번 실패하면 즉시 악의 승리 <<

3회 원정 성공 시, 최후의 발악으로 멀린 암살 시도
>> 멀린이 지목되면 악의 승리 <<
>> 멀린이 지목되지 않으면 선의 승리 <<


"""
