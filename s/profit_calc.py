"""抖店利润对比（公式验证版）

口径变更（2026-09-04 生效，与 s/index.html 的 ddRate() 保持一致）：
  2026-07-02 ~ 2026-09-03（直播期）：抖店利润 = 流水×85% − 流水×8%直播服务费 − 流水×0.6%服务费 − 流水×15%研发分成
                                    ⇒ 合计系数 0.764
  2026-09-04 起（无直播）：          抖店利润 = 流水×85% − 流水×0.6%服务费 − 流水×15%研发分成
                                    ⇒ 合计系数 0.844（免扣 8% 直播服务费）
  切分依据：按场次「日期」的天粒度，date > 2026-09-03 即适用免扣口径。
  平台支付 / 原 iOS 两个对比渠道口径不受本次变更影响。
"""
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, 'data.json'), encoding='utf-8') as f:
    data = json.load(f)

sessions = data['sessions']

DD_LIVE_END = '2026-09-03'          # 直播分成截止日（含当日）


def dd_rate(date_str):
    """按日期返回抖店利润合计系数：0.844（9/4 起，免 8% 直播服务费）/ 0.764（9/3 前）"""
    return 0.844 if (date_str and date_str > DD_LIVE_END) else 0.764


total = sum(s['product']['sales'] for s in sessions)
android = sum(s['payment']['android']['amount'] for s in sessions)
ios = sum(s['payment']['ios']['amount'] for s in sessions)
flow = android + ios
# 页面「利润率」的 GMV 口径：totalGMV = Σ直播销售额 + Σ自营销售额（= storeSummary.totalGMV）
gmv = data.get('storeSummary', {}).get('totalGMV') or flow

print(f"直播销售额: {total:,} 元  (安卓: {android:,}  iOS: {ios:,})")
print(f"支付流水: {flow:,} 元   totalGMV: {gmv:,} 元")
print()

# 正确公式: 利润 = 销售额×85% - 渠道费(从总销售额扣)
# 正常: a×85% + i×75%×85%
# 平台: total×85% - total×1%
# 抖店: total×85% - total×8%(直播服务费，仅 9/3 前) - total×0.6%

nm = android * 0.85 + ios * 0.75 * 0.85
pt = flow * 0.85 - flow * 0.01
# 抖店利润：逐场按日期双段口径累加（不可用总流水统一乘系数）
dd = sum((s['payment']['android']['amount'] + s['payment']['ios']['amount']) * dd_rate(s['date'])
         for s in sessions)

# 分区间明细，便于人工核对
live_flow = sum(s['payment']['android']['amount'] + s['payment']['ios']['amount']
                for s in sessions if dd_rate(s['date']) == 0.764)
noli_flow = flow - live_flow
print(f"直播期(7/2~9/3) 流水 {live_flow:,} 元 × 0.764 = {live_flow * 0.764:,.2f} 元")
print(f"免扣期(9/4 起)  流水 {noli_flow:,} 元 × 0.844 = {noli_flow * 0.844:,.2f} 元")
print(f"抖店利润合计 {dd:,.2f} 元（利润率 {dd / flow * 100:.2f}% / 支付流水口径）")
print(f"抖店利润合计 {dd:,.2f} 元（利润率 {dd / gmv * 100:.2f}% / GMV 口径，页面口径）")
print()

print(f"{'场景':<16} {'公式':<44} {'利润':>12} {'利润率':>8}")
print("-" * 84)
print(f"{'正常':<16} {'安卓×85% + iOS×75%×85%':<44} {nm:>12,.0f} {nm / gmv * 100:>7.1f}%")
print(f"{'平台':<16} {'流水×85% - 流水×1%':<44} {pt:>12,.0f} {pt / gmv * 100:>7.1f}%")
print(f"{'抖店':<16} {'双段：9/3前×0.764，9/4起×0.844':<44} {dd:>12,.0f} {dd / gmv * 100:>7.1f}%")
print("-" * 84)
print(f"{'平台 vs 抖店':<16} {'':<44} {pt - dd:>+12,.0f} {(pt - dd) / gmv * 100:>+7.1f}%")
print(f"{'正常 vs 抖店':<16} {'':<44} {nm - dd:>+12,.0f} {(nm - dd) / gmv * 100:>+7.1f}%")
print(f"{'平台 vs 正常':<16} {'':<44} {pt - nm:>+12,.0f} {(pt - nm) / gmv * 100:>+7.1f}%")
print()

# 逐日明细验证
print("逐日对账:")
print(f"{'日期':<8} {'安卓':>7} {'iOS':>7} {'系数':>6} {'抖店':>9} {'平台':>9} {'正常':>9}")
for s in sessions:
    a = s['payment']['android']['amount']
    i = s['payment']['ios']['amount']
    r = dd_rate(s['date'])
    d = (a + i) * r
    p = (a + i) * 0.85 - (a + i) * 0.01
    n = a * 0.85 + i * 0.75 * 0.85
    print(f"{s['date'][5:]:<8} {a:>7,.0f} {i:>7,.0f} {r:>6.3f} {d:>9,.0f} {p:>9,.0f} {n:>9,.0f}")

# 关键验证点
print()
print("=== 关键验证 ===")
print(f"安卓100 → 正常: 100×85% = {100 * 0.85:.0f}")
print(f"安卓100 → 平台: 100×85% - 100×1% = {100 * 0.85 - 100 * 0.01:.0f}")
print(f"安卓100 → 抖店(9/3前): 100×0.764 = {100 * 0.764:.1f}")
print(f"安卓100 → 抖店(9/4起): 100×0.844 = {100 * 0.844:.1f}")
print(f"iOS 100 → 正常: 100×75%×85% = {100 * 0.75 * 0.85:.2f}")
print(f"iOS 100 → 平台: 100×85% - 100×1% = {100 * 0.85 - 100 * 0.01:.0f}")
print(f"iOS 100 → 抖店(9/3前): 100×0.764 = {100 * 0.764:.1f}")
print(f"iOS 100 → 抖店(9/4起): 100×0.844 = {100 * 0.844:.1f}")
print()
print("=== 与 storeSummary 对账 ===")
ss = data.get('storeSummary', {})
print(f"storeSummary.estimatedProfit = {ss.get('estimatedProfit')}")
print(f"脚本重算                    = {round(dd, 2)}")
print(f"storeSummary.profitRate     = {ss.get('profitRate')}  /  脚本重算 = {round(dd / gmv * 100, 1)}")
print("PASS" if abs(float(ss.get('estimatedProfit', 0)) - dd) < 0.5 else "FAIL: 与 storeSummary 不一致")
