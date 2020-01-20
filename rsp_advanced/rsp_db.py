import discord
import sqlite3

"""
!가위바위보, !rsp
!rsp rank, !rsp stat
"""

async def init(server:discord.Guild, channel:discord.TextChannel):
    rspDB = init_connect()
    init_first(rspDB)
    init_make_member_table(rspDB, server)

def init_connect():
    return sqlite3.connect("rsp.db", check_same_thread=False)

def init_first(rspDB):
    try:
        c = rspDB.cursor()
        c.execute(f"""CREATE TABLE member(
                           id TEXT NOT NULL,
                           NAME TEXT NOT NULL,
                           win INTEGER,
                           lose INTEGER,
                           win_streak INTEGER
                   )""")
    except sqlite3.OperationalError:
        print("Table already exsists, skip making...")

def init_make_member_table(rspDB, server:discord.Guild):
    c = rspDB.cursor()
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
        c.execute("INSERT INTO member VALUES (?, ?, ?, ?, ?)", (member_id, member_nick, 0, 0, 0,))
        rspDB.commit()

def save_result(winner_id, loser_id):
    rspDB = init_connect()
    c = rspDB.cursor()
    c.execute("SELECT * FROM member WHERE id == (?)", (winner_id,))
    id, nick, win, lose, win_streak = c.fetchone()
    c.execute("update member set (id, NAME, win, lose, win_streak) = (id, NAME, ?, lose, ?) where id == (?)", (win+1, win_streak+1, winner_id))

    c.execute("SELECT * FROM member WHERE id == (?)", (loser_id,))
    id, nick, win, lose, win_streak = c.fetchone()
    c.execute("update member set (id, NAME, win, lose, win_streak) = (id, NAME, win, ?, ?) where id == (?)",
              (lose+1, 0, loser_id))
    rspDB.commit()
#