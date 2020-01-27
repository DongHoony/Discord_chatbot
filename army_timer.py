from datetime import datetime

army_day    = {"신나무":datetime(2019, 4, 16, 14, 0, 0), "이동훈":datetime(2020, 3, 8, 14, 0, 0), "김용진":datetime(2020, 1, 28, 14, 0, 0)}
freedom_day = {"신나무":datetime(2020, 11, 16, 0, 0, 0), "이동훈":datetime(2022, 1, 8, 0, 0, 0), "김용진":datetime(2021, 7, 27, 0, 0, 0)}
id_to_name = {"206298119661420544":"이동훈", "276706037531279361":"신나무", "228823662864629761":"김용진"}

def cal_date(name):
    if name not in freedom_day:
        return -1
    if datetime.today() < army_day[name]:
        return army_day[name], True
    else:
        return freedom_day[name], False


async def cycle(channel, command):
    row = command.content.split(" ")
    if len(row) != 2:
        return -1

    id = row[1][3:-1]
    if id not in id_to_name:
        return -1
    name = id_to_name[id]
    time, need_to_go = cal_date(name)
    msg = "입대" if need_to_go else "전역"
    delta = time - datetime.today()  if need_to_go else datetime.today() - time
    days, hours, minutes, seconds = abs(delta.days), delta.seconds // 60 // 60, delta.seconds // 60 % 60, delta.seconds % 60
    message = await channel.send(f"<@{id}> : {msg}까지 `{days}일 {hours}시간 {minutes}분 {seconds}초`, {msg}일 `{time.year}년 {time.month}월 {time.day}일`")



