"""去重7/16 + 重算汇总"""
import json

path = '/mnt/c/temp/13yan.github.io/s/data.json'
with open(path) as f:
    data = json.load(f)

# 去重：相同日期+游戏 只保留第一个
seen = {}
unique = []
for s in data['sessions']:
    key = s['date'] + '|' + s['game']
    if key not in seen:
        seen[key] = True
        unique.append(s)
    else:
        print(f"去重: {s['date']} {s['game']} 销售额={s['product']['sales']}")

data['sessions'] = unique

# 去重 salesChannels
seen_sc = {}
unique_sc = []
for sc in data['salesChannels']:
    key = sc['date'] + '|' + sc['game']
    if key not in seen_sc:
        seen_sc[key] = True
        unique_sc.append(sc)
data['salesChannels'] = unique_sc

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
s['estimatedProfit'] = round((total_and + total_ios) * 0.764, 2)
s['profitRate'] = round(s['estimatedProfit'] / (total_and + total_ios) * 100, 1) if (total_and + total_ios) > 0 else 0
data['updatedAt'] = '2026-07-16'

with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n场次: {n}")
print(f"总GMV: {total_gmv:,}")
print(f"总订单: {total_ord}")
print(f"安卓: {total_and:,}")
print(f"iOS: {total_ios:,}")
print("✅ 完成")
