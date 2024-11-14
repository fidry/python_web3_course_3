import json
import os


def get_json(path: str | list[str] | tuple[str]):
    if isinstance(path, (list, tuple)):
        path = os.path.join(*path)
    return json.load(open(path))


class TxUtils:
    @staticmethod
    def to_cut_hex_prefix_and_zfill(data: int | str, length: int = 64):
        str_hex_data = str(data)
        """
        Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

        Args:
            hex_data (str): The original hex string.
            length (int): The desired length of the string after filling. The default is 64.

        Returns:
            str: The modified string with '0x' prefix removed and zero-filled to the specified length.
        """
        if str_hex_data.startswith('0x'):
            str_hex_data = str_hex_data[2:]

        return str_hex_data.zfill(length)
    
    @staticmethod
    def parse_params(
        params: str,
        has_function_signature: bool = True
    ) -> None:
        """
        Parse a string of parameters, optionally printing function signature and memory addresses.

        Args:
            params (str): The string of parameters to parse.
            has_function_signature (bool, optional): Whether to print the function signature (default is True).

        Returns:
            None
        """
        if has_function_signature:
            function_signature = params[:10]
            print('Function signature:', function_signature)
            params = params[10:]
        else:
            params = params[2:]

        count = 0
        while params:
            memory_address = hex(count * 32)[2:].zfill(3)
            print(f'{memory_address}: {params[:64]}')
            count += 1
            params = params[64:]
        print()

    @staticmethod
    def print_normalize_number(number: int):
        print(f'{number:,}'.replace(',', '_'))
