import asyncio
import time

from tasks.base import Base
from data.config import logger, SLEEP_AFTER_APPROVAL
from data.models import TokenAmount, Contracts, RawContract


class SpaceFi(Base):
    async def get_raw_tx_params(self, wei_value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": wei_value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }

    async def _swap(
            self,
            path: list[RawContract],
            token_amount: TokenAmount | None = None,
            slippage: float = 1
    ) -> str:
        router = Contracts.SPACE_FI_ROUTER
        from_token = path[0]
        to_token = path[-1]
        addresses_path = list(map(lambda x: x.address, path))
        from_token_is_native = from_token.address == Contracts.WETH.address

        if not token_amount:
            token_amount = self.get_eth_amount_for_swap()

        failed_text = (f'Failed to swap {token_amount.Ether} {from_token.address} '
                       f'to {to_token.address} via {router.title}')

        to_token_contract = self.client.w3.eth.contract(
            address=to_token.address,
            abi=to_token.abi
        )

        router_contract = self.client.w3.eth.contract(
            address=router.address,
            abi=router.abi
        )

        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token.title),
            self.client.get_token_price(token_symbol=to_token.title)
        )

        amount_out_min = TokenAmount(
            amount=(float(token_amount.Ether)
                    * from_token_price_dollar
                    / to_token_price_dollar
                    * (100 - slippage) / 100),
            decimals=await to_token_contract.functions.decimals().call()
        )

        # Approve
        if not from_token_is_native:
            if not self.approve_interface(
                token_address=from_token.address,
                spender=router.address,
                amount=token_amount
            ):
                return (f'{failed_text}: Can not approve {token_amount.Ether} {from_token.title} '
                        f'for spender {router.title}')
            else:
                logger.info(f'Approved {token_amount.Ether} {from_token.title} to swap on SpaceFi, '
                            f'sleeping {SLEEP_AFTER_APPROVAL} secs...')
                await asyncio.sleep(SLEEP_AFTER_APPROVAL)

            tx_hash_bytes = await self.client.send_transaction(
                to=router.address,
                data=router_contract.encodeABI(
                    'swapExactTokensForETH',
                    args=(
                        token_amount.Wei,
                        amount_out_min.Wei,
                        addresses_path,
                        self.client.account.address,
                        int(time.time() + 1200)
                    )
                ),
                max_priority_fee_per_gas=0
            )

        else:
            tx_hash_bytes = await self.client.send_transaction(
                to=router.address,
                data=router_contract.encodeABI(
                    'swapExactETHForTokens',
                    args=(
                        amount_out_min.Wei,
                        addresses_path,
                        self.client.account.address,
                        int(time.time() + 1200)
                    )),
                value=token_amount.Wei,
                max_priority_fee_per_gas=0,
            )

        if not tx_hash_bytes:
            return f'{failed_text} | Can not get tx_hash_bytes'

        try:
            tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
            return (f'({router.title}) Transaction success! ({token_amount.Ether} {from_token.title} -> '
                    f'{amount_out_min.Ether} {to_token.title}) | tx_hash: {tx_hash}')
        except Exception as err:
            return f' {failed_text} | tx_hash: {tx_hash_bytes.hex()}; error: {err}'

    async def swap_eth_to_usdt(self, token_amount: TokenAmount | None = None, slippage: float = 0.5) -> str:
        # Transaction success (0.001 ETH -> 2.87 USDT)!!
        # tx_hash: 0x358ab333050193e02623c0b81aad6acea73f358eabd35e6c7526a5e7f52b98db
        return await self._swap(
            path=[
                Contracts.WETH,
                Contracts.USDT,
            ],
            token_amount=token_amount,
            slippage=slippage
        )

    async def swap_eth_to_wbtc(self, token_amount: TokenAmount | None = None, slippage: float = 0.5) -> str:
        # Transaction success (0.0008 ETH -> 0.000029105322888639857 WBTC)!!
        # tx_hash: 0x669310c1ec16ed385e8d0778cc96c05e2bc3d8b2e6d3490f4363b370bc6d2446
        return await self._swap(
            path=[
                Contracts.WETH,
                Contracts.WBTC,
            ],
            token_amount=token_amount,
            slippage=slippage
        )

    async def swap_usdc_e_to_eth(self, token_amount: TokenAmount | None = None, slippage: float = 0.5) -> str:
        # Transaction success (1.961663 USDC.e -> 0.0006465444482972901 WETH)!!
        # tx_hash: 0x0161e7cb528408427fce8eda171a251632d0b28cb89bf8dfd9616189964ae08b
        return await self._swap(
            path=[
                Contracts.USDC_E.address,
                Contracts.SPACE.address,
                Contracts.WETH.address,
            ],
            token_amount=token_amount,
            slippage=slippage
        )

    async def swap_usdt_to_eth(self, token_amount: TokenAmount | None = None, slippage: float = 0.5):
        # Transaction success (0.0004 ETH -> 1.13988 USDT)!!
        # tx_hash: 0x16ed6ce885e1f65a4a068b5e9253a5ebe2251ae93ed878ab583830515c627fb0
        return await self._swap(
            path=[
                Contracts.USDT.address,
                Contracts.SPACE.address,
                Contracts.WETH.address,
            ],
            token_amount=token_amount,
            slippage=slippage
        )

    async def swap_usdt_to_usdc_e(self, token_amount: TokenAmount | None = None, slippage: float = 0.5) -> str:
        # Transaction success (2.027439 USDT -> 1.946341 USDC.e)!!
        # tx_hash: 0xbd678a795c66238f067a0df7f49c759d7e3bc422a60c8fd7baadd1532566c98c
        return await self._swap(
            path=[
                Contracts.USDT.address,
                Contracts.SPACE.address,
                Contracts.USDC_E.address,
            ],
            token_amount=token_amount,
            slippage=slippage
        )
