import asyncio
from asyncio import Event
import json

from loguru import logger
from playwright.async_api import Route

from config import KEYWORD_BY_TASK_ID
from controllers.base_controller import TelegramWebController


class BlumPageController(TelegramWebController):
    channel_with_bot_link_username: str = 'channelwithblumlink'
    frame_url_part: str = 'telegram.blum.codes'

    def __init__(self, cdp_url: str, profile_name: str):
        super().__init__(cdp_url=cdp_url, profile_name=profile_name)

        self.headers: dict | None = None
        self.headers_defined_event = Event()

    @staticmethod
    def extract_task_ids(data: list[dict]) -> tuple[set[str], set[str], set[str]]:
        """
        Рекурсивно проходит по данным и собирает ID заданий с validationType == 'DEFAULT',
        разделяя их по статусам.
        """
        not_started: set[str] = set()
        ready_for_claim: set[str] = set()
        ready_for_verify: set[str] = set()

        def process_tasks(tasks):
            """Обрабатывает список задач."""
            for task in tasks:
                task_id = task.get('id')
                status = task.get('status')

                if status == 'NOT_STARTED':
                    not_started.add(task_id)
                elif status == 'READY_FOR_VERIFY':
                    ready_for_verify.add(task_id)
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
        return not_started, ready_for_claim, ready_for_verify

    async def validate_task(self, task_id: str, keyword: str) -> bool:
        logger.info(f'Validating task {task_id} with {keyword}')

        body: dict[str, str] = {
            'keyword': keyword,
        }

        response: dict = await self.frame.evaluate(
            expression="""
                  async ([headers, task_id, body]) => {
                      const response = await fetch(`https://earn-domain.blum.codes/api/v1/tasks/${task_id}/validate`, {
                          headers: headers,
                          body: body,
                          method: "POST"
                      });
                      return response.json();
                  }
                  """,
            arg=[self.headers | {'content-type': 'application/json'}, task_id, json.dumps(body)],
        )

        return response['status'] == 'READY_FOR_CLAIM'

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
        task_verified: int = 0
        total_reward: int = 0

        for _ in range(2):
            tasks: list[dict] = await self.fetch_tasks()
            to_start, to_claim, to_verify = self.extract_task_ids(tasks)
            logger.info(f'Found {len(to_start)} to start, {len(to_claim)} to claim tasks')

            for task_to_start_id in to_start:
                started: bool = await self.start_task(task_to_start_id)
                if started:
                    task_started += 1

            for task_to_claim_id in to_claim:
                reward: int = await self.claim_task(task_to_claim_id)
                task_completed += 1
                total_reward += reward

            for task_to_verify_id in to_verify:
                if task_to_verify_id in KEYWORD_BY_TASK_ID.keys():
                    verified: bool = await self.validate_task(
                        task_id=task_to_verify_id,
                        keyword=KEYWORD_BY_TASK_ID[task_to_verify_id],
                    )
                    if verified:
                        task_verified += 1

            await asyncio.sleep(10)

        logger.info(f'{task_started=}; {task_completed=}; {task_verified=}; {total_reward=}')

        await self.open_home_tab()

        await self.send_telegram_notification(
            text=f'Finished with tasks, started: {task_started}; verified: {task_verified}; '
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
