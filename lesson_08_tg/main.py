import asyncio
from asyncio import Event
import json

import aiogram
import playwright._impl._errors as playwright_errors
from aiogram.types import BufferedInputFile
from loguru import logger
from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Browser,
    Page, Frame, Route,
)

import config
from ads_power.client import Client as AdsPowerClient

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


class BlumPageController(TelegramWebController):
    channel_with_bot_link_username: str = 'channelwithblumlink'
    frame_url_part: str = 'telegram.blum.codes'

    def __init__(self, cdp_url: str, profile_name: str):
        super().__init__(cdp_url=cdp_url, profile_name=profile_name)

        self.headers: dict | None = None
        self.headers_defined_event = Event()

    @staticmethod
    def extract_task_ids(data: list[dict]) -> tuple[set[str], set[str]]:
        """
        Рекурсивно проходит по данным и собирает ID заданий с validationType == 'DEFAULT',
        разделяя их по статусам.
        """
        not_started: set[str] = set()
        ready_for_claim: set[str] = set()

        def process_tasks(tasks):
            """Обрабатывает список задач."""
            for task in tasks:
                if task.get('validationType') == 'DEFAULT':
                    task_id = task.get('id')
                    status = task.get('status')
                    if status == 'NOT_STARTED':
                        not_started.add(task_id)
                    elif status == 'READY_FOR_CLAIM':
                        ready_for_claim.add(task_id)

                # Проверяем вложенные задачи, если они есть
                if 'subTasks' in task:
                    process_tasks(task['subTasks'])

        # Рекурсивно обходим секции и вложенные задачи
        def traverse(data):
            for section in data:
                tasks = section.get('tasks', [])
                process_tasks(tasks)

                # Проверяем вложенные секции
                if 'subSections' in section:
                    traverse(section['subSections'])

        traverse(data)
        return not_started, ready_for_claim

    async def claim_task(self, task_id: str) -> int:
        logger.info(f'Claiming task {task_id}')

        response: dict = await self.frame.evaluate(
            expression="""
            async ([headers, task_id]) => {
                const response = await fetch(`https://earn-domain.blum.codes/api/v1/tasks/${task_id}/claim`, {
                    headers: headers,
                    method: "POST"
                });
                return response.json();
            }
            """,
            arg=[self.headers, task_id],
        )

        if response['status'] != 'FINISHED':
            raise RuntimeError(f'Failed to claim {task_id=}')

        return int(response['reward'])

    async def start_task(self, task_id: str) -> bool:
        logger.info(f'Starting task {task_id}')

        response: dict = await self.frame.evaluate(
            expression="""
            async ([headers, task_id]) => {
                const response = await fetch(`https://earn-domain.blum.codes/api/v1/tasks/${task_id}/start`, {
                    headers: headers,
                    method: "POST"
                });
                return response.json();
            }
            """,
            arg=[self.headers, task_id],
        )

        error_message: str | None = response.get('message')
        if error_message:
            logger.warning(f'Failed to start task {task_id}, because: "{error_message}"')
            return False

        return response['status'] == 'STARTED'

    async def fetch_tasks(self) -> list[dict]:
        logger.info(f'Requesting tasks...')

        response: list[dict] = await self.frame.evaluate(
            expression="""
            async (headers) => {
                const response = await fetch("https://earn-domain.blum.codes/api/v1/tasks", {
                    headers: headers,
                    method: "GET"
                });
                return response.json();
            }
            """,
            arg=self.headers,
        )

        return response

    async def handle_api_request(self, route: Route) -> None:
        request_url: str = route.request.url

        if 'blum.codes/api/v1/' in request_url and not self.headers_defined_event.is_set():
            self.headers = route.request.headers
            logger.info(
                f"Intercepted API request with headers: {route.request.url}; {self.headers}",
            )
            self.headers_defined_event.set()

        await route.continue_()

    async def complete_tasks(self) -> None:
        await self.page.route(
            "**/*",
            handler=self.handle_api_request,
        )

        await self.open_tasks_tab()

        try:
            await asyncio.wait_for(self.headers_defined_event.wait(), timeout=5)
        except Exception:
            raise RuntimeError('Failed to obtain headers for requests to API...')

        task_started: int = 0
        task_completed: int = 0
        total_reward: int = 0

        for _ in range(2):
            tasks: list[dict] = await self.fetch_tasks()
            to_start, to_claim = self.extract_task_ids(tasks)
            logger.info(f'Found {len(to_start)} to start, {len(to_claim)} to claim tasks')

            for task_to_start_id in to_start:
                started: bool = await self.start_task(task_to_start_id)
                if started:
                    task_started += 1

            for task_to_claim_id in to_claim:
                reward: int = await self.claim_task(task_to_claim_id)
                task_completed += 1
                total_reward += reward

            await asyncio.sleep(10)

        logger.info(f'{task_started=}; {task_completed=}; {total_reward=}')

        await self.open_home_tab()

        await self.send_telegram_notification(
            text=f'Finished with tasks, started: {task_started}; '
                 f'completed: {task_completed}; reward: {total_reward} BP',
            with_screenshot=True,
        )

    async def handle_account(self) -> None:
        await self.open_link(
            username=self.channel_with_bot_link_username,
        )
        await self.launch_app()

        await asyncio.sleep(10)

        await self.open_home_tab()
        await self.claim_all()
        await self.start_farming()

        await self.complete_tasks()

    async def start_farming(self) -> None:
        farming_started: bool = await self.click_by_text(
            entity=self.frame,
            text='Start farming',
            exact=True,
            raise_on_timeout=False,
        )
        if farming_started:
            await self.send_telegram_notification(
                text='Successfully started farming',
                with_screenshot=True,
            )

    async def open_tasks_tab(self) -> None:
        await self.click_by_text(
            entity=self.frame,
            text='Earn',
            exact=True,
        )

    async def open_home_tab(self) -> None:
        await self.click_by_text(
            entity=self.frame,
            text='Home',
            exact=True,
        )

    async def claim_all(self) -> None:
        claimed: bool = await self.click_by_text(
            entity=self.frame,
            text='Claim',
            exact=True,
            raise_on_timeout=False,
        )
        if claimed:
            await self.send_telegram_notification(
                text='Successfully clicked on "Claim" button',
                with_screenshot=True,
            )


async def main():
    ads_power_client: AdsPowerClient = AdsPowerClient(
        api_key=config.ADS_API_KEY,
        api_uri=config.ADS_API_URI,
    )

    # Получаем группу с названием "Telegram"
    telegram_group_id = ads_power_client.groups.get_group_id_by_group_name(
        group_name='Telegram',
    )

    # Получаем все профили в группе "Telegram"
    telegram_profiles: dict = ads_power_client.profiles.query_profile(
        group_id=telegram_group_id,
    )
    if not telegram_profiles:
        raise RuntimeError('Профили в группе "Telegram" не найдены')

    for profile in telegram_profiles['data']['list']:
        user_id: str = profile['user_id']
        profile_name: str = profile['name']
        start_profile_data: dict = ads_power_client.browser.open_browser(
            user_id=user_id,
        )

        try:
            await asyncio.sleep(3)

            async with BlumPageController(
                    cdp_url=start_profile_data['data']['ws']['puppeteer'],
                    profile_name=profile_name,
            ) as blum_controller:
                await blum_controller.handle_account()

                await asyncio.sleep(5)

        except Exception as error:
            logger.exception('Во время работы браузера произошла ошибка', error)

        ads_power_client.browser.close_browser(user_id=user_id)


if __name__ == '__main__':
    asyncio.run(main())
