#!/bin/bash
set -e
echo "Настройка сетевых правил..."

# IP-адреса
PROXY_IP="192.168.121.174"
BACKEND_IP="192.168.121.214"
POSTGRES_PORT="5432"

# Очистка существующих правил
iptables -F
iptables -X
iptables -Z

# Политики по умолчанию
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Разрешить loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Разрешить SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Разрешение на исходящие соединения
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Правила для конкретных хостов:
if ip a | grep -q "$PROXY_IP"; then

    ### ПРАВИЛА ДЛЯ PROXY ###

    # Прокси принимает запросы от любого источника
    iptables -I INPUT 3 -p tcp --dport 5000 -j ACCEPT

    # Прокси имеет доступ к Redis (127.0.0.1:6379, т.к. на той же ВМ)

    # Прокси имеет доступ к Backend (в OUTPUT всё разрешено по умолчанию)

    echo "Правила iptables установлены для прокси."

elif ip a | grep -q "$BACKEND_IP"; then
    ### ПРАВИЛА ДЛЯ BACKEND ###

    # Backend принимает запросы только от прокси.
    iptables -A INPUT -p tcp --dport 8080 -s $PROXY_IP -j ACCEPT

    # Backend имеет доступ только к PostgreSQL (на той же ВМ).

    # PostgreSQL принимает подключения только от Backend (на той же ВМ).
    iptables -A INPUT -p tcp --dport $POSTGRES_PORT -s 127.0.0.1 -j ACCEPT
    iptables -A INPUT -p tcp --dport $POSTGRES_PORT -j DROP

    echo "Правила iptables установлены для бэкэнда."

else
    echo "IP не совпал ни с PROXY, ни с BACKEND — правила не применены!"
    exit 1
fi

# Логирование дропа для отладки
iptables -A INPUT -j LOG --log-prefix "iptables denied: " --log-level 7
