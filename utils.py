import base64
from typing import Union

# Helper methods
class Utilities:
    @staticmethod
    def decode_data(key: str, data: Union[bytearray, str]) -> bytearray:
        key_bytes = bytes(key, 'utf-8')
        s = bytearray(range(256))
        j = 0

        for i in range(256):
            j = (j + s[i] + key_bytes[i % len(key_bytes)]) & 0xff
            s[i], s[j] = s[j], s[i]

        decoded = bytearray(len(data))
        i = 0
        k = 0

        for index in range(len(data)):
            i = (i + 1) & 0xff
            k = (k + s[i]) & 0xff
            s[i], s[k] = s[k], s[i]
            t = (s[i] + s[k]) & 0xff

            if isinstance(data[index], str):
                decoded[index] = ord(data[index]) ^ s[t]
            elif isinstance(data[index], int):
                decoded[index] = data[index] ^ s[t]
            else:
                raise ValueError("Unsupported data type in the input")

        return decoded
    
    @staticmethod
    def int_2_base(x: int, base: int) -> str:
        charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"

        if x < 0:
            sign = -1
        elif x == 0:
            return 0
        else:
            sign = 1

        x *= sign
        digits = []

        while x:
            digits.append(charset[int(x % base)])
            x = int(x / base)
        
        if sign < 0:
            digits.append('-')
        digits.reverse()

        return ''.join(digits)
    
    @staticmethod
    def decode_base64_url_safe(s: str) -> bytearray:
        standardized_input = s.replace('_', '/').replace('-', '+')
        binary_data = base64.b64decode(standardized_input)
        return bytearray(binary_data)

# Errors
class VidSrcError(Exception):
    '''Base Error'''
    pass

class CouldntFetchKeysError(VidSrcError):
    '''Failed to fetch decryption keys for vidplay'''
    pass