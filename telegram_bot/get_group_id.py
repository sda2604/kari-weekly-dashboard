"""
Скрипт для получения ID группы
Добавь бота в группу, затем отправь любое сообщение в группу
"""

import requests

BOT_TOKEN = "8483881283:AAELuJVaYJcm2jNvGOKT0kqwr1pJvfyV9A0"

print("\n" + "="*60)
print("🤖 ПОЛУЧЕНИЕ ID ГРУППЫ")
print("="*60)
print("\nИНСТРУКЦИЯ:")
print("1. Добавь бота в нужную группу")
print("2. Сделай бота администратором группы")
print("3. Отправь любое сообщение в группу (например: 'тест')")
print("4. Нажми Enter здесь")
print("\n" + "="*60 + "\n")

input("Нажми Enter когда будешь готов...")

print("\n⏳ Проверяю сообщения...\n")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get('ok'):
        print("❌ Ошибка подключения к боту")
        print(f"Ответ: {data}")
    elif not data.get('result'):
        print("⚠️  Пока нет сообщений")
        print("Отправь сообщение в группу и запусти скрипт заново")
    else:
        print("✅ Найдены чаты!\n")
        print("="*60)
        
        groups = {}
        users = {}
        
        for update in data['result']:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat['type']
                
                if chat_type in ['group', 'supergroup']:
                    # Это группа
                    title = chat.get('title', 'Unknown')
                    groups[chat_id] = title
                elif chat_type == 'private':
                    # Это личный чат
                    first_name = chat.get('first_name', 'Unknown')
                    username = chat.get('username', 'Unknown')
                    users[chat_id] = (first_name, username)
        
        if groups:
            print("👥 ГРУППЫ:\n")
            for chat_id, title in groups.items():
                print(f"📱 Название: {title}")
                print(f"🆔 GROUP_CHAT_ID: {chat_id}")
                print("-"*60)
            
            print("\n📋 СКОПИРУЙ ЭТОТ ID ДЛЯ config.py:")
            for chat_id in groups.keys():
                print(f"   GROUP_CHAT_ID = {chat_id}")
        else:
            print("⚠️  Групп не найдено")
            print("Убедись что:")
            print("1. Бот добавлен в группу")
            print("2. Бот сделан администратором")
            print("3. Ты отправил сообщение в группу")
        
        if users:
            print("\n" + "="*60)
            print("👤 ЛИЧНЫЕ ЧАТЫ:\n")
            for chat_id, (name, username) in users.items():
                print(f"Пользователь: {name} (@{username})")
                print(f"chat_id: {chat_id}")
                print("-"*60)
        
        print("="*60)

except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n")
input("Нажми Enter для выхода...")
