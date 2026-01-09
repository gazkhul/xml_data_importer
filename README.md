# XML Data Importer

**XML Data Importer** — сервис для автоматического импорта данных из XML-файлов в базу данных MariaDB/MySQL.

Сервис работает в фоновом режиме, отслеживая появление новых файлов в указанной директории, разбирает их и выполняет синхронизацию данных: вставку новых записей (INSERT), обновление существующих (UPDATE) и удаление отсутствующих (DELETE, если установлен флаг delete=true).

### Основные возможности
*   **Автоматический запуск**: использует `systemd.path`, отслеживая появления новых файлов в директории для импорта.
*   **Полная синхронизация**: поддерживает вставку, обновление и удаление данных.
*   **Безопасность**: работает от имени отдельного пользователя БД с минимальными привилегиями.
*   **Отчетность**: генерирует детальный JSON-отчет, доступный через веб-интерфейс.
*   **Логирование**: подробные логи операций с ротацией.

### Поддерживаемые файлы
*   `prod_dop.xml` — данные о дополнительных параметрах продуктов.
*   `warehouses.xml` — данные о складских остатках и ценах.

***

## 1. Установка и настройка

### Шаг 1: Установка системных зависимостей

**Ubuntu:**
```bash
sudo apt update
sudo apt install -y build-essential libmariadb-dev
```

**CentOS:**
```bash
sudo yum install -y mariadb-devel gcc gcc-c++ make
```

### Шаг 2: Получение кода

Скачать архив с кодом и распаковать в рабочую директорию (`/opt/xml_data_importer`).

```bash
cd /opt
sudo wget https://github.com/gazkhul/xml_data_importer/archive/refs/heads/master.zip
sudo unzip master.zip
sudo mv xml_data_importer-master xml_data_importer
cd xml_data_importer
```

### Шаг 3: Настройка окружения Python

Проект использует **uv** для управления зависимостями.

1.  **Установить uv** (если еще нет):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
    ```

2.  **Установить зависимости**:
    ```bash
    # Создаст виртуальное окружение .venv и установит пакеты
    uv venv && uv sync
    ```

### Шаг 4: Конфигурация приложения (.env)

Переименовать файл-пример и отредактировать:

```bash
cp .env.example .env
nano .env
```

**Пример содержимого `.env`:**

```ini
# --- Настройки подключения к БД (Администратор) ---
# Используется ТОЛЬКО для первоначальной миграции (init_db.py)
DB_ADMIN_USERNAME=root
DB_ADMIN_PASSWORD=secure_root_password

# --- Настройки подключения к БД (Приложение) ---
# Используется основным сервисом для работы
DB_APP_USERNAME=xml_importer
DB_APP_PASSWORD=secure_app_password
# Хост, с которого разрешено подключение пользователя (обычно localhost)
DB_APP_ALLOWED_HOST=localhost

# --- Общие настройки БД ---
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mydb

# --- Пути ---
# Директория, куда заливаются XML файлы для импорта
IMPORT_DIR=/var/xml_inbox
```

> **Важно**: убедитесь, что директория `IMPORT_DIR` существует и доступна для записи.

***

## 2. Инициализация базы данных

Перед первым запуском необходимо подготовить базу данных. Модуль `init_db.py` создаст таблицы и настроит права доступа.

```bash
uv run python -m importer.init_db
```

**Что делает этот модуль:**
1.  **Бэкап**: если таблицы `tbl_prod_dop` или `warehouses` уже есть, они переименовываются в `*_backup`.
2.  **Миграция**: создает новые пустые таблицы на основе актуальной схемы.
3.  **Безопасность**: создает пользователя (из `.env`) и выдает ему права `SELECT, INSERT, UPDATE, DELETE` **только** на эти две таблицы и **только** с хоста `localhost`.

***

## 3. Настройка Systemd (Автозапуск)

Используется `.path` + `.service`. Юнит `xml-import.path` следит за директорией импорта и запускает `xml-import.service` при появлении файлов.

1.  **Отредактировать путь к директории в файле path-юнита**:
    Откройте `deploy/systemd/xml-import.path` и убедитесь, что `PathExistsGlob` указывает на вашу директорию входящих файлов.
    ```ini
    [Path]
    PathExistsGlob=/var/xml_inbox/*.xml
    ```

2.  **Копирование и активация**:
    ```bash
    sudo cp deploy/systemd/* /etc/systemd/system/

    sudo systemctl daemon-reload
    sudo systemctl enable --now xml-import.path
    ```

Теперь при появлении любого `.xml` файла в `/var/xml_inbox` сервис запустится автоматически.

***

## 4. Настройка Nginx (Отчеты)

Сервис генерирует отчет о последнем импорте в файл `reports/report.json`.

1.  **Запустить скрипт настройки прав:**
    ```bash
    sudo sh deploy/scripts/setup_perms.sh www-data
    ```
    где `www-data` - имя пользователя nginx. Узнать можно в строке `user` файла `/etc/nginx/nginx.conf`

2.  **Скопировать конфиг**:
    ```bash
    sudo cp deploy/nginx/importer_report.conf /etc/nginx/vhosts-includes/
    ```

3.  **Проверить nginx.conf**: путь `(/etc/nginx/vhosts-includes/)` должен быть включен в `server{}` конфига nginx.

4.  **Перезагрузить Nginx**:
    ```bash
    sudo nginx -t
    sudo systemctl reload nginx
    ```

Отчет доступен по адресу: `https://your-site.com/importer/report.json`.

***

## 5. Мониторинг и Логирование

### Лог-файл
Основной лог сервиса:
`tail -f /opt/xml_data_importer/logs/xml_importer.log`

### Формат отчета (report.json)

Файл `report.json` содержит результат обработки каждого файла.

**Пример:**
```json
[
  {
    "file": "prod_dop.xml",
    "status": "success",
    "started_at": "2026-01-09T18:30:51+03:00",
    "finished_at": "2026-01-09T18:30:51+03:00",
    "rows_parsed": 5186,
    "rows_inserted": 5186,
    "rows_updated": 0,
    "rows_deleted": 312,
    "row_errors": [],
    "error": null
  },
  {
    "file": "warehouses.xml",
    "status": "success",
    "started_at": "2026-01-09T18:30:51+03:00",
    "finished_at": "2026-01-09T18:31:02+03:00",
    "rows_parsed": 115960,
    "rows_inserted": 12360,
    "rows_updated": 2423,
    "rows_deleted": 11243,
    "row_errors": [
        "Строка 1050: Некорректный формат даты '2024-99-99'"
    ],
    "error": null
  }
]
```

**Поля:**
*   `status`: `success` (успешно) или `failed` (критический сбой всего файла).
*   `rows_parsed`: Сколько строк XML прочитано.
*   `rows_inserted`: Новые записи, добавленные в БД.
*   `rows_updated`: Существующие записи, которые были изменены.
*   `rows_deleted`: Удаленные записи при `delete=true`.
*   `row_errors`: Список ошибок валидации конкретных строк (не прерывают импорт).
*   `error`: Текст критической ошибки (если есть).
