#!/usr/bin/env python3
"""
抖店工作台 data.json 校验脚本
- 防止 product.sales 误填为合并值
- 防止 salesChannel.self.sales 与 product.sales 重复计算
- 校验 totalGMV = 直播 + 自营
"""
import json
import csv
import sys
import os
from pathlib import Path

DATA = Path(__file__).parent / 'data.json'
CSV_CANDIDATES = [
    # 最新合并 CSV (优先)
    r'E:\抖店数据_2026-07-02~2026-07-30.csv',
    '/mnt/e/抖店数据_2026-07-02~2026-07-30.csv',
    r'/mnt/e/抖店数据_2026-07-02~2026-07-30.csv',
    # 旧版 fallback
    r'E:\抖店数据_2026-07-02~2026-07-28.csv',
    '/mnt/e/抖店数据_2026-07-02~2026-07-28.csv',
    r'/mnt/e/抖店数据_2026-07-02~2026-07-28.csv',
]

def num(s):
    s = s.replace(',','').strip()
    return float(s) if s else 0.0

def load_data():
    with open(DATA, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv():
    for p in CSV_CANDIDATES:
        if os.path.exists(p):
            print(f"📂 CSV 源: {p}")
            with open(p, 'r', encoding='utf-8-sig') as f:
                return [r for r in csv.DictReader(f) if r['日期'] != '合计']
    return None

def check(data, csv_rows):
    errors = []
    warns = []

    # 1. 基础累加
    total_live = sum(s['product']['sales'] for s in data['sessions'])
    total_self = sum(sc['self']['sales'] for sc in data['salesChannels'])
    total_gmv = total_live + total_self
    total_ord = sum(s['product']['paymentOrders'] for s in data['sessions'])
    total_and = sum(s['payment']['android']['amount'] for s in data['sessions'])
    total_ios = sum(s['payment']['ios']['amount'] for s in data['sessions'])

    print("=" * 60)
    print(f"📊 data.json 校验")
    print("=" * 60)
    print(f"场次数:     {len(data['sessions'])}")
    print(f"直播GMV:    ¥{total_live:,.2f}")
    print(f"自营GMV:    ¥{total_self:,.2f}")
    print(f"总GMV:      ¥{total_gmv:,.2f}")
    print(f"支付订单:   {total_ord}")
    print(f"安卓+iOS:   ¥{total_and + total_ios:,.2f}")
    print()

    # 2. 必查项: 重复计算自营
    if csv_rows:
        csv_live  = sum(num(r['直播间销售额(元)']) for r in csv_rows)
        csv_self  = sum(num(r['店铺自营(元)']) for r in csv_rows)
        csv_total = sum(num(r['销售额(元)']) for r in csv_rows)

        print(f"📋 CSV 校验源")
        print(f"CSV 直播累加:  ¥{csv_live:,.2f}")
        print(f"CSV 自营累加:  ¥{csv_self:,.2f}")
        print(f"CSV 销售累加:  ¥{csv_total:,.2f}  ← 注意：此列含直播+自营合并值")
        print(f"CSV 直播+自营: ¥{csv_live + csv_self:,.2f}")
        print()

        # 检查 product.sales 是否误填
        if abs(total_live - csv_live) > 1:
            errors.append(
                f"❌ product.sales 累加 ¥{total_live:,.2f} 与 CSV 直播间销售额累加 "
                f"¥{csv_live:,.2f} 不一致！\n"
                f"   可能原因：把 CSV 销售额(元) 合并列填进了 product.sales"
            )

        # 检查 salesChannel.self.sales
        if abs(total_self - csv_self) > 1:
            errors.append(
                f"❌ self.sales 累加 ¥{total_self:,.2f} 与 CSV 店铺自营累加 "
                f"¥{csv_self:,.2f} 不一致！"
            )

        # 检查 totalGMV
        if abs(total_gmv - (csv_live + csv_self)) > 1:
            errors.append(
                f"❌ totalGMV ¥{total_gmv:,.2f} 与 CSV 直播+自营 "
                f"¥{csv_live + csv_self:,.2f} 不一致！"
            )

    # 3. 检查 _meta
    if '_meta' not in data:
        warns.append("⚠️  data.json 没有 _meta 字段（建议加上 CSV 校验元数据）")
    else:
        meta = data['_meta']
        if 'antiMistake' in meta:
            print("🛡️  _meta 护栏规则:")
            for rule in meta['antiMistake'].get('DO_NOT', []):
                print(f"  - ❌ {rule}")
            for rule in meta['antiMistake'].get('VERIFY_BEFORE_WRITE', []):
                print(f"  - ✅ {rule}")
            print()

    # 4. 检查 sessions 日期连续性
    dates = sorted([s['date'] for s in data['sessions']])
    print(f"📅 日期范围: {dates[0]} ~ {dates[-1]} ({len(dates)} 天)")

    # 5. 检查字段污染
    for i, sc in enumerate(data['salesChannels']):
        if isinstance(sc.get('live'), dict) and 'orders' in sc['live']:
            warns.append(f"⚠️  salesChannel[{i}] 有 live.orders 字段（已废弃）")
        if isinstance(sc.get('self'), dict) and 'orders' in sc['self']:
            warns.append(f"⚠️  salesChannel[{i}] 有 self.orders 字段（已废弃）")
    for i, s in enumerate(data['sessions']):
        if 'orders' in s.get('product', {}):
            warns.append(f"⚠️  session[{i}].product 有 orders 字段（已废弃）")

    # 6. 输出结果
    print()
    if errors:
        print("=" * 60)
        print("❌ 校验失败:")
        for e in errors:
            print(e)
        for w in warns:
            print(w)
        print("=" * 60)
        return False

    print("=" * 60)
    print("✅ 校验通过")
    if warns:
        print("\n警告项:")
        for w in warns:
            print(w)
    print("=" * 60)
    return True

if __name__ == '__main__':
    data = load_data()
    csv_rows = load_csv()
    if csv_rows is None:
        print(f"⚠️  CSV 源文件不存在:")
        for p in CSV_CANDIDATES:
            print(f"   - {p}")
        print("   跳过 CSV 对比，仅检查 data.json 内部一致性")
    ok = check(data, csv_rows)
    sys.exit(0 if ok else 1)
