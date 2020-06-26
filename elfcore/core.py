# Copyright (c) 2020 by Terry Greeniaus.
import struct

from .mmap import MemMap


def round_up_pow_2(v, p2):
    return ((v + p2 - 1) & ~(p2 - 1))


class Core:
    EHDR_FORMAT = '<7B9xHHLLLLLHHHHHH'
    EHDR_SIZE   = struct.calcsize(EHDR_FORMAT)

    PHDR_FORMAT = '<LLLLLLLL'
    PHDR_SIZE   = struct.calcsize(PHDR_FORMAT)

    SHDR_FORMAT = '<LLLLLLLLLL'
    SHDR_SIZE   = struct.calcsize(SHDR_FORMAT)

    def __init__(self):
        self.mmaps = []

    def _write_elf_header(self, f):
        data = struct.pack(Core.EHDR_FORMAT,
                           0x7F, 'E', 'L', 'F',
                           1,                # e_ident[4] = ELFCLASS32
                           1,                # e_ident[5] = ELFDATA2LSB
                           1,                # e_ident[6] = EV_CURRENT
                           4,                # e_type     = ET_CORE
                           40,               # e_machine  = EM_ARM
                           1,                # e_version  = EV_CURRENT
                           0,                # e_entry
                           Core.EHDR_SIZE,   # e_phoff
                           0,                # e_shoff
                           0,                # e_flags
                           Core.EHDR_SIZE,   # e_ehsize
                           Core.PHDR_SIZE,   # e_phentsize
                           len(self.mmaps),  # e_phnum
                           Core.SHDR_SIZE,   # e_shentsize
                           0,                # e_shnum
                           0                 # e_shstrndx
                           )
        f.write(data)

    def _write_pt_load_header(self, f, mmap, p_offset, p_align):
        data = struct.pack(Core.PHDR_FORMAT,
                           1,               # p_type = PT_LOAD
                           p_offset,        # p_offset
                           mmap.addr,       # p_vaddr
                           mmap.addr,       # p_paddr
                           len(mmap.data),  # p_filesz
                           len(mmap.data),  # p_memsz
                           0x7,             # p_flags = rwx
                           p_align          # p_align
                           )
        f.write(data)

    def add_mem_map(self, addr, data):
        '''
        Adds the specified chunk of data to the core at the specified virtual
        address.
        '''
        self.mmaps.append(MemMap(addr, data))

    def write(self, path):
        '''
        Writes the core file to the specified path.
        '''
        with open(path, 'wb') as f:
            self.write_to_file_object(f)

    def write_to_file_object(self, f):
        '''
        Writes the core file to the specified file-like object.  It should be
        opened in binary format.
        '''
        # Compute the length of all combined headers and then find where the
        # data offset would be from there based on the data alignment.
        hdr_size    = Core.EHDR_SIZE + len(self.mmaps)*Core.PHDR_SIZE
        data_align  = 4096
        data_offset = round_up_pow_2(hdr_size, data_align)

        # Start with the ELF header.
        self._write_elf_header(f)

        # Now, write a PT_LOAD header for each memory mapping.
        pos = data_offset
        for m in self.mmaps:
            self._write_pt_load_header(m, pos, data_align)
            pos += round_up_pow_2(len(m.data), data_align)

        # Now, write the memory mappings themselves.
        pos = data_offset
        for m in self.mmaps:
            pad = round_up_pow_2(pos, data_align)
            f.write(b'\x00'*pad)
            f.write(m.data)
