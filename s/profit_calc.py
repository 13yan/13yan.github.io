"""抖店利润对比（公式验证版）"""
import json

with open('/mnt/c/temp/13yan.github.io/s/data.json') as f:
    data = json.load(f)

sessions = data['sessions']

total = sum(s['product']['sales'] for s in sessions)
android = sum(s['payment']['android']['amount'] for s in sessions)
ios = sum(s['payment']['ios']['amount'] for s in sessions)

print(f"总销售额: {total:,} 元  (安卓: {android:,}  iOS: {ios:,})")
print()

# 正确公式: 利润 = 销售额×85% - 渠道费(从总销售额扣)
# 正常: a×85% + i×75%×85%
# 平台: total×85% - total×1%  
# 抖店: total×85% - total×8% - total×0.6%

nm = android*0.85 + ios*0.75*0.85
pt = total*0.85 - total*0.01
dd = total*0.85 - total*0.08 - total*0.006

print(f"{'场景':<16} {'公式':<35} {'利润':>8} {'利润率':>8}")
print("-" * 68)
print(f"{'正常':<16} {'安卓×85% + iOS×75%×85%':<35} {nm:>8,.0f} {nm/total*100:>7.1f}%")
print(f"{'平台':<16} {'总和×85% - 总和×1%':<35} {pt:>8,.0f} {pt/total*100:>7.1f}%")
print(f"{'抖店':<16} {'总和×85% - 总和×8% - 总和×0.6%':<35} {dd:>8,.0f} {dd/total*100:>7.1f}%")
print("-" * 68)
print(f"{'平台 vs 抖店':<16} {'':<35} {pt-dd:>+8,.0f} {(pt-dd)/total*100:>+7.1f}%")
print(f"{'正常 vs 抖店':<16} {'':<35} {nm-dd:>+8,.0f} {(nm-dd)/total*100:>+7.1f}%")
print(f"{'平台 vs 正常':<16} {'':<35} {pt-nm:>+8,.0f} {(pt-nm)/total*100:>+7.1f}%")
print()

# 逐日明细验证
print("逐日对账:")
print(f"{'日期':<8} {'安卓':>6} {'iOS':>6} {'抖店':>7} {'平台':>7} {'正常':>7}")
for s in sessions:
    a = s['payment']['android']['amount']
    i = s['payment']['ios']['amount']
    d = (a+i)*0.85 - (a+i)*0.08 - (a+i)*0.006
    p = (a+i)*0.85 - (a+i)*0.01
    n = a*0.85 + i*0.75*0.85
    print(f"{s['date'][5:]:<8} {a:>6} {i:>6} {d:>7,.0f} {p:>7,.0f} {n:>7,.0f}")

# 关键验证点
print()
print("=== 关键验证 ===")
print(f"安卓100 → 正常: 100×85% = {100*0.85:.0f}")
print(f"安卓100 → 平台: 100×85% - 100×1% = {100*0.85-100*0.01:.0f}")
print(f"安卓100 → 抖店: 100×85% - 100×8% - 100×0.6% = {100*0.85-100*0.08-100*0.006:.1f}")
print(f"iOS 100 → 正常: 100×75%×85% = {100*0.75*0.85:.2f}")
print(f"iOS 100 → 平台: 100×85% - 100×1% = {100*0.85-100*0.01:.0f}")
print(f"iOS 100 → 抖店: 100×85% - 100×8% - 100×0.6% = {100*0.85-100*0.08-100*0.006:.1f}")
