# Copyright (c) 2020 by Terry Greeniaus.
import struct


class Note:
    '''
    A note starts with a note header, which is then followed by the note name
    as a string padded out to a multiple of 4 bytes and finally by the note
    contents which is also padded to a multiple of 4 bytes.  The format looks
    something like this:

        uint32_t    n_namesz; // Size of name including single NULL-terminator
        uint32_t    n_descsz; // Size of descriptor data following padded name
        uint32_t    n_type;   // Type, i.e. NT_PRSTATUS
        char        name[n_namesz];
        char        pad[n_namesz to multiple of 4];
        n_type      descriptor_data;
        char        pad[n_descsz to multiple of 4];
    '''
    def __init__(self, name, note_type, descriptor):
        self.name       = name
        self.note_type  = note_type
        self.descriptor = descriptor

    def serialize(self):
        data = struct.pack('<LLL', len(self.name) + 1, len(self.descriptor),
                           self.note_type)
        data += self.name.encode() + b'\x00'
        while len(data) % 4:
            data += b'\x00'
        data += self.descriptor
        while len(data) % 4:
            data += b'\x00'

        return data


class NoteSection:
    def __init__(self):
        self.notes = []
        self.data  = b''

    def add_note(self, name, note_type, descriptor):
        n = Note(name, note_type, descriptor)
        self.notes.append(n)
        self.data += n.serialize()

    def add_prstatus(self, pid, sig, regs):
        '''
        Adds an NT_PRSTATUS note to the section.  The regs should be an array
        of 17 or 18 values with the following contents, depending on if FPSCR
        is included:
        
            [r0, ..., r15, xpsr, <fpscr>]
        '''
        assert len(regs) in (17, 18)
        fpvalid = (len(regs) == 18)
        if not fpvalid:
            regs += [0]
        data = struct.pack('<12xH10xL44x18LL', sig, pid, *regs, fpvalid)
        assert len(data) == 148
        self.add_note('CORE', 1, data)

    def add_prpsinfo(self, name, cmdline):
        '''
        Adds an NT_PRPSINFO note to the section.  We include only the process
        name and initial command line.
        '''
        data = struct.pack('<28x15sx79sx', name.encode(), cmdline.encode())
        assert len(data) == 124
        self.add_note('CORE', 3, data)
