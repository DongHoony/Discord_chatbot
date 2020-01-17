# Practice Database
import discord
import sqlite3

async def init(server:discord.Guild, channel:discord.TextChannel):
    EconomyDB = init_connect()
    init_first(EconomyDB)
    init_make_member_table(EconomyDB, server)
    emb = get_rank(EconomyDB)
    await channel.send(embed=emb)

def init_connect():
    return sqlite3.connect("economy.db", check_same_thread=False)

def init_first(EconomyDB):
    try:
        c = EconomyDB.cursor()
        c.execute(f"""CREATE TABLE member(
                           id TEXT NOT NULL,
                           NAME TEXT NOT NULL,
                           BALANCE INTEGER
                   )""")
    except sqlite3.OperationalError:
        print("Table already exsists, skip making...")

def init_make_member_table(EconomyDB, server:discord.Guild):
    c = EconomyDB.cursor()
    for i in server.members:
        member_id = str(i.id)
        member_nick = i.nick
        print(f"ID : {member_id}, NICK = {member_nick}")
        # STRING SHOULD BE REPRESENTED AS (VARIBALE,) _ COMMA AFTERWORD
        c.execute("SELECT * FROM member WHERE id == (?)", (member_id,))
        fetch = c.fetchone()
        if member_nick == None:
            continue
        if fetch:
            print(f"User {fetch[1]} ({fetch[0]}) already exsists.")
            continue
        c.execute("INSERT INTO member VALUES (?, ?, ?)", (member_id, member_nick, 0,))
        EconomyDB.commit()

def get_rank(EconomyDB):
    c = EconomyDB.cursor()
    c.execute("SELECT * FROM member ORDER BY -BALANCE")
    data = c.fetchall()
    embed = discord.Embed(
        title="순위",
        colour=discord.Colour.gold()
    )
    for i in range(5):
        embed.add_field(name=f"{i+1}위", value=data[i][1], inline=False)
        embed.insert_field_at(2*i+1, name="자금", value=str(data[i][2]), inline=True)
    return embed
