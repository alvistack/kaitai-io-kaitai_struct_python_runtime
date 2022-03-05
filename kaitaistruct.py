import itertools
import sys
import struct
from io import open, BytesIO, SEEK_CUR, SEEK_END  # noqa

PY2 = sys.version_info[0] == 2

# Kaitai Struct runtime streaming API version, defined as per PEP-0396
# standard. Used for two purposes:
#
# * .py files generated by ksc from .ksy check that they import proper
#   KS runtime library by this version number;
# * distribution utils (setup.py) use this when packaging for PyPI
#
__version__ = '0.9'


class KaitaiStruct(object):
    def __init__(self, stream):
        self._io = stream

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self._io.close()

    @classmethod
    def from_file(cls, filename):
        f = open(filename, 'rb')
        try:
            return cls(KaitaiStream(f))
        except Exception:
            # close file descriptor, then reraise the exception
            f.close()
            raise

    @classmethod
    def from_bytes(cls, buf):
        return cls(KaitaiStream(BytesIO(buf)))

    @classmethod
    def from_io(cls, io):
        return cls(KaitaiStream(io))


class KaitaiStream(object):
    def __init__(self, io):
        self._io = io
        self.align_to_byte()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self._io.close()

    # ========================================================================
    # Stream positioning
    # ========================================================================

    def is_eof(self):
        if self.bits_left > 0:
            return False

        io = self._io
        t = io.read(1)
        if t == b'':
            return True
        else:
            io.seek(-1, SEEK_CUR)
            return False

    def seek(self, n):
        self._io.seek(n)

    def pos(self):
        return self._io.tell()

    def size(self):
        # Python has no internal File object API function to get
        # current file / StringIO size, thus we use the following
        # trick.
        io = self._io
        # Remember our current position
        cur_pos = io.tell()
        # Seek to the end of the File object
        io.seek(0, SEEK_END)
        # Remember position, which is equal to the full length
        full_size = io.tell()
        # Seek back to the current position
        io.seek(cur_pos)
        return full_size

    # ========================================================================
    # Integer numbers
    # ========================================================================

    packer_s1 = struct.Struct('b')
    packer_s2be = struct.Struct('>h')
    packer_s4be = struct.Struct('>i')
    packer_s8be = struct.Struct('>q')
    packer_s2le = struct.Struct('<h')
    packer_s4le = struct.Struct('<i')
    packer_s8le = struct.Struct('<q')

    packer_u1 = struct.Struct('B')
    packer_u2be = struct.Struct('>H')
    packer_u4be = struct.Struct('>I')
    packer_u8be = struct.Struct('>Q')
    packer_u2le = struct.Struct('<H')
    packer_u4le = struct.Struct('<I')
    packer_u8le = struct.Struct('<Q')

    # ------------------------------------------------------------------------
    # Signed
    # ------------------------------------------------------------------------

    def read_s1(self):
        return KaitaiStream.packer_s1.unpack(self.read_bytes(1))[0]

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_s2be(self):
        return KaitaiStream.packer_s2be.unpack(self.read_bytes(2))[0]

    def read_s4be(self):
        return KaitaiStream.packer_s4be.unpack(self.read_bytes(4))[0]

    def read_s8be(self):
        return KaitaiStream.packer_s8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_s2le(self):
        return KaitaiStream.packer_s2le.unpack(self.read_bytes(2))[0]

    def read_s4le(self):
        return KaitaiStream.packer_s4le.unpack(self.read_bytes(4))[0]

    def read_s8le(self):
        return KaitaiStream.packer_s8le.unpack(self.read_bytes(8))[0]

    # ------------------------------------------------------------------------
    # Unsigned
    # ------------------------------------------------------------------------

    def read_u1(self):
        return KaitaiStream.packer_u1.unpack(self.read_bytes(1))[0]

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_u2be(self):
        return KaitaiStream.packer_u2be.unpack(self.read_bytes(2))[0]

    def read_u4be(self):
        return KaitaiStream.packer_u4be.unpack(self.read_bytes(4))[0]

    def read_u8be(self):
        return KaitaiStream.packer_u8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_u2le(self):
        return KaitaiStream.packer_u2le.unpack(self.read_bytes(2))[0]

    def read_u4le(self):
        return KaitaiStream.packer_u4le.unpack(self.read_bytes(4))[0]

    def read_u8le(self):
        return KaitaiStream.packer_u8le.unpack(self.read_bytes(8))[0]

    # ========================================================================
    # Floating point numbers
    # ========================================================================

    packer_f4be = struct.Struct('>f')
    packer_f8be = struct.Struct('>d')
    packer_f4le = struct.Struct('<f')
    packer_f8le = struct.Struct('<d')

    # ........................................................................
    # Big-endian
    # ........................................................................

    def read_f4be(self):
        return KaitaiStream.packer_f4be.unpack(self.read_bytes(4))[0]

    def read_f8be(self):
        return KaitaiStream.packer_f8be.unpack(self.read_bytes(8))[0]

    # ........................................................................
    # Little-endian
    # ........................................................................

    def read_f4le(self):
        return KaitaiStream.packer_f4le.unpack(self.read_bytes(4))[0]

    def read_f8le(self):
        return KaitaiStream.packer_f8le.unpack(self.read_bytes(8))[0]

    # ========================================================================
    # Unaligned bit values
    # ========================================================================

    def align_to_byte(self):
        self.bits = 0
        self.bits_left = 0

    def read_bits_int_be(self, n):
        bits_needed = n - self.bits_left
        if bits_needed > 0:
            # 1 bit  => 1 byte
            # 8 bits => 1 byte
            # 9 bits => 2 bytes
            bytes_needed = ((bits_needed - 1) // 8) + 1
            buf = self.read_bytes(bytes_needed)
            for byte in buf:
                byte = KaitaiStream.int_from_byte(byte)
                self.bits <<= 8
                self.bits |= byte
                self.bits_left += 8

        # raw mask with required number of 1s, starting from lowest bit
        mask = (1 << n) - 1
        # shift self.bits to align the highest bits with the mask & derive reading result
        shift_bits = self.bits_left - n
        res = (self.bits >> shift_bits) & mask
        # clear top bits that we've just read => AND with 1s
        self.bits_left -= n
        mask = (1 << self.bits_left) - 1
        self.bits &= mask

        return res

    # Unused since Kaitai Struct Compiler v0.9+ - compatibility with
    # older versions.
    def read_bits_int(self, n):
        return self.read_bits_int_be(n)

    def read_bits_int_le(self, n):
        bits_needed = n - self.bits_left
        if bits_needed > 0:
            # 1 bit  => 1 byte
            # 8 bits => 1 byte
            # 9 bits => 2 bytes
            bytes_needed = ((bits_needed - 1) // 8) + 1
            buf = self.read_bytes(bytes_needed)
            for byte in buf:
                byte = KaitaiStream.int_from_byte(byte)
                self.bits |= (byte << self.bits_left)
                self.bits_left += 8

        # raw mask with required number of 1s, starting from lowest bit
        mask = (1 << n) - 1
        # derive reading result
        res = self.bits & mask
        # remove bottom bits that we've just read by shifting
        self.bits >>= n
        self.bits_left -= n

        return res

    # ========================================================================
    # Byte arrays
    # ========================================================================

    def read_bytes(self, n):
        if n < 0:
            raise ValueError(
                "requested invalid %d amount of bytes" %
                (n,)
            )
        r = self._io.read(n)
        if len(r) < n:
            raise EOFError(
                "requested %d bytes, but got only %d bytes" %
                (n, len(r))
            )
        return r

    def read_bytes_full(self):
        return self._io.read()

    def read_bytes_term(self, term, include_term, consume_term, eos_error):
        r = b''
        while True:
            c = self._io.read(1)
            if c == b'':
                if eos_error:
                    raise Exception(
                        "end of stream reached, but no terminator %d found" %
                        (term,)
                    )
                else:
                    return r
            elif ord(c) == term:
                if include_term:
                    r += c
                if not consume_term:
                    self._io.seek(-1, SEEK_CUR)
                return r
            else:
                r += c

    def ensure_fixed_contents(self, expected):
        actual = self._io.read(len(expected))
        if actual != expected:
            raise Exception(
                "unexpected fixed contents: got %r, was waiting for %r" %
                (actual, expected)
            )
        return actual

    @staticmethod
    def bytes_strip_right(data, pad_byte):
        return data.rstrip(KaitaiStream.byte_from_int(pad_byte))

    @staticmethod
    def bytes_terminate(data, term, include_term):
        new_data, term_byte, _ = data.partition(KaitaiStream.byte_from_int(term))
        if include_term:
            new_data += term_byte
        return new_data

    # ========================================================================
    # Byte array processing
    # ========================================================================

    @staticmethod
    def process_xor_one(data, key):
        if PY2:
            return bytes(bytearray(v ^ key for v in bytearray(data)))
        else:
            return bytes(v ^ key for v in data)

    @staticmethod
    def process_xor_many(data, key):
        if PY2:
            return bytes(bytearray(a ^ b for a, b in zip(bytearray(data), itertools.cycle(bytearray(key)))))
        else:
            return bytes(a ^ b for a, b in zip(data, itertools.cycle(key)))

    @staticmethod
    def process_rotate_left(data, amount, group_size):
        if group_size != 1:
            raise Exception(
                "unable to rotate group of %d bytes yet" %
                (group_size,)
            )

        mask = group_size * 8 - 1
        anti_amount = -amount & mask

        r = bytearray(data)
        for i in range(len(r)):
            r[i] = (r[i] << amount) & 0xff | (r[i] >> anti_amount)
        return bytes(r)

    # ========================================================================
    # Misc
    # ========================================================================

    @staticmethod
    def int_from_byte(v):
        return ord(v) if PY2 else v

    @staticmethod
    def byte_from_int(i):
        return chr(i) if PY2 else bytes((i,))

    @staticmethod
    def byte_array_index(data, i):
        return KaitaiStream.int_from_byte(data[i])

    @staticmethod
    def byte_array_min(b):
        return KaitaiStream.int_from_byte(min(b))

    @staticmethod
    def byte_array_max(b):
        return KaitaiStream.int_from_byte(max(b))

    @staticmethod
    def resolve_enum(enum_obj, value):
        """Resolves value using enum: if the value is not found in the map,
        we'll just use literal value per se. Works around problem with Python
        enums throwing an exception when encountering unknown value.
        """
        try:
            return enum_obj(value)
        except ValueError:
            return value


class KaitaiStructError(Exception):
    """Common ancestor for all error originating from Kaitai Struct usage.
    Stores KSY source path, pointing to an element supposedly guilty of
    an error.
    """
    def __init__(self, msg, src_path):
        super(KaitaiStructError, self).__init__("%s: %s" % (src_path, msg))
        self.src_path = src_path


class UndecidedEndiannessError(KaitaiStructError):
    """Error that occurs when default endianness should be decided with
    switch, but nothing matches (although using endianness expression
    implies that there should be some positive result).
    """
    def __init__(self, src_path):
        super(KaitaiStructError, self).__init__("unable to decide on endianness for a type", src_path)


class ValidationFailedError(KaitaiStructError):
    """Common ancestor for all validation failures. Stores pointer to
    KaitaiStream IO object which was involved in an error.
    """
    def __init__(self, msg, io, src_path):
        super(ValidationFailedError, self).__init__("at pos %d: validation failed: %s" % (io.pos(), msg), src_path)
        self.io = io


class ValidationNotEqualError(ValidationFailedError):
    """Signals validation failure: we required "actual" value to be equal to
    "expected", but it turned out that it's not.
    """
    def __init__(self, expected, actual, io, src_path):
        super(ValidationNotEqualError, self).__init__("not equal, expected %s, but got %s" % (repr(expected), repr(actual)), io, src_path)
        self.expected = expected
        self.actual = actual


class ValidationLessThanError(ValidationFailedError):
    """Signals validation failure: we required "actual" value to be
    greater than or equal to "min", but it turned out that it's not.
    """
    def __init__(self, min, actual, io, src_path):
        super(ValidationLessThanError, self).__init__("not in range, min %s, but got %s" % (repr(min), repr(actual)), io, src_path)
        self.min = min
        self.actual = actual


class ValidationGreaterThanError(ValidationFailedError):
    """Signals validation failure: we required "actual" value to be
    less than or equal to "max", but it turned out that it's not.
    """
    def __init__(self, max, actual, io, src_path):
        super(ValidationGreaterThanError, self).__init__("not in range, max %s, but got %s" % (repr(max), repr(actual)), io, src_path)
        self.max = max
        self.actual = actual


class ValidationNotAnyOfError(ValidationFailedError):
    """Signals validation failure: we required "actual" value to be
    from the list, but it turned out that it's not.
    """
    def __init__(self, actual, io, src_path):
        super(ValidationNotAnyOfError, self).__init__("not any of the list, got %s" % (repr(actual)), io, src_path)
        self.actual = actual


class ValidationExprError(ValidationFailedError):
    """Signals validation failure: we required "actual" value to match
    the expression, but it turned out that it doesn't.
    """
    def __init__(self, actual, io, src_path):
        super(ValidationExprError, self).__init__("not matching the expression, got %s" % (repr(actual)), io, src_path)
        self.actual = actual
