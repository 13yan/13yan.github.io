"""恢复7/15原始数据 + 追加7/16"""
import json

path = '/mnt/c/temp/13yan.github.io/s/data.json'
with open(path) as f:
    data = json.load(f)

# 恢复7/15
for s in data['sessions']:
    if s['date'] == '2026-07-15':
        s['traffic'] = {"exposure":1368,"entry":290,"entryRate":round(290/1368,4),"avgOnline":3,"maxOnline":26}
        s['interaction'] = {"comments":27,"commentRate":round(27/290,4),"likes":233,"likeRate":round(233/290,4),"avgStay":"2.28min","newFans":0}
        s['product'] = {"sales":3126,"exposure":164,"clicks":11,"orders":2,"paymentOrders":2,"exposureClickRate":round(11/164,4),"clickOrderRate":round(2/11,4)}
        s['payment'] = {"android":{"amount":2998,"settle":round(2998*0.994,2),"users":1},"ios":{"amount":128,"settle":round(128*0.994,2),"users":1}}
        print("✅ 7/15已恢复：3126")

# 追加7/16
new = {
    "game":"巨兽战场","date":"2026-07-16","label":"07-16直播",
    "traffic":{"exposure":1821,"entry":363,"entryRate":round(363/1821,4),"avgOnline":3,"maxOnline":17},
    "interaction":{"comments":10,"commentRate":round(10/363,4),"likes":257,"likeRate":round(257/363,4),"avgStay":"1.90min","newFans":1},
    "product":{"sales":4290,"exposure":271,"clicks":36,"orders":11,"paymentOrders":11,"exposureClickRate":round(36/271,4),"clickOrderRate":round(11/36,4)},
    "payment":{"android":{"amount":4110,"settle":round(4110*0.994,2),"users":4},"ios":{"amount":180,"settle":round(180*0.994,2),"users":1}}
}
data['sessions'].append(new)
data['salesChannels'].append({"game":"巨兽战场","date":"2026-07-16","label":"7月16日","live":{"sales":4290,"orders":11},"self":{"sales":0,"orders":0}})
print("✅ 7/16已追加：4290")

# 重算汇总
total_gmv = sum(s['product']['sales'] for s in data['sessions'])
total_ord = sum(s['product']['paymentOrders'] or s['product']['orders'] or 0 for s in data['sessions'])
total_and = sum(s['payment']['android']['amount'] or 0 for s in data['sessions'])
total_ios = sum(s['payment']['ios']['amount'] or 0 for s in data['sessions'])
total_and_u = sum(s['payment']['android']['users'] or 0 for s in data['sessions'])
total_ios_u = sum(s['payment']['ios']['users'] or 0 for s in data['sessions'])
n = len(data['sessions'])

s = data['storeSummary']
s['totalGMV'] = total_gmv
s['totalOrders'] = total_ord
s['totalPayUsers'] = total_and_u + total_ios_u
s['totalSessions'] = n
s['avgGMV'] = round(total_gmv / n, 1)
s['paymentChannels']['android']['amount'] = total_and
s['paymentChannels']['android']['settle'] = round(total_and * 0.994, 2)
s['paymentChannels']['android']['users'] = total_and_u
s['paymentChannels']['ios']['amount'] = total_ios
s['paymentChannels']['ios']['settle'] = round(total_ios * 0.994, 2)
s['paymentChannels']['ios']['users'] = total_ios_u
s['estimatedProfit'] = round((total_and+total_ios) * 0.764, 2)
s['profitRate'] = round(s['estimatedProfit'] / (total_and+total_ios) * 100, 1) if (total_and+total_ios) > 0 else 0
data['updatedAt'] = '2026-07-16'

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n场次: {n}")
print(f"总GMV: {total_gmv:,}")
print(f"总订单: {total_ord}")
print(f"安卓: {total_and:,}")
print(f"iOS: {total_ios:,}")
print("✅ 完成")
