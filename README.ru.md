# LogWatcher

Асинхронный наблюдатель за логами, который следит за несколькими файлами, ищет ошибки и выводит их с цветовой подсветкой.

## Возможности

- Асинхронный мониторинг нескольких лог-файлов одновременно
- "Хвостинг" логов — анализ только новых строк (аналогично `tail -F`)
- Поиск ошибок по регулярным выражениям и ключевым словам
- Цветная подсветка ошибок разных типов в консоли
- Простая настройка через JSON
- Быстрый запуск через аргументы командной строки

## Требования

- Python 3.7+
- Зависимости:
  - colorama

## Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/alexk136/log_watcher
cd LogWatcher

# Установите зависимости
pip install colorama
```

## Использование

### Базовый запуск

```bash
# Простой запуск (автоматически использует config.json из директории скрипта)
python logwatcher.py

# Использование указанного конфигурационного файла
python logwatcher.py -c path/to/config.json

# Прямой мониторинг указанных логов
python logwatcher.py -l /var/log/syslog /var/log/auth.log

# Использование скрипта для продакшена (фоновый режим)
./watch_log.sh start    # Запуск LogWatcher как фонового сервиса
./watch_log.sh stop     # Остановка сервиса
./watch_log.sh restart  # Перезапуск сервиса
./watch_log.sh status   # Проверка статуса

# Быстрая настройка для мониторинга нескольких логов
./setup_logs.sh --logs /var/log/app1.log,/var/log/app2.log
```

### Конфигурация

LogWatcher настраивается через JSON-файл:

**Конфигурация (config.json)**

```json
{
  "logs": [
    {
      "path": "/var/log/syslog",
      "name": "system"
    },
    {
      "path": "/var/log/auth.log",
      "name": "auth"
    }
  ],
  "patterns": {
    "error": "error|fail(ed|ure)",
    "exception": "exception",
    "fatal": "fatal",
    "warning": "warning"
  }
}
```

## Аргументы командной строки

- `-c, --config`: Путь к конфигу (YAML или JSON)
- `-l, --logs`: Список лог-файлов для мониторинга (через пробел)

## Скрипты для эксплуатации

### watch_log.sh

Скрипт управления сервисом LogWatcher для продакшн-среды:

- `./watch_log.sh start`: Запуск LogWatcher в фоне
- `./watch_log.sh stop`: Остановка сервиса
- `./watch_log.sh restart`: Перезапуск
- `./watch_log.sh status`: Проверка статуса и последних логов

Скрипт управляет PID, логированием и корректным завершением работы.

### setup_logs.sh

Утилита для быстрой генерации конфигурации:

```bash
# Настроить мониторинг нескольких логов
./setup_logs.sh --logs /path/to/log1.log,/path/to/log2.log

# Указать свои паттерны ошибок
./setup_logs.sh --logs /var/log/app.log --patterns error:"error|failed",critical:"urgent|critical"
```

### Системный сервис

Файл systemd-сервиса — `logwatcher.service`. Перед установкой отредактируйте пути:

```bash
# Откройте файл и укажите свой путь установки
# Замените %h/path/to/logwatcher на ваш путь
nano logwatcher.service
```

Далее установите сервис:

```bash
sudo cp logwatcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable logwatcher
sudo systemctl start logwatcher
```

## Особенности

- Цветная подсветка ошибок по типу
- Временная метка для каждого события
- Автоматический поиск ошибок по регуляркам
- Классификация ошибок (ERROR, EXCEPTION, FATAL и др.)
- Работа в фоне и управление через скрипты
- Интеграция с systemd
- Автоматический перезапуск при сбоях

## Лицензия

MIT
