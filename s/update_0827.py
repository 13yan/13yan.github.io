"""追加 8/27 抖店数据（巨兽战场直播日）"""
import json, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

# ===== CSV 8/27 原始数据 =====
# 2026/8/27,巨兽战场,6165,807,22,38,53,971,3,9.6min,25,840,23,362,65,762,101,18926,30276,27,13
RAW = ['2026/8/27', '巨兽战场', '6165', '807', '22', '38', '53', '971', '3', '9.6min', '25840', '23362', '65', '762', '101', '18926', '30276', '27', '13']

def num(v):
    return float(str(v).replace(',', '').strip())

def toint(v):
    return int(num(v))

r = RAW
p = r[0].split('/')
date = f'{p[0]}-{int(p[1]):02d}-{int(p[2]):02d}'
game = r[1]
exposure, entry = toint(r[2]), toint(r[3])
avgOnline, maxOnline = toint(r[4]), toint(r[5])
comments, likes, newFans = toint(r[6]), toint(r[7]), toint(r[8])
stay = r[9]
live, self_sales = num(r[10]), num(r[11])
orders = toint(r[12])
prodExp, prodClick = toint(r[13]), toint(r[14])
andAmt, iosAmt = num(r[15]), num(r[16])
andUsr, iosUsr = toint(r[17]), toint(r[18])

# 对账
chk = live + self_sales
chk2 = andAmt + iosAmt
assert abs(chk - chk2) < 1, f'{date} 对账失败: 直播+自营={chk} != 安卓+iOS={chk2}'
print(f'✅ 对账: 直播+自营 = 安卓+iOS = {chk:,.0f}')

label = f"{int(p[1])}月{int(p[2])}日直播"
s = {
    'game': game, 'date': date, 'label': label,
    'traffic': {
        'exposure': exposure, 'entry': entry,
        'entryRate': round(entry / exposure, 4) if exposure > 0 else 0,
        'avgOnline': avgOnline, 'maxOnline': maxOnline,
    },
    'interaction': {
        'comments': comments,
        'commentRate': round(comments / entry, 4) if entry > 0 else 0,
        'likes': likes,
        'likeRate': round(likes / exposure, 4) if exposure > 0 else 0,
        'avgStay': stay, 'newFans': newFans,
    },
    'product': {
        'sales': live,
        'exposure': prodExp, 'clicks': prodClick,
        'paymentOrders': orders,
        'exposureClickRate': round(prodClick / prodExp, 4) if prodExp > 0 else 0,
        'clickOrderRate': round(orders / prodClick, 4) if prodClick > 0 else 0,
    },
    'payment': {
        'android': {'amount': andAmt, 'settle': andAmt, 'users': andUsr},
        'ios': {'amount': iosAmt, 'settle': iosAmt, 'users': iosUsr},
    },
}
sc = {
    'game': game, 'date': date, 'label': label.replace('直播', ''),
    'live': {'sales': live}, 'self': {'sales': self_sales},
}

assert data['sessions'][-1]['date'] < date, f'{date} 日期顺序异常'
data['sessions'].append(s)
data['salesChannels'].append(sc)
day_pct = andAmt / chk * 100
level = '健康' if day_pct <= 60 else ('中度' if day_pct <= 80 else '高度')
print(f"✅ {date}: 直播 {live:,.0f} + 自营 {self_sales:,.0f} = {chk:,.0f} | 订单{orders} | 安卓占比 {day_pct:.1f}% [{level}]")

# ===== 重算 storeSummary =====
live_total = sum(c['live']['sales'] for c in data['salesChannels'])
self_total = sum(c['self']['sales'] for c in data['salesChannels'])
gmv = live_total + self_total
orders = sum(x['product']['paymentOrders'] for x in data['sessions'])
pay_users = sum(x['payment']['android']['users'] + x['payment']['ios']['users'] for x in data['sessions'])
android_amt = sum(x['payment']['android']['amount'] for x in data['sessions'])
ios_amt = sum(x['payment']['ios']['amount'] for x in data['sessions'])
android_users = sum(x['payment']['android']['users'] for x in data['sessions'])
ios_users = sum(x['payment']['ios']['users'] for x in data['sessions'])
n = len(data['sessions'])

assert abs(gmv - (android_amt + ios_amt)) < 1, f'总GMV {gmv} != 安卓+iOS {android_amt+ios_amt}'

ss = data['storeSummary']
ss['totalGMV'] = round(gmv, 2)
ss['totalOrders'] = orders
ss['totalPayUsers'] = pay_users
ss['estimatedProfit'] = round(gmv * 0.764, 2)
ss['profitRate'] = 76.4
ss['totalSessions'] = n
ss['avgGMV'] = round(gmv / n, 2)
ss['paymentChannels']['android'] = {
    'amount': android_amt, 'users': android_users, 'settle': android_amt,
    'share': round(android_amt / gmv * 100, 1),
}
ss['paymentChannels']['ios'] = {
    'amount': ios_amt, 'users': ios_users, 'settle': ios_amt,
    'share': round(ios_amt / gmv * 100, 1),
}
ss['totalLiveGMV'] = round(live_total, 2)
ss['totalSelfGMV'] = round(self_total, 2)
android_share = android_amt / gmv * 100
ss['androidRisk'] = '健康' if android_share <= 60 else ('中度风险' if android_share <= 80 else '高度风险')

# ===== updatedAt / _meta =====
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data['updatedAt'] = now
data['_meta']['lastWrite'] = '2026-08-28'
data['_meta']['lastUpdate'] = {
    'csv': '桌面抖店数据_0716.csv',
    'dates': '8/27',
    'note': f"增量追加1天(8/27直播: 直播25,840+自营23,362=¥49,202; 安卓18,926/27人+iOS30,276/13人(iOS主导); 订单65); totalGMV=859,186"
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ===== 汇总 =====
print()
print(f"✅ 已追加 1 天，共 {n} 场")
print(f"总GMV: {gmv:,.2f} (直播 {live_total:,.2f} + 自营 {self_total:,.2f})")
print(f"订单: {orders} | 付费用户: {pay_users}")
print(f"安卓占比: {android_share:.2f}% (显示 {ss['paymentChannels']['android']['share']}%) → {ss['androidRisk']}")
print(f"预估利润: {ss['estimatedProfit']:,.2f} (76.4%)")
print(f"updatedAt: {now}")
