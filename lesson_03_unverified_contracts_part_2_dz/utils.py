import json
import os


def get_json(path: str | list[str] | tuple[str]):
    if isinstance(path, (list, tuple)):
        path = os.path.join(*path)
    return json.load(open(path))


class TxUtils:
    @staticmethod
    def to_cut_hex_prefix_and_zfill(hex_data: str, length: int = 64):
        """
        Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

        Args:
            hex_data (str): The original hex string.
            length (int): The desired length of the string after filling. The default is 64.

        Returns:
            str: The modified string with '0x' prefix removed and zero-filled to the specified length.
        """
        if hex_data.startswith('0x'):
            hex_data = hex_data[2:]

        return hex_data.zfill(length)
