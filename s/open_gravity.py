"""打开引力引擎"""
import subprocess

cmd = ['cmd.exe', '/c', 
       'cd', '/d', 'C:\\Users\\Administrator', '&&',
       'opencli', 'browser', 'work', 'open', 
       'https://rank.gravity-engine.com/#/']

r = subprocess.run(cmd, capture_output=True, timeout=30)
out = r.stdout.decode('gbk', errors='replace')
err = r.stderr.decode('gbk', errors='replace')
print('stdout:', out[:500])
print('stderr:', err[:300])
