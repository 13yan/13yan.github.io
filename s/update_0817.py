#!/usr/bin/env python3
"""追加 8/17 巨兽战场数据到 data.json（一次性脚本，用完即删）"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json
from pathlib import Path
from datetime import datetime

DATA = Path('C:/temp/13yan.github.io/s/data.json')
data = json.loads(DATA.read_text(encoding='utf-8'))

DATE = '2026-08-17'
assert not any(s['date'] == DATE for s in data['sessions']), '8/17 已存在，勿重复追加'

def r4(x): return round(x, 4)

# --- CSV 2026/8/17 巨兽战场 ---
session = {
    "game": "巨兽战场",
    "date": DATE,
    "label": "8月17日直播",
    "traffic": {"exposure": 6908, "entry": 730, "entryRate": r4(730/6908),
                "avgOnline": 12, "maxOnline": 26},
    "interaction": {"comments": 110, "commentRate": r4(110/730),
                    "likes": 5666, "likeRate": r4(5666/6908),
                    "avgStay": "4.2min", "newFans": 15},
    "product": {"sales": 31722.0, "exposure": 772, "clicks": 161,
                "paymentOrders": 71,
                "exposureClickRate": r4(161/772), "clickOrderRate": r4(71/161)},
    "payment": {"android": {"amount": 22564, "settle": 22564, "users": 13},
                "ios": {"amount": 43448, "settle": 43448, "users": 19}},
}
channel = {"game": "巨兽战场", "date": DATE, "label": "8月17日",
           "live": {"sales": 31722.0}, "self": {"sales": 34290.0}}

data['sessions'].append(session)
data['salesChannels'].append(channel)

# --- 重算 storeSummary ---
ss = data['storeSummary']
total_live = sum(s['product']['sales'] for s in data['sessions'])
total_self = sum(c['self']['sales'] for c in data['salesChannels'])
total = total_live + total_self
a_amt = sum(s['payment']['android']['amount'] for s in data['sessions'])
a_usr = sum(s['payment']['android']['users'] for s in data['sessions'])
i_amt = sum(s['payment']['ios']['amount'] for s in data['sessions'])
i_usr = sum(s['payment']['ios']['users'] for s in data['sessions'])
orders = sum(s['product']['paymentOrders'] for s in data['sessions'])
n = len(data['sessions'])

ss['totalGMV'] = total
ss['totalLiveGMV'] = total_live
ss['totalSelfGMV'] = total_self
ss['totalOrders'] = orders
ss['totalPayUsers'] = a_usr + i_usr
ss['totalSessions'] = n
ss['avgGMV'] = round(total / n, 1)
ss['estimatedProfit'] = round(total * 0.764, 2)  # 抖店口径: ×85% -8% -0.6%
ss['profitRate'] = round(total * 0.764 / total * 100, 1)
ss['paymentChannels'] = {
    "android": {"amount": a_amt, "users": a_usr, "settle": a_amt,
                "share": round(a_amt / total * 100, 1)},
    "ios": {"amount": i_amt, "users": i_usr, "settle": i_amt,
            "share": round(i_amt / total * 100, 1)},
}
ss['androidRisk'] = '健康' if ss['paymentChannels']['android']['share'] < 60 else '偏高'

data['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')

# --- 汇报 ---
print(f'✅ 已追加 {DATE}')
print(f'场次: {n-1} -> {n}')
print(f'总GMV: {total-66012:,.0f} -> {total:,.0f} (+66,012)')
print(f'  直播: {total_live:,.0f} / 自营: {total_self:,.0f}')
print(f'订单: {orders-71} -> {orders}')
print(f'付费用户: {a_usr+i_usr-32} -> {a_usr+i_usr}')
print(f'安卓占比: {ss["paymentChannels"]["android"]["share"]}% ({ss["androidRisk"]})')
print(f'预估利润: {ss["estimatedProfit"]:,.2f} (利润率 {ss["profitRate"]}%)')
print(f'updatedAt: {data["updatedAt"]}')
