#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从尼康 D90 官方固件包 D90_0101.bin 切出 A/B 两段并校验 CRC。

D90 的发布文件是一份**明文单文件固件**：
  - 前 524,290 字节为 A 段（IO 协处理器程序）
  - 紧接着 7,340,032 字节为 B 段（主控 MCU 程序）
两段各自带 2 字节 CRC-16/XMODEM 收尾，整体与 D300 / D300S 解出的净体积完全一致
（524,290 + 7,340,032），三台机器用的是同一套烧录布局。

校验算法：CRC-16/XMODEM（poly 0x1021，init 0x0000，非反射，无输出异或），
以**大端序**存放于每段末 2 字节，覆盖范围为「长度 − 2」字节。
Python 验证：binascii.crc_hqx(data[:-2], 0)
"""
import binascii, struct, os, sys

SRC = "D90_0101.bin"
A_LEN, B_LEN = 524290, 7340032


def main():
    if not os.path.exists(SRC):
        sys.exit("找不到 %s（请与本脚本放在同一目录）" % SRC)
    data = open(SRC, "rb").read()
    if len(data) != A_LEN + B_LEN:
        sys.exit("文件长度异常：%d 字节（预期 %d）" % (len(data), A_LEN + B_LEN))

    a = data[:A_LEN]
    b = data[A_LEN:A_LEN + B_LEN]
    open("D90_A.bin", "wb").write(a)
    open("D90_B.bin", "wb").write(b)

    ca = binascii.crc_hqx(a[:-2], 0)
    cb = binascii.crc_hqx(b[:-2], 0)
    sa = struct.unpack(">H", a[-2:])[0]
    sb = struct.unpack(">H", b[-2:])[0]

    print("D90_A.bin : %8d B   CRC 计算=%04X  存储=%04X   %s" %
          (len(a), ca, sa, "OK" if ca == sa else "FAIL"))
    print("D90_B.bin : %8d B   CRC 计算=%04X  存储=%04X   %s" %
          (len(b), cb, sb, "OK" if cb == sb else "FAIL"))


if __name__ == "__main__":
    main()
