"""引力引擎数据采集"""
import subprocess, json, time

def ev(js):
    cmd = ['cmd.exe', '/c', 'cd', '/d', 'C:\\Users\\Administrator', '&&',
           'opencli', 'browser', 'work', 'eval', js]
    r = subprocess.run(cmd, capture_output=True, timeout=45)
    text = r.stdout.decode('gbk', errors='replace')
    for line in text.split('\n'):
        ls = line.strip()
        if ls.startswith('[') or ls.startswith('{'):
            try: return json.loads(ls)
            except: pass
    return text.strip()

# 1. 检查登录和数据量
count = ev("document.querySelectorAll('.rank-child-item').length")
print('可见数据:', count, '条')

# 2. 检查Tab
title = ev("document.title")
print('标题:', title[:80])

# 3. 检查各列数量
cols = ev("JSON.stringify(Array.from(document.querySelectorAll('.rank-list > div')).map(function(el,i){return{idx:i,items:el.querySelectorAll('.rank-child-item').length}}))")
print('各列:', cols)

# 4. 滚动加载
if isinstance(count, (int, float)) and count < 200:
    print('数据不足，滚动加载...')
    for pos in [2000, 4000, 6000, 8000]:
        ev("var s=document.querySelector('#app');s.scrollTop=" + str(pos) + ";void(s.dispatchEvent(new Event('scroll')));")
        time.sleep(1)
    count2 = ev("document.querySelectorAll('.rank-child-item').length")
    print('滚动后:', count2, '条')

# 5. 提取畅销榜（列索引1）
nls = chr(92)+'n'
js_code = """var col=document.querySelectorAll('.rank-list > div')[1];var items=col.querySelectorAll('.rank-child-item');JSON.stringify(Array.from(items).slice(0,100).map(function(el,i){var c=el.querySelector('.rank-center-item');var rt=el.querySelector('.rank-right-item');var parts=(c?c.innerText:'').split('\\n').filter(function(s){return s.trim()});return{rank:i+1,name:parts[0]||'',category:parts[1]||'',company:parts[2]||'',change:rt?rt.innerText.replace(/\\n/g,' ').trim():''}}))"""
data = ev(js_code)
print('畅销榜提取:', len(data) if isinstance(data,list) else 0, '条')
if isinstance(data, list) and len(data) > 0:
    print('Top5:')
    for g in data[:5]:
        print('  #', g['rank'], g['name'], '|', g['category'])
