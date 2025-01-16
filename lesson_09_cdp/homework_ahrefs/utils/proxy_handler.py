import random
from pathlib import Path

class ProxyHandler:
    def __init__(self):
        # Путь к файлу с прокси
        self.proxy_file = Path("./data/proxies.txt")
        
    def get_random_proxy(self) -> str:
        """Возвращает случайный прокси из файла"""
        # Проверяем существование файла
        if not self.proxy_file.exists():
            raise FileNotFoundError(f"Файл с прокси не найден: {self.proxy_file}")
            
        # Читаем все прокси из файла
        with open(self.proxy_file, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
            
        if not proxies:
            raise ValueError("Файл с прокси пуст")
            
        # Возвращаем случайный прокси из списка
        return random.choice(proxies)
