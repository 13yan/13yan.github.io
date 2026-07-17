"""追加7月16日数据"""
import json

path = '/mnt/c/temp/13yan.github.io/s/data.json'
with open(path) as f:
    data = json.load(f)

# 新数据（CSV内容，日期改为07-16）
row = ['2026/7/16', '巨兽战场', '1821', '363', '3', '17', '10', '257', '1', '1.90min', '4290', '11', '271', '36', '4110', '180', '4', '1']
d, game, exp, entry, avg, max_ol, com, likes, fans, stay, sales, orders, p_exp, p_clicks, android_amt, ios_amt, android_usr, ios_usr = row

date_str = '2026-07-16'
sales_n = int(sales)
android_n = int(android_amt)
ios_n = int(ios_amt)
entry_n = int(entry)
exp_n = int(exp)

# 追加 session
new_session = {
    "game": game,
    "date": date_str,
    "label": "07-16直播",
    "traffic": {
        "exposure": exp_n,
        "entry": entry_n,
        "entryRate": round(entry_n/exp_n, 4),
        "avgOnline": int(avg),
        "maxOnline": int(max_ol)
    },
    "interaction": {
        "comments": int(com),
        "commentRate": round(int(com)/entry_n, 4),
        "likes": int(likes),
        "likeRate": round(int(likes)/entry_n, 4),
        "avgStay": stay + "min",
        "newFans": int(fans)
    },
    "product": {
        "sales": sales_n,
        "exposure": int(p_exp),
        "clicks": int(p_clicks),
        "orders": int(orders),
        "paymentOrders": int(orders),
        "exposureClickRate": round(int(p_clicks)/int(p_exp), 4),
        "clickOrderRate": round(int(orders)/int(p_clicks), 4)
    },
    "payment": {
        "android": {"amount": android_n, "settle": round(android_n*0.994,2), "users": int(android_usr)},
        "ios": {"amount": ios_n, "settle": round(ios_n*0.994,2), "users": int(ios_usr)}
    }
}

data['sessions'].append(new_session)
data['salesChannels'].append({
    "game": game, "date": date_str, "label": "7月16日",
    "live": {"sales": sales_n, "orders": int(orders)},
    "self": {"sales": 0, "orders": 0}
})

# 更新汇总
s = data['storeSummary']
s['totalGMV'] += sales_n
s['totalOrders'] += int(orders)
s['totalPayUsers'] += int(android_usr) + int(ios_usr)
s['totalSessions'] += 1
s['avgGMV'] = round(s['totalGMV'] / s['totalSessions'], 1)
s['paymentChannels']['android']['amount'] += android_n
s['paymentChannels']['android']['settle'] += round(android_n * 0.994, 2)
s['paymentChannels']['android']['users'] += int(android_usr)
s['paymentChannels']['ios']['amount'] += ios_n
s['paymentChannels']['ios']['settle'] += round(ios_n * 0.994, 2)
s['paymentChannels']['ios']['users'] += int(ios_usr)
s['estimatedProfit'] = round(sum(s['paymentChannels'][p]['amount'] for p in ['android','ios']) * 0.764, 2)
s['profitRate'] = round(s['estimatedProfit'] / sum(s['paymentChannels'][p]['amount'] for p in ['android','ios']) * 100, 1)

data['updatedAt'] = '2026-07-16'

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已追加 2026-07-16")
print(f"总GMV: {s['totalGMV']:,}")
print(f"总订单: {s['totalOrders']}")
print(f"场次: {s['totalSessions']}")
print(f"安卓: {s['paymentChannels']['android']['amount']:,}")
print(f"iOS: {s['paymentChannels']['ios']['amount']:,}")
