import asyncio
import time

from eth_abi import abi

from tasks.base import Base
from data.config import logger, SLEEP_AFTER_APPROVAL
from data.models import TokenAmount, Contracts


class SyncSwap(Base):
    async def swap_usdc_e_to_eth(
        self,
        token_amount: TokenAmount | None = None,
        slippage: float = 1
    ) -> str:
        router = Contracts.SYNCSWAP_ROUTER
        from_token = Contracts.USDC_E
        to_token = Contracts.WETH
        from_token_is_native = from_token.address == Contracts.WETH.address

        from_token_contract = self.client.w3.eth.contract(
            address=from_token.address,
            abi=from_token.abi
        )

        if not token_amount:
            token_amount = TokenAmount(
                amount=await from_token_contract.functions.balanceOf(self.client.account.address).call(),
                decimals=await from_token_contract.functions.decimals().call(),
                wei=True
            )

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
            if not await self.approve_interface(
                token_address=from_token.address,
                spender=router.address,
                amount=token_amount
            ):
                return (f'{failed_text}: Can not approve {token_amount.Ether} {from_token.title} '
                        f'for spender {router.title}')
            else:
                logger.info(f'Approved {token_amount.Ether} {from_token.title} to swap on SyncSwap, '
                            f'sleeping {SLEEP_AFTER_APPROVAL} secs...')
                await asyncio.sleep(SLEEP_AFTER_APPROVAL)

        steps = [
            [
                Contracts.USDC_E_ZK_LP.address,
                self.client.w3.to_hex(
                    abi.encode(
                        ['address', 'address', 'uint8'],
                        [from_token.address, Contracts.ZK_WETH_C_LP.address, 2]
                    )
                ),
                Contracts.ZERO_ADDRESS.address,
                '0x',
                False
            ],
            [
                Contracts.ZK_WETH_C_LP.address,
                self.client.w3.to_hex(
                    abi.encode(
                        ['address', 'address', 'uint8'],
                        [Contracts.ZK.address, self.client.account.address, 1]
                    )
                ),
                Contracts.ZERO_ADDRESS.address,
                '0x',
                False
            ]
        ]
        paths = [
            steps,
            from_token.address,
            token_amount.Wei
        ]
        deadline = int(time.time()) + 11850
        
        tx_hash_bytes = await self.client.send_transaction(
            to=router.address,
            data=router_contract.encodeABI(
                'swap',
                args=(
                    [paths],
                    amount_out_min.Wei,
                    deadline
                )
            ),
            max_priority_fee_per_gas=0,
        )

        if not tx_hash_bytes:
            return f'{failed_text} | Can not get tx_hash_bytes'

        try:
            tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
            return (f'({router.title}) Transaction success! ({token_amount.Ether} USDC.e -> '
                    f'{amount_out_min.Ether} {to_token.title}) | tx_hash: {tx_hash}')
        except Exception as err:
            return f' {failed_text} | tx_hash: {tx_hash_bytes.hex()}; error: {err}'
