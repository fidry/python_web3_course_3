import asyncio
from hexbytes import HexBytes

from curl_cffi.requests import AsyncSession
from fake_useragent import UserAgent
from eth_typing import ChecksumAddress, HexStr
from eth_account.signers.local import LocalAccount
from web3.exceptions import Web3Exception
from web3 import AsyncWeb3, Web3
from web3.middleware import geth_poa_middleware


class Client:
    private_key: str
    rpc: str
    proxy: str | None
    w3: AsyncWeb3
    account: LocalAccount

    def __init__(self, private_key: str, rpc: str, proxy: str | None = None):
        self.private_key = private_key
        self.rpc = rpc
        self.proxy = proxy

        if self.proxy:
            if '://' not in self.proxy:
                self.proxy = f'http://{self.proxy}'

        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().chrome
        }

        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(
            endpoint_uri=rpc,
            request_kwargs={'proxy': self.proxy, 'headers': self.headers}
        ))
        self.account = self.w3.eth.account.from_key(private_key)

    def max_priority_fee(self, block: dict | None = None) -> int:
        w3 = Web3(provider=AsyncWeb3.HTTPProvider(endpoint_uri=self.rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not block:
            block = w3.eth.get_block('latest')

        block_number = block['number']
        latest_block_transaction_count = w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_lst = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = w3.eth.get_transaction_by_block(block_number, i)
                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_lst.append(transaction['maxPriorityFeePerGas'])
            except Exception:
                continue

        if not max_priority_fee_per_gas_lst:
            max_priority_fee_per_gas = 0
        else:
            max_priority_fee_per_gas_lst.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_lst[len(max_priority_fee_per_gas_lst) // 2]
        return max_priority_fee_per_gas

    async def send_transaction(
            self,
            to: str | ChecksumAddress,
            data: HexStr | None = None,
            from_: str | ChecksumAddress | None = None,
            increase_gas: float = 1,
            value: int | None = None,
            eip1559: bool = True,
            max_priority_fee_per_gas: int | None = None
    ) -> HexBytes | None:
        if not from_:
            from_ = self.account.address

        tx_params = {
            'chainId': await self.w3.eth.chain_id,
            'nonce': await self.w3.eth.get_transaction_count(self.account.address),
            'from': AsyncWeb3.to_checksum_address(from_),
            'to': AsyncWeb3.to_checksum_address(to),
        }

        if eip1559:
            if max_priority_fee_per_gas is None:
                max_priority_fee_per_gas = await self.w3.eth.max_priority_fee
            base_fee = (await self.w3.eth.get_block('latest'))['baseFeePerGas']
            max_fee_per_gas = base_fee + max_priority_fee_per_gas
            tx_params['maxFeePerGas'] = max_fee_per_gas  # максимальная общая комиссия
            tx_params['maxPriorityFeePerGas'] = max_priority_fee_per_gas  # приоритетная комиссия майнеру
        else:
            tx_params['gasPrice'] = await self.w3.eth.gas_price

        if data:
            tx_params['data'] = data
        if value:
            tx_params['value'] = value

        gas = await self.w3.eth.estimate_gas(tx_params)
        tx_params['gas'] = int(gas * increase_gas)

        sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        return await self.w3.eth.send_raw_transaction(sign.rawTransaction)

    async def verif_tx(self, tx_hash: HexBytes, timeout: int = 200) -> str:
        data = await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        if data.get('status') == 1:
            return tx_hash.hex()
        raise Web3Exception(f'transaction failed {data["transactionHash"].hex()}')

    @staticmethod
    async def get_token_price(token_symbol='ETH') -> float | None:
        token_symbol = token_symbol.upper()

        if token_symbol in ('USDC', 'USDT', 'DAI', 'CEBUSD', 'BUSD', 'USDC.E'):
            return 1
        if token_symbol == 'WETH':
            token_symbol = 'ETH'
        if token_symbol == 'WBTC':
            token_symbol = 'BTC'

        for _ in range(5):
            try:
                async with AsyncSession() as session:
                    response = await session.get(
                        f'https://api.binance.com/api/v3/depth?limit=1&symbol={token_symbol}USDT')
                    result_dict = response.json()
                    if 'asks' not in result_dict:
                        return
                    return float(result_dict['asks'][0][0])
            except Exception:
                await asyncio.sleep(5)
        raise ValueError(f'Can not get {token_symbol} price from Binance API')
