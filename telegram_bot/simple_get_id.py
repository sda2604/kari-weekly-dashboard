"""
Простой скрипт для получения chat_id
Запусти, затем отправь /start боту в Telegram
"""

import requests
import time

BOT_TOKEN = "8483881283:AAELuJVaYJcm2jNvGOKT0kqwr1pJvfyV9A0"

print("\n" + "="*60)
print("🤖 ПОЛУЧЕНИЕ CHAT_ID")
print("="*60)
print("\nИНСТРУКЦИЯ:")
print("1. Найди своего бота в Telegram")
print("2. Отправь боту команду: /start")
print("3. Подожди 5 секунд")
print("4. Твой chat_id появится ниже")
print("\n" + "="*60 + "\n")

input("Нажми Enter когда будешь готов...")

print("\n⏳ Проверяю сообщения...\n")

# Получаем обновления
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get('ok'):
        print("❌ Ошибка подключения к боту")
        print(f"Ответ: {data}")
    elif not data.get('result'):
        print("⚠️  Пока нет сообщений")
        print("Отправь /start боту и запусти скрипт заново")
    else:
        print("✅ Найдены сообщения!\n")
        print("="*60)
        
        chat_ids = set()
        for update in data['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                username = update['message']['chat'].get('username', 'Unknown')
                first_name = update['message']['chat'].get('first_name', 'Unknown')
                
                chat_ids.add(chat_id)
                
                print(f"👤 Пользователь: {first_name} (@{username})")
                print(f"📱 chat_id: {chat_id}")
                print("-"*60)
        
        print("\n📋 СКОПИРУЙ ЭТОТ CHAT_ID:")
        for chat_id in chat_ids:
            print(f"   {chat_id}")
        print("="*60)

except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка сети: {e}")
    print("\nПроверь подключение к интернету")

except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n")
input("Нажми Enter для выхода...")
