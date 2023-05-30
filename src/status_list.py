from base64 import urlsafe_b64decode, urlsafe_b64encode
import gzip


class StatusList:
    list: bytearray
    bits: int
    size: int

    def __init__(self, size: int, bits: int):
        self.divisor = 8 // bits
        self.list = bytearray([0] * (size // self.divisor))
        self.bits = bits
        self.size = size

    @classmethod
    def fromEncoded(cls, bits: int, encoded: str):
        new = cls(0, bits)
        new.decode(encoded)
        return new

    def encode(self) -> str:
        zipped = gzip.compress(self.list)
        return urlsafe_b64encode(zipped).decode().strip("=")

    def decode(self, input: str):
        zipped = urlsafe_b64decode(f"{input}{'=' * divmod(len(input),4)[1]}")
        self.list = bytearray(gzip.decompress(zipped))

    def set(self, pos: int, value: int):
        assert value < 2**self.bits
        rest = pos % self.divisor
        floored = pos // self.divisor
        shift = self._shift(rest)
        mask = 0xFF ^ (((1 << self.bits) - 1) << shift)
        self.list[floored] = (self.list[floored] & mask) + (value << shift)

    def get(self, pos: int) -> int:
        rest = pos % self.divisor
        floored = pos // self.divisor
        shift = self._shift(rest)
        return (self.list[floored] & (((1 << self.bits) - 1) << shift)) >> shift

    def _shift(self, rest: int) -> int:
        return self.bits * rest

    def __str__(self):
        val = ""
        for x in range(0, self.size):
            val = val + format(self.get(x), "x")
        return val