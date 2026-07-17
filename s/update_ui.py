#!/usr/bin/env python3
"""更新 renderProfitRow 样式"""
import re

path = '/mnt/c/temp/13yan.github.io/s/index.html'
with open(path, 'r') as f:
    content = f.read()

# 找到函数起始和结束
start = content.find('function renderProfitRow')
end = content.find('function renderProfitCards')
if end == -1:
    end = content.find('</script>')

old_func = content[start:end].rstrip('\n')
print(f"旧函数长度: {len(old_func)}")

new_body = '''function renderProfitRow(containerId, sessions) {
  var p = calcProfit(sessions);
  var vsP = p.dd - p.pt;
  var vsN = p.dd - p.nm;
  containerId.innerHTML =
    '<div style="display:flex;gap:12px;flex-wrap:wrap">'+
    '<div style="flex:1;min-width:180px;background:linear-gradient(135deg,#f0fdf4,#ecfdf5);border:1px solid #86efac;border-radius:12px;padding:14px 18px">'+
      '<div style="font-size:11px;color:#059669;font-weight:500;margin-bottom:2px">抖店支付 · 发行方利润</div>'+
      '<div style="font-size:24px;font-weight:700;color:#059669;letter-spacing:-0.5px">¥' + p.dd.toFixed(2) + '</div>'+
      '<div style="font-size:11px;color:#6b7280;margin-top:4px"><span style="font-weight:600;color:#059669">'+(p.dd/(p.dd+p.pt+p.nm||1)*100).toFixed(2)+'%</span> 利润率(扣0.6%+8%+15%)</div>'+
    '</div>'+
    '<div style="flex:1;min-width:160px;background:linear-gradient(135deg,#fef2f2,#fff);border:1px solid #fecaca;border-radius:12px;padding:14px 18px">'+
      '<div style="font-size:11px;color:#dc2626;font-weight:500;margin-bottom:2px">同比平台支付利润</div>'+
      '<div style="font-size:24px;font-weight:700;color:'+(vsP<0?"#dc2626":"#059669")+';letter-spacing:-0.5px">'+(vsP<0?"":"+")+(vsP/(p.pt||1)*100).toFixed(2)+'%</div>'+
      '<div style="font-size:11px;color:'+(vsP<0?"#dc2626":"#059669")+';margin-top:4px">'+(vsP<0?"":"+")+vsP.toFixed(2)+' 元 · 平台利润 '+p.pt.toFixed(2)+'</div>'+
    '</div>'+
    '<div style="flex:1;min-width:160px;background:linear-gradient(135deg,#f0f9ff,#fff);border:1px solid #b3c5ff;border-radius:12px;padding:14px 18px">'+
      '<div style="font-size:11px;color:#2563eb;font-weight:500;margin-bottom:2px">同比原支付渠道利润</div>'+
      '<div style="font-size:24px;font-weight:700;color:'+(vsN>=0?"#059669":"#dc2626")+';letter-spacing:-0.5px">'+(vsN>=0?"+":"")+(vsN/(p.nm||1)*100).toFixed(2)+'%</div>'+
      '<div style="font-size:11px;color:'+(vsN>=0?"#059669":"#dc2626")+';margin-top:4px">'+(vsN>=0?"+":"")+vsN.toFixed(2)+' 元 · 正常利润 '+p.nm.toFixed(2)+'</div>'+
    '</div>'+
    '</div>';
}
'''

content = content[:start] + new_body + content[end:]

with open(path, 'w') as f:
    f.write(content)
print('✅ 样式已更新')
