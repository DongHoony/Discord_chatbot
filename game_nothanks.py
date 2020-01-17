import discord
from collections import deque
import game
import random as r



"""
# No thanks:
자신의 토큰의 개수는 비밀이다


"""



async def main(client:discord.Client, channel:discord.TextChannel, author):
    participants = await game.get_participants("노 땡스(No Thanks)", client, channel, author, 3, 7)

    # Game set, participants[0] = [Member, Token amount]
    # Deck => Randomly shuffled
    participants, deck = init(participants)


async def cycle(client:discord.Client, channel:discord.TextChannel, participants:list, deck:list):
    while deck:
        current_number = deck.pop()
        now_player = participants[0]
        await show_number(channel, current_number)



async def show_number(channel, number):
    pass



def init(participants:deque):
    players_num = len(participants)
    numbers = r.sample([x for x in range(3, 36)], 24)
    token = 9 if players_num == 6 else 7 if players_num == 7 else 11
    ret = [[x, token] for x in participants]
    return ret, numbers
