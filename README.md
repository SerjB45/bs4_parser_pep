# Проект парсинга документации Python

## Описание 
Программа для парсинга информации с официального сайта по Рython https://www.python.org/. В проекте реализовано 4 парсера: 
- whats-new - Считывает обрабатывает статьи о нововведениях в Python
- latest-versions - Получение актуального статуса версий Python
- download - Загрузка документации по Python
- pep - Получение информации по документации PEP

## Как развернуть проект:

Клонировать проект:
```
git clone https://github.com/SerjB45/bs4_parser_pep.git 
```

Перейти в проект, создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Linux/macOS

    ```
    source venv/bin/activate
    ```

* Windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
## Запуск программы
В развернутом окружении(в терминале) вводить команды:
- python3 main.py -h(help) - вывод справки
- python3 main.py whats-new - Обновления в Python
- python3 main.py latest-versions - Версии Python 
- python3 main.py download - Скачать документацию
- python3 main.py pep - Документация PEP

Дополнительные опции:
- -с очиcтка кэша
- -o выбор варианта вывода информации (file - файл, pretty - с форматированием в консоль)

Пример:
```
python3 main.py whats-new --output file  
```
```
python3 main.py latest-versions --pretty 
```
```
python3 main.py whats-new -c 
```