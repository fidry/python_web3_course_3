import hashlib

from faker import Faker
from loguru import logger

from tasks.base import Base
from data.models import Contracts


class Dmail(Base):
    @staticmethod
    async def fake_acc():
        fake = Faker()
        profile = fake.profile()
        email_address, theme = profile['mail'], fake.company()

        return email_address, theme

    @staticmethod
    async def sha256(data):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data.encode('utf-8'))
        hash_str = sha256_hash.hexdigest()

        return hash_str

    async def send_dmail(self):
        # tx: 0x011194e04c7d3971b27b6824744ba8b97200b8dfc3fee713e019a2efefdd6d36
        router = Contracts.DMAIL
        failed_text = f'Failed send e-mail via Dmail'

        email_address, theme_info = await Dmail.fake_acc()
        logger.info(f'Sending e-mail to: {email_address} theme: {theme_info} - via Dmail')

        to = await Dmail.sha256(email_address)
        theme = await Dmail.sha256(theme_info)

        router_contract = self.client.w3.eth.contract(
            address=router.address,
            abi=router.abi
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=router.address,
            data=router_contract.encodeABI(
                'send_mail',
                args=(
                    to,
                    theme
                )),
            max_priority_fee_per_gas=0,
        )

        if not tx_hash_bytes:
            return f'{failed_text} | Can not get tx_hash_bytes'

        try:
            tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
            return f'E-mail was sent to {email_address} via Dmail: TX-Hash {tx_hash}'
        except Exception as err:
            return f' {failed_text} | tx_hash: {tx_hash_bytes.hex()}; error: {err}'
