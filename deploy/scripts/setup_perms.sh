#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Ошибка: запустите скрипт с правами root (sudo)."
  exit 1
fi

NGINX_USER="$1"
BASE_DIR="/opt/xml_data_importer"
REPORTS_DIR="$BASE_DIR/reports"

if [ -z "$NGINX_USER" ]; then
  echo "Ошибка: не указано имя пользователя nginx."
  echo "Использование: $0 <username>"
  echo "Пример: $0 www-data"
  exit 1
fi

echo "Настройка прав для пользователя/группы: $NGINX_USER"

echo "-> Создание директории $REPORTS_DIR"
mkdir -p "$REPORTS_DIR"

echo "-> Установка владельца root:$NGINX_USER"
chown -R root:"$NGINX_USER" "$REPORTS_DIR"

echo "-> Установка прав 775 на директорию отчетов"
chmod -R 775 "$REPORTS_DIR"

echo "-> Открытие доступа к родительским папкам (o+x)"
chmod o+x /opt "$BASE_DIR"

echo "Готово!"
