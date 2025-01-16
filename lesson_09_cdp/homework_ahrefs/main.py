from seleniumbase import SB
from utils.proxy_handler import ProxyHandler


def get_domain_rating(domain_to_check: str, random_proxy: str) -> str:
    with SB(uc=True, test=True, proxy=random_proxy) as sb:
        url = "https://ahrefs.com/backlink-checker/"
        sb.activate_cdp_mode(url)
        sb.sleep(5)
        
        # Selectors
        input_field_selector = 'input[placeholder="Enter domain or URL"]'
        check_backlinks_button_selector = 'span:contains("Check backlinks")'
        
        sb.cdp.press_keys(input_field_selector, domain_to_check)
        sb.cdp.click(check_backlinks_button_selector) # <- нажимаем на кнопку
        sb.sleep(7)
        
        sb.uc_gui_click_captcha()
        
        # Domain Rating
        domain_rating_selector = 'div:contains("Domain Rating")'
        sb.cdp.wait_for_element_visible(domain_rating_selector, timeout=20)
        
        domain_rating_xpath = (
            "//div[normalize-space(text())='Domain Rating']"  # 1️⃣ Находим div с текстом "Domain Rating"
            "/ancestor::div[5]"                               # 2️⃣ Поднимаемся на 5 div-элементов вверх
            "/following-sibling::div[1]"                      # 3️⃣ Берем первый следующий div на том же уровне
            "//span"                                          # 4️⃣ Внутри найденного div ищем элемент span
        )
        
        domain_rating_value = sb.cdp.get_text(domain_rating_xpath)
        
        if domain_rating_value:
            return domain_rating_value
        else:
            return "Domain rating not found"
        
def get_domain_names() -> list[str]:
    with open("./data/domains.txt", 'r') as file:
        return [line.strip() for line in file.readlines()]

if __name__ == "__main__":
    proxy_handler = ProxyHandler()
    random_proxy = proxy_handler.get_random_proxy()
    
    all_domains = get_domain_names()
    
    for domain in all_domains:
        domain_rating = get_domain_rating(domain, random_proxy)
        print(f"Domain: {domain}, Rating: {domain_rating}")


