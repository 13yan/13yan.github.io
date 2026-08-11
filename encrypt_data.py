#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抖店/市场资讯工作台 数据加密脚本
用法:
  python3 encrypt_data.py                        # 抖店: s/data.json -> s/data.enc
  python3 encrypt_data.py <src> <dst>            # 指定单文件
  python3 encrypt_data.py --workbench            # 市场资讯工作台全量加密
                                                 #   work/manifest.json -> work/manifest.enc
                                                 #   w/**/report-data.json -> w/**/report-data.enc
解密: 各工作台 index.html 内嵌 JS 的 xorDecrypt() 与之对应
密钥 ENC_KEY 必须与 index.html 中的保持一致!
"""
import base64
import glob
import os
import sys

# 密钥（与抖店 s/index.html、市场资讯 work/index.html 的 ENC_KEY 保持一致）
ENC_KEY = "3ksDd2026@workbench#dscs"

def xor_encrypt(data: bytes, key: str) -> bytes:
    kb = key.encode("utf-8")
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))

def encrypt_file(src, dst):
    if not os.path.exists(src):
        print(f"错误: 源文件 {src} 不存在")
        return False
    with open(src, "rb") as f:
        raw = f.read()
    enc = xor_encrypt(raw, ENC_KEY)
    b64 = base64.b64encode(enc).decode("ascii")
    with open(dst, "w", encoding="ascii") as f:
        f.write(b64)
    print(f"✓ {src} ({len(raw)} bytes) -> {dst} ({len(b64)} chars)")
    return True

def encrypt_workbench(base):
    ok = True
    ok &= encrypt_file(os.path.join(base, "work", "manifest.json"),
                       os.path.join(base, "work", "manifest.enc"))
    files = glob.glob(os.path.join(base, "w", "**", "report-data.json"), recursive=True)
    if not files:
        print("提示: 未找到任何 report-data.json")
    for src in sorted(files):
        ok &= encrypt_file(src, os.path.splitext(src)[0] + ".enc")
    return ok

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1 and sys.argv[1] == "--workbench":
        print("=== 市场资讯工作台全量加密 ===")
        encrypt_workbench(base)
        print("\n完成。请将 manifest.enc 与各 report-data.enc 一起提交推送")
        return
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "s", "data.json")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, "s", "data.enc")
    encrypt_file(src, dst)
    print("请将 data.enc 与 index.html 一起提交推送")

if __name__ == "__main__":
    main()
