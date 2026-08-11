#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抖店数据工作台 数据加密脚本
用法: python3 encrypt_data.py [源文件] [输出文件]
  默认: data.json -> data.enc
解密: index.html 内嵌 JS 的 xorDecrypt() 与之对应
密钥与 index.html 中 ENC_KEY 必须一致!
"""
import base64
import os
import sys

# 密钥（与 index.html 的 ENC_KEY 保持一致）
ENC_KEY = "3ksDd2026@workbench#dscs"

def xor_encrypt(data: bytes, key: str) -> bytes:
    kb = key.encode("utf-8")
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "s", "data.json")
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, "s", "data.enc")
    if not os.path.exists(src):
        print(f"错误: 源文件 {src} 不存在")
        sys.exit(1)
    with open(src, "rb") as f:
        raw = f.read()
    enc = xor_encrypt(raw, ENC_KEY)
    b64 = base64.b64encode(enc).decode("ascii")
    with open(dst, "w", encoding="ascii") as f:
        f.write(b64)
    print(f"✓ 已加密: {src} ({len(raw)} bytes) -> {dst} ({len(b64)} chars)")
    print("  请将 data.enc 与 index.html 一起提交推送")

if __name__ == "__main__":
    main()
