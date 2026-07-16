#!/usr/bin/env python3
"""更新抖店数据：追加7月15日数据"""
import json

path = '/mnt/c/temp/13yan.github.io/s/data.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_session = {
    "game": "巨兽战场",
    "date": "2026-07-15",
    "label": "7月15日直播",
    "traffic": {
        "exposure": 1368,
        "entry": 290,
        "entryRate": round(290/1368, 4),
        "avgOnline": 3,
        "maxOnline": 26
    },
    "interaction": {
        "comments": 27,
        "commentRate": round(27/290, 4),
        "likes": 233,
        "likeRate": round(233/290, 4),
        "avgStay": "2.28min",
        "newFans": 0
    },
    "product": {
        "sales": 3126,
        "exposure": 164,
        "clicks": 11,
        "orders": 2,
        "paymentOrders": 2,
        "exposureClickRate": round(11/164, 4),
        "clickOrderRate": round(2/11, 4)
    },
    "payment": {
        "android": {"amount": 2998, "settle": round(2998*0.994, 2), "users": 1},
        "ios": {"amount": 128, "settle": round(128*0.994, 2), "users": 1}
    }
}

data["sessions"].append(new_session)
data["salesChannels"].append({
    "game": "巨兽战场",
    "date": "2026-07-15",
    "label": "7月15日",
    "live": {"sales": 3126, "orders": 2},
    "self": {"sales": 0, "orders": 0}
})

s = data["storeSummary"]
s["totalGMV"] += 3126
s["totalOrders"] += 2
s["totalPayUsers"] += 2
s["totalSessions"] += 1
s["avgGMV"] = round(s["totalGMV"] / s["totalSessions"], 1)
s["paymentChannels"]["android"]["amount"] += 2998
s["paymentChannels"]["android"]["settle"] += round(2998*0.994, 2)
s["paymentChannels"]["android"]["users"] += 1
s["paymentChannels"]["ios"]["amount"] += 128
s["paymentChannels"]["ios"]["settle"] += round(128*0.994, 2)
s["paymentChannels"]["ios"]["users"] += 1
data["updatedAt"] = "2026-07-16"

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已更新")
print(f"   sessions: {len(data['sessions'])} 条")
print(f"   总 GMV: {s['totalGMV']} 元")
print(f"   最新日期: 2026-07-15")
