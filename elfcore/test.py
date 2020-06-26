#!/usr/bin/env python3
import elfcore.core


def main():
    c = elfcore.core.Core()
    c.add_thread()
    c.add_mem_map(0x10000000, b'\xaa'*32768)
    c.write('/tmp/elf.core')


if __name__ == '__main__':
    main()
