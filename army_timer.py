from datetime import datetime, timezone, timedelta
import re
KST = timezone(timedelta(hours=9))

army_day    = {"신나무":datetime(2019, 4, 16, 14, 0, 0, tzinfo=KST), "이동훈":datetime(2020, 3, 8, 14, 0, 0, tzinfo=KST), "김용진":datetime(2020, 1, 28, 14, 0, 0, tzinfo=KST)}
freedom_day = {"신나무":datetime(2020, 11, 16, 0, 0, 0, tzinfo=KST), "이동훈":datetime(2022, 1, 8, 0, 0, 0, tzinfo=KST), "김용진":datetime(2021, 7, 27, 0, 0, 0, tzinfo=KST)}
id_to_name = {"206298119661420544":"이동훈", "276706037531279361":"신나무", "228823662864629761":"김용진"}
name_to_id = {"이동훈":"206298119661420544", "신나무":"276706037531279361", "김용진":"228823662864629761"}

def cal_date(name):
    if name not in freedom_day:
        return -1
    if datetime.now(tz=KST) < army_day[name]:
        return army_day[name], True
    else:
        return freedom_day[name], False

def get_name(string):
    if "동훈" in string or "낑깡" in string:
        return "이동훈"
    if "나무" in string:
        return "신나무"
    if "용진" in string or "사과나무" in string:
        return "김용진"
    else:
        return ""

async def cycle(channel, command):
    row = command.content.split(" ")
    if len(row) != 2:
        return -1
    if re.findall("<@.*>", row[1]):
        id = row[1][3:-1]
        if id not in id_to_name:
            return -1
        name = id_to_name[id]
    else:
        name = get_name(row[1])
        id = name_to_id[name]
    time, need_to_go = cal_date(name)
    msg = "입대" if need_to_go else "전역"
    delta = time - datetime.now(tz=KST)  if need_to_go else datetime.now(tz=KST) - time
    days, hours, minutes, seconds = abs(delta.days), delta.seconds // 60 // 60, delta.seconds // 60 % 60, delta.seconds % 60



    message = await channel.send(f"<@{id}> : {msg}까지 `{days}일 {hours}시간 {minutes}분 {seconds}초`, {msg}일 `{time.year}년 {time.month}월 {time.day}일`")



