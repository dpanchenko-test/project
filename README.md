# 🚀 DevOps: Микросервисы через Systemd + iptables

**Учебный проект развертывания Go Backend API (:8080), Flask Cache Proxy (:5000) и сетевых правил** на Ubuntu Server через **systemd сервисы**.

[![Статус сервисов](https://github.com/dpanchenko-test/project/raw/master/3.%20Запуск%20сервиса%20(Backend).png)](https://github.com/dpanchenko-test/project)

## 🏗️ Архитектура
Клиент ──HTTP──> Cache API (:5000, Flask+Redis) ──HTTP──> Backend API (:8080, Go+PostgreSQL)
│
iptables правила (rules.service)
│
PostgreSQL + Redis (локальные сервисы)

## 📁 Файлы проекта
| Файл | Описание |
|------|----------|
| `backend-api.service` | Systemd юнит Go backend API |
| `cache-api.service` | Systemd юнит Flask cache-прокси |
| `rules.service` | Systemd сервис iptables правил |
| `rules.sh` | Скрипт настройки файрвола |
| `cache-api.cache-api.spec` | Спецификация Cache API |
| `control` | Скрипт управления сервисами |

**Скриншоты:**
## 📸 Скриншоты (исправленные)
![1. Виртуалки](https://github.com/dpanchenko-test/project/blob/master/1%20%D0%BF%D0%BE%D0%B4%D0%BD%D1%8F%D1%82%D1%8B%20%D0%B2%D0%B8%D1%80%D1%82%D1%83%D0%B0%D0%BB%D0%BA%D0%B8.png) 
![2. БД+Redis](https://github.com/dpanchenko-test/project/raw/master/2_postavili_bd_redis.png)
![3. Backend](https://github.com/dpanchenko-test/project/raw/master/3_zapusk_backend.png)
![4. Curl Backend](https://github.com/dpanchenko-test/project/raw/master/4_uspeshnyy_curl_backend.png)
![5. Через прокси](https://github.com/dpanchenko-test/project/raw/master/5_zapros_proksi.png)

## 🚀 Развертывание (5 минут)

### 1. Подготовка системы
```bash
sudo apt update && sudo apt install -y golang-go python3-pip postgresql redis-server iptables-persistent git
pip3 install flask redis psycopg2-binary requests

### 2. Настройка БД 
sudo systemctl start postgresql redis-server
sudo -u postgres psql <<EOF
CREATE DATABASE app_db;
CREATE USER app_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
EOF

### 3. Размещение и запуск 

git clone https://github.com/dpanchenko-test/project.git ~/project
cd ~/project
sudo cp *.service /etc/systemd/system/
sudo chmod +x rules.sh control
sudo systemctl daemon-reload
sudo systemctl enable backend-api cache-api rules
sudo systemctl start backend-api cache-api rules

### 4. Проверка (статус серверов) 

sudo systemctl status backend-api cache-api rules
./control status  # Через скрипт control


### 5. Статус сервисов 

sudo systemctl status backend-api cache-api rules
./control status  # Через скрипт control

### 6. Тест АПИ 

# Через Cache Proxy (Redis)
curl http://localhost:5000/users/5

# Прямо на Backend
curl http://localhost:8080/users/5

### 7. Ожидаемый ответ

{
  "id": 5,
  "name": "Charlie Davis", 
  "age": 35
}

### 8. Логи 

sudo journalctl -u backend-api -f
sudo journalctl -u cache-api -f  
./control logs backend-api


### 9. Управление

| Команда                  | Описание              |
| ------------------------ | --------------------- |
| ./control start          | Запустить все сервисы |
| ./control stop           | Остановить все        |
| ./control restart        | Перезапустить         |
| ./control status         | Статус                |
| ./control logs <service> | Логи сервиса          |
