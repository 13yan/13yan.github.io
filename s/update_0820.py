"""追加 8/20 抖店数据（巨兽战场直播日）"""
import json, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('data.json', encoding='utf-8') as f:
    data = json.load(f)

# ===== CSV 8/20 原始数据 =====
# 2026/8/20,巨兽战场,6943,751,12,24,84,2731,10,5.7min,20,830,1,016,41,970,143,13504,8342,16,9
CSV = {
    'date': '2026-08-20', 'game': '巨兽战场',
    'exposure': 6943, 'entry': 751, 'avgOnline': 12, 'maxOnline': 24,
    'comments': 84, 'likes': 2731, 'newFans': 10, 'avgStay': '5.7min',
    'liveSales': 20830.0, 'selfSales': 1016.0, 'paymentOrders': 41,
    'prodExposure': 970, 'prodClicks': 143,
    'androidAmount': 13504, 'androidUsers': 16,
    'iosAmount': 8342, 'iosUsers': 9,
}

# ===== 对账：直播+自营 == 安卓+iOS =====
chk_live_self = CSV['liveSales'] + CSV['selfSales']
chk_pay = CSV['androidAmount'] + CSV['iosAmount']
assert abs(chk_live_self - chk_pay) < 1, f'对账失败: 直播+自营={chk_live_self} != 安卓+iOS={chk_pay}'
print(f'✅ 对账: 直播+自营 = 安卓+iOS = {chk_live_self:,.0f}')
day_pct = CSV['androidAmount'] / chk_pay * 100
print(f'  单日安卓占比: {day_pct:.1f}%', '(中度风险场)' if day_pct > 60 else '')

# ===== 构造 session =====
s = {
    'game': CSV['game'],
    'date': CSV['date'],
    'label': '8月20日直播',
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
    'game': CSV['game'], 'date': CSV['date'], 'label': '8月20日',
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
data['_meta']['lastWrite'] = '2026-08-21'
data['_meta']['lastUpdate'] = {
    'csv': '桌面抖店数据_0716.csv',
    'dates': '8/20',
    'note': f"增量追加1天(8/20直播: 直播20,830+自营1,016=¥21,846; 安卓13,504/16人+iOS8,342/9人; 订单41); totalGMV=574,426"
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ===== 输出对账 =====
print(f"✅ 已追加 {CSV['date']} {CSV['game']}")
print(f"场次: {n}  |  总GMV: {gmv:,.2f} (直播 {live_total:,.2f} + 自营 {self_total:,.2f})")
print(f"订单: {orders}  |  付费用户: {pay_users}  |  安卓占比: {android_share:.1f}% ({ss['androidRisk']})")
print(f"预估利润: {ss['estimatedProfit']:,.2f} (76.4%)")
print(f"8/20 增量核对: 直播 {CSV['liveSales']:,.0f} + 自营 {CSV['selfSales']:,.0f} = {chk_live_self:,.0f}")
print(f"  安卓 {CSV['androidAmount']:,}/{CSV['androidUsers']}人 + iOS {CSV['iosAmount']:,}/{CSV['iosUsers']}人 订单{CSV['paymentOrders']}")
print(f"updatedAt: {now}")
