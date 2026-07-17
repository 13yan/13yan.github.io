"""修正日期格式+去重+重算汇总"""
import json

path = '/mnt/c/temp/13yan.github.io/s/data.json'
with open(path) as f:
    data = json.load(f)

# 修正日期
for s in data['sessions']:
    if s['date'] == '2026-7-15':
        s['date'] = '2026-07-15'; s['label'] = '07-15直播'
for sc in data['salesChannels']:
    if sc['date'] == '2026-7-15':
        sc['date'] = '2026-07-15'

# 去重（保留后出现的）
seen = {}
for i in range(len(data['sessions'])-1, -1, -1):
    key = data['sessions'][i]['date'] + '|' + data['sessions'][i]['game']
    if key in seen:
        data['sessions'].pop(i)
    else:
        seen[key] = True

seen_sc = {}
for i in range(len(data['salesChannels'])-1, -1, -1):
    key = data['salesChannels'][i]['date'] + '|' + data['salesChannels'][i]['game']
    if key in seen_sc:
        data['salesChannels'].pop(i)
    else:
        seen_sc[key] = True

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
s['avgGMV'] = round(total_gmv / n, 1) if n else 0
s['paymentChannels']['android']['amount'] = total_and
s['paymentChannels']['android']['settle'] = round(total_and * 0.994, 2)
s['paymentChannels']['android']['users'] = total_and_u
s['paymentChannels']['ios']['amount'] = total_ios
s['paymentChannels']['ios']['settle'] = round(total_ios * 0.994, 2)
s['paymentChannels']['ios']['users'] = total_ios_u
s['estimatedProfit'] = round((total_and + total_ios) * 0.764, 2)
s['profitRate'] = round(s['estimatedProfit'] / (total_and + total_ios) * 100, 1) if (total_and + total_ios) > 0 else 0
data['updatedAt'] = '2026-07-16'

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"场次: {n}")
print(f"总GMV: {total_gmv:,}")
print(f"总订单: {total_ord}")
print(f"安卓: {total_and:,}")
print(f"iOS: {total_ios:,}")
print("✅ 修正完成")
