import asyncio

import aiogram
from aiogram.types import BufferedInputFile
import playwright._impl._errors as playwright_errors
from playwright.async_api import async_playwright, Browser, BrowserContext, Frame, Page

from loguru import logger

import config

NOTIFIER_BOT = aiogram.Bot(
    token=config.TELEGRAM_NOTIFIER_BOT,
)


class TelegramWebController:
    channel_with_bot_link_username: str = 'redefine_me'
    frame_url_part: str = 'redefine.me'

    def __init__(self, cdp_url: str, profile_name: str):
        self.profile_name: str = profile_name
        self.cdp_url: str = cdp_url

        self.browser: Browser | None = None
        self.page: Page | None = None
        self.frame: Frame | None = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser: Browser = await self.playwright.chromium.connect_over_cdp(
            endpoint_url=self.cdp_url,
        )

        self.context: BrowserContext = self.browser.contexts[0]
        self.page = await self.context.new_page()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def open_link(self, username: str) -> None:
        await self.page.goto(
            f'https://web.telegram.org/k/#@{username}',
            wait_until='networkidle',
        )

    async def click_by_text(
            self,
            text: str,
            exact: bool = False,
            timeout: float = 3000,
            raise_on_timeout: bool = True,
            entity: Page | Frame | None = None,
    ) -> bool:
        await asyncio.sleep(0.25)

        entity = entity or self.page
        clicked: bool = False

        elements = await entity.get_by_text(text, exact=exact).all()
        for element in elements:
            try:
                if not await element.is_visible():
                    await element.wait_for(state="visible", timeout=timeout)

                await asyncio.sleep(0.25)

                await element.click(timeout=timeout)

                clicked = True
            except playwright_errors.TimeoutError:
                if raise_on_timeout:
                    raise

                logger.warning(f'Ignored timeout on click on element "{text}"')

        return clicked

    async def launch_app(self) -> None:
        await self.click_by_text('LAUNCH APP', exact=True)
        await asyncio.sleep(1.5)
        await self.click_by_text('Launch', exact=True, raise_on_timeout=False)

        await asyncio.sleep(1.5)

        self.frame = self.get_frame()

    def get_frame(self) -> Frame:
        for frame in self.page.frames:
            if self.frame_url_part in frame.url:
                return frame

        raise RuntimeError('Opened bot frame not found')

    async def send_telegram_notification(self, text: str, with_screenshot: bool = True) -> None:
        text = f'[{self.profile_name}] {text}'

        try:
            if with_screenshot:
                await NOTIFIER_BOT.send_photo(
                    chat_id=config.TELEGRAM_NOTIFY_GROUP_ID,
                    caption=text,
                    photo=BufferedInputFile(
                        file=await self.page.screenshot(
                            timeout=3000,
                        ),
                        filename='screenshot.png',
                    )
                )
            else:
                await NOTIFIER_BOT.send_message(
                    chat_id=config.TELEGRAM_NOTIFY_GROUP_ID,
                    text=text,
                )
        except Exception:
            logger.exception('Failed to send telegram notification')
