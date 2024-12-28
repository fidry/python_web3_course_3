from ads_power.modules.base import Base


class Browser(Base):
    def open_browser(
            self,
            user_id: str,
            serial_number: str | None = None,
            open_tabs: str = '0',
            ip_tab: str = '1',
            new_first_tab: str = '0',
            launch_args: str | None = None,
            headless: str = '0',
            disable_password_filling: str = '0',
            clear_cache_after_closing: str = '0',
            enable_password_saving: str = '0',
            cdp_mask: str = '1'
    ):
        path = '/api/v1/browser/start'
        method = 'GET'
        params = {
            'user_id': user_id,
            'serial_number': serial_number,
            'open_tabs': open_tabs,
            'ip_tab': ip_tab,
            'new_first_tab': new_first_tab,
            'launch_args': launch_args,
            'headless': headless,
            'disable_password_filling': disable_password_filling,
            'clear_cache_after_closing': clear_cache_after_closing,
            'enable_password_saving': enable_password_saving,
            'cdp_mask': cdp_mask,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def close_browser(
            self,
            user_id: str,
            serial_number: str | None = None
    ):
        path = '/api/v1/browser/stop'
        method = 'GET'
        params = {
            'user_id': user_id,
            'serial_number': serial_number,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def check_browser_status(
            self,
            user_id: str,
            serial_number: str | None = None
    ):
        path = '/api/v1/browser/active'
        method = 'GET'
        params = {
            'user_id': user_id,
            'serial_number': serial_number,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )


# ---------------------------------------------------------------------------------------
# import config
# import time
#
# user_id = 'kq2kc44'
# browser = Browser(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
# print(browser.open_browser(user_id=user_id))
# time.sleep(1)
# print(browser.check_browser_status(user_id=user_id))
# time.sleep(5)
# print(browser.close_browser(user_id=user_id))
# time.sleep(1)
# print(browser.check_browser_status(user_id=user_id))
# ---------------------------------------------------------------------------------------
