"""滚动加载+检查数据"""
import subprocess, time

def ev(js):
    cmd = ['cmd.exe', '/c', 'cd', '/d', 'C:\\Users\\Administrator', '&&',
           'opencli', 'browser', 'work', 'eval', js]
    r = subprocess.run(cmd, capture_output=True, timeout=30)
    return r.stdout.decode('gbk', errors='replace').strip()

# 滚动
print('滚动加载中...')
for pos in [3000, 6000, 9000, 12000]:
    ev('var s=document.querySelector("#app");s.scrollTop=' + str(pos) + ';void(s.dispatchEvent(new Event("scroll")));')
    time.sleep(1.5)

c = ev('document.querySelectorAll(".rank-child-item").length')
print('总条数:', c)

# 提取畅销榜（列1）
js = """var col=document.querySelectorAll('.rank-list > div')[1];var items=col.querySelectorAll('.rank-child-item');JSON.stringify(Array.from(items).slice(0,100).map(function(el,i){var c=el.querySelector('.rank-center-item');var rt=el.querySelector('.rank-right-item');var parts=(c?c.innerText:'').split(String.fromCharCode(92,110)).filter(function(s){return s.trim()});return{rank:i+1,name:parts[0]||'',category:parts[1]||'',company:parts[2]||'',change:rt?rt.innerText.replace(/\\n/g,' ').trim():''}}))"""
data = ev(js)
print('\nTop10:')
lines = data.split('\n')
for i, line in enumerate(lines):
    if '"rank"' in line:
        print(line[:150])
        if i >= 40:
            break
