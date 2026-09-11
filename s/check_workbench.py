#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
抖店工作台 s/index.html 完整性自检（2026-09-11 建立）

背景：仓库有多个 agent 并行操作 s/index.html。2026-09-11 15:52 有会话把 7/6 的旧版
（917 行的残缺框架）重新提交覆盖上线，导致侧边栏 logo、概览卡、accent 配色全被削掉。
本脚本用于在任何前端改动后快速确认框架完整。

用法：
    python s/check_workbench.py            # 检查本地 s/index.html
    python s/check_workbench.py --online   # 同时检查线上页面

退出码：0 = 通过，1 = 框架异常（需还原）
基线：git tag s-index-baseline-2375 / git show 960b820:s/index.html（2375 行）
还原：git show 960b820:s/index.html > s/index.html
"""
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 's', 'index.html')

# 必备特征：(标识名, 子串, 最少出现次数)
REQUIRED = [
    ('侧边栏 logo 图标块', 'logo-icon', 2),
    ('侧边栏概览小卡片', 'sidebar-summary', 2),
    ('data.enc 解密器', 'xorDecrypt', 2),
    ('加密数据加载', "fetch('./data.enc')", 1),
    ('全店汇总 tab', '全店汇总', 4),
    ('基础数据报表 tab', '基础数据报表', 2),
    ('抖店充值转移效果分析 tab', '抖店充值转移效果分析', 3),
    ('操作记录 tab', '操作记录', 4),
    ('支付渠道占比情况区块', '支付渠道占比情况', 1),
    ('渠道充值金额占比饼图', '渠道充值金额占比', 2),
    ('渠道充值人数占比饼图', '渠道充值人数占比', 2),
    ('数据风险评估区块', '数据风险评估', 4),
    ('利润方案对比区块', '利润方案对比', 2),
    ('accent-purple 配色变量', '--accent-purple', 1),
    ('warm 配色变量', '--warm', 2),
]

MIN_LINES = 2000          # 基线 2375 行；低于此值判定被削
BASELINE_LINES = 2375


def check_html(text, label):
    lines = text.count('\n') + 1
    problems = []
    for name, needle, min_count in REQUIRED:
        got = text.count(needle)
        if got < min_count:
            problems.append(f'  ✗ {name}: 期望 ≥{min_count} 次，实际 {got} 次（找不到 "{needle}"）')
    if lines < MIN_LINES:
        problems.append(f'  ✗ 文件仅 {lines} 行，低于基线 {BASELINE_LINES} 行（疑似被削短）')

    print(f'--- {label} ---')
    print(f'  行数: {lines}（基线 {BASELINE_LINES}）')
    print(f'  字符数: {len(text)}')
    if problems:
        print(f'  ❌ 框架异常，{len(problems)} 项不达标：')
        for p in problems:
            print(p)
        print('  还原命令: git show 960b820:s/index.html > s/index.html')
    else:
        print(f'  ✅ 框架完整，{len(REQUIRED)} 项特征全部命中')
    print()
    return not problems


def main():
    ok = True

    if not os.path.exists(INDEX):
        print(f'❌ 找不到 {INDEX}')
        return 1
    with open(INDEX, encoding='utf-8') as f:
        local = f.read()
    ok &= check_html(local, '本地 s/index.html')

    # 与基线做精确比对（忽略行尾差异）
    try:
        base = subprocess.run(
            ['git', '-C', ROOT, 'show', '960b820:s/index.html'],
            capture_output=True, check=True).stdout.decode('utf-8')
        diff = subprocess.run(
            ['diff', '--strip-trailing-cr', '-', INDEX],
            input=base.encode('utf-8'), capture_output=True)
        if diff.returncode == 0:
            print('--- 与基线对比 ---\n  ✅ 与 960b820 基线完全一致\n')
        else:
            n = len([l for l in diff.stdout.decode('utf-8', 'replace').splitlines()
                     if l[:1] in '<>'])
            print(f'--- 与基线对比 ---\n  ⚠ 与基线有 {n} 行差异（可能是有意改动，请人工确认）\n')
    except Exception as e:
        print(f'--- 与基线对比 ---\n  （跳过：{type(e).__name__}）\n')

    if '--online' in sys.argv:
        try:
            import urllib.request
            req = urllib.request.Request('https://3ksczx.cloud/s/',
                                         headers={'User-Agent': 'Mozilla/5.0'})
            online = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
            ok &= check_html(online, '线上 https://3ksczx.cloud/s/')
        except Exception as e:
            print(f'--- 线上检查 ---\n  ⚠ 拉取失败：{type(e).__name__}: {e}\n')

    print('=' * 46)
    print('✅ 自检通过' if ok else '❌ 自检未通过 —— 请按上面的还原命令恢复框架')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
