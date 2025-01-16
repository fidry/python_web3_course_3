**Ссылка на презенатцию к теории:**

https://docs.google.com/presentation/d/1IDC7eOWfYSfKA0izqsQvrj6YQdwIK304lMISiPFUVg4/edit?usp=sharing

**Дополнительные ссылки:**

* Chrome DevTools Protocol - [https://chromedevtools.github.io/devtools-protocol/](https://chromedevtools.github.io/devtools-protocol/)
* SeleniumBase uc mode - [https://seleniumbase.io/help_docs/uc_mode/](https://seleniumbase.io/help_docs/uc_mode/)
* SeleniumBase cdp mode - [https://seleniumbase.io/examples/cdp_mode/ReadMe/](https://seleniumbase.io/examples/cdp_mode/ReadMe/)
* SeleniumBase github - [https://github.com/seleniumbase/SeleniumBase](https://github.com/seleniumbase/SeleniumBase)
* SeleniumBase github examples - [https://github.com/seleniumbase/SeleniumBase/tree/master/examples/cdp_mode](https://github.com/seleniumbase/SeleniumBase/tree/master/examples/cdp_mode)

**Домашнее задание:**

Написать скрипт с помощью SeleniumBase,  
который будет проверять неограниченное количество доменов на сайте [ahrefs.com/backlink-checker/](https://ahrefs.com/backlink-checker/) и выводить в консоль их доменный рейтинг.
Обратите внимание, что доменный рейтинг можно получить только после решения Trunstile captcha при нажатии на кнопку "Check backlinks".

**Теория таймкоды:**

* 00:00 - Введение / План
* 00:41 - Проблема использования стандартных методов подключения по CDP
* 03:53 - Каким образом автор фреймворка SeleniumBase обходит защиту вебсайтов
* 05:46 - Лирическое отступление про то, как DripHouse побанил мои аккаунты
* 08:33 - Наглядные примеры как обнаруживается автоматизация при использовании стандартных методов подключения по CDP
* 10:58 - Используем SeleniumBase uc/cdp mode
* 14:50 - Обзор параметров запуска контекстного менеджера SB
* 17:33 - Обзор методов класса sb.cdp
* 20:00 - Мысли про важность использовать современный софт
* 20:58 - История о том как был побежден кран Kodiak
* 22:33 - Выводы
* 23:51 - Домашнее задание

**Практика таймкоды:**

* 00:00 - Постановка задачи / Разведка
* 02:51 - Создаем каркас проекта
* 12:25 - Изучаем как правильно воспользоваться селекторами
* 22:26 - Сложные изыскания по построению селектора для обхода динамических классов
* 32:51 - Добавляем возможность массовой проверки доменов
* 40:57 - Заключение
