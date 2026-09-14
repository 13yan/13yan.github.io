"""追加 8/18 抖店数据（巨兽战场直播日）"""
import json, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

# ===== CSV 8/18 原始数据 =====
# 2026/8/18,巨兽战场,8029,619,18,35,103,3270,13,9.2min,41170,7276,70,631,135,35572,12874,17,12
CSV = {
    'date': '2026-08-18', 'game': '巨兽战场',
    'exposure': 8029, 'entry': 619, 'avgOnline': 18, 'maxOnline': 35,
    'comments': 103, 'likes': 3270, 'newFans': 13, 'avgStay': '9.2min',
    'liveSales': 41170.0, 'selfSales': 7276.0, 'paymentOrders': 70,
    'prodExposure': 631, 'prodClicks': 135,
    'androidAmount': 35572, 'androidUsers': 17,
    'iosAmount': 12874, 'iosUsers': 12,
}

# ===== 构造 session =====
s = {
    'game': CSV['game'],
    'date': CSV['date'],
    'label': '8月18日直播',
    'traffic': {
        'exposure': CSV['exposure'], 'entry': CSV['entry'],
        'entryRate': round(CSV['entry'] / CSV['exposure'], 4),
        'avgOnline': CSV['avgOnline'], 'maxOnline': CSV['maxOnline'],
    },
    'interaction': {
        'comments': CSV['comments'],
        'commentRate': round(CSV['comments'] / CSV['entry'], 4),
        'likes': CSV['likes'],
        'likeRate': round(CSV['likes'] / CSV['exposure'], 4),
        'avgStay': CSV['avgStay'], 'newFans': CSV['newFans'],
    },
    'product': {
        'sales': CSV['liveSales'],
        'exposure': CSV['prodExposure'], 'clicks': CSV['prodClicks'],
        'paymentOrders': CSV['paymentOrders'],
        'exposureClickRate': round(CSV['prodClicks'] / CSV['prodExposure'], 4),
        'clickOrderRate': round(CSV['paymentOrders'] / CSV['prodClicks'], 4),
    },
    'payment': {
        'android': {'amount': CSV['androidAmount'], 'settle': CSV['androidAmount'], 'users': CSV['androidUsers']},
        'ios': {'amount': CSV['iosAmount'], 'settle': CSV['iosAmount'], 'users': CSV['iosUsers']},
    },
}

# ===== 构造 salesChannel =====
sc = {
    'game': CSV['game'], 'date': CSV['date'], 'label': '8月18日',
    'live': {'sales': CSV['liveSales']}, 'self': {'sales': CSV['selfSales']},
}

# ===== 追加 =====
assert data['sessions'][-1]['date'] < CSV['date'], '日期顺序异常'
data['sessions'].append(s)
data['salesChannels'].append(sc)

# ===== 重算 storeSummary（从 salesChannels 累加）=====
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
data['_meta']['lastWrite'] = '2026-08-19'
data['_meta']['lastUpdate'] = {
    'csv': '桌面抖店数据_0716.csv',
    'dates': '8/18',
    'note': f"增量追加1天(8/18直播: 直播41,170+自营7,276=¥48,446; 安卓35,572/17人+iOS12,874/12人; 订单70); totalGMV=520,606"
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ===== 输出对账 =====
print(f"✅ 已追加 {CSV['date']} {CSV['game']}")
print(f"场次: {n}  |  总GMV: {gmv:,.2f} (直播 {live_total:,.2f} + 自营 {self_total:,.2f})")
print(f"订单: {orders}  |  付费用户: {pay_users}  |  安卓占比: {android_share:.1f}% ({ss['androidRisk']})")
print(f"预估利润: {ss['estimatedProfit']:,.2f} (76.4%)")
print(f"8/18 增量核对: 直播 {CSV['liveSales']:,.0f} + 自营 {CSV['selfSales']:,.0f} = {CSV['liveSales']+CSV['selfSales']:,.0f}")
print(f"  安卓 {CSV['androidAmount']:,}/{CSV['androidUsers']}人 + iOS {CSV['iosAmount']:,}/{CSV['iosUsers']}人 = {CSV['androidAmount']+CSV['iosAmount']:,} 订单{CSV['paymentOrders']}")
print(f"updatedAt: {now}")
