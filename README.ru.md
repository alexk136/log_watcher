# LogWatcher

Асинхронный наблюдатель за логами, который следит за несколькими файлами, ищет ошибки и выводит их с цветовой подсветкой.

## Возможности

- Асинхронный мониторинг нескольких лог-файлов одновременно
- "Хвостинг" логов — анализ только новых строк (аналогично `tail -F`)
- Поиск ошибок по регулярным выражениям и ключевым словам
- **Исключающие паттерны** - фильтрация нежелательных записей (debug, deprecated предупреждения и т.д.)
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
    "warning": "warning",
    "critical": "critical"
  },
  "exclude": [
    "deprecated",
    "debug"
  ]
}
```

#### Параметры конфигурации

- **logs**: Массив лог-файлов для мониторинга
  - `path`: Путь к лог-файлу (если файл еще не существует, LogWatcher будет молча ожидать его появления)
  - `name`: Отображаемое имя для лога (опционально, по умолчанию имя файла)
- **patterns**: Регулярные выражения для поиска ошибок (нечувствительны к регистру)
  - Ключ: Тип ошибки (используется для цветовой подсветки)
  - Значение: Регулярное выражение для поиска
- **exclude**: Массив регулярных выражений для исключения из мониторинга
  - Строки, соответствующие любому из этих паттернов, будут игнорированы
  - Полезно для фильтрации шума, например, debug-сообщений или deprecated предупреждений
  - Все паттерны нечувствительны к регистру

### Примеры

#### Базовый мониторинг ошибок
```json
{
  "logs": [{"path": "app.log", "name": "myapp"}],
  "patterns": {
    "error": "error",
    "warning": "warning"
  }
}
```

#### Продвинутая фильтрация с исключениями
```json
{
  "logs": [{"path": "verbose_app.log", "name": "app"}],
  "patterns": {
    "error": "error|failed|exception",
    "critical": "critical|fatal"
  },
  "exclude": [
    "deprecated",
    "debug",
    "info.*session",
    "cache.*miss"
  ]
}
```

#### Мониторинг нескольких файлов с разными целями
```json
{
  "logs": [
    {"path": "error.log", "name": "errors"},
    {"path": "access.log", "name": "access"},
    {"path": "debug.log", "name": "debug"}
  ],
  "patterns": {
    "error": "error|fail",
    "warning": "warn",
    "auth": "authentication|authorization"
  },
  "exclude": ["trace", "verbose"]
}
```

### Тестирование

LogWatcher включает тестовые скрипты для проверки функциональности:

```bash
# Запуск основного тестового набора (включает тестирование функции исключения)
./run_test.sh

# Тестирование исключающих паттернов
python logwatcher.py -c test_exclude_config.json

# Генерация тестовых логов для отладки
python generate_test_logs.py -o test.log -i 0.5
```

## Аргументы командной строки

- `-c, --config`: Путь к конфигу JSON
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
# Настроить мониторинг нескольких логов (поддерживает разделение запятыми и пробелами)
./setup_logs.sh --logs /path/to/log1.log,/path/to/log2.log
# ИЛИ
./setup_logs.sh --logs "/path/to/log1.log /path/to/log2.log"

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
- **Исключающие паттерны** для фильтрации шума и нежелательных записей
- Классификация ошибок (ERROR, EXCEPTION, FATAL и др.)
- Работа в фоне и управление через скрипты
- Интеграция с systemd
- Автоматический перезапуск при сбоях
- Нечувствительность к регистру в паттернах
- Мониторинг еще не существующих файлов логов (тихое ожидание появления файлов и автоматический старт мониторинга)
- Корректное завершение работы по Ctrl+C (безопасное закрытие всех наблюдателей за файлами)

## Лицензия

MIT
