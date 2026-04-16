import json
import re
import requests
from datetime import datetime
import os
import random

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

CATEGORIES = [
    {"name": "marketing", "display": "📢 Маркетинг", "sub": ["smm", "seo", "email", "copywriting", "ads", "branding", "analytics"]},
    {"name": "coding", "display": "💻 Программирование", "sub": ["python", "javascript", "sql", "algorithms", "devops", "testing", "frontend", "backend"]},
    {"name": "business", "display": "💼 Бизнес", "sub": ["startup", "finance", "sales", "management", "strategy", "hr"]},
    {"name": "translate", "display": "🌐 Перевод", "sub": ["general", "technical", "marketing", "legal", "medical"]},
    {"name": "science", "display": "🔬 Наука", "sub": ["physics", "biology", "math", "history", "chemistry", "astronomy"]},
    {"name": "social", "display": "📱 Соцсети", "sub": ["tiktok", "instagram", "youtube", "telegram", "twitter", "linkedin"]},
    {"name": "creative", "display": "🎨 Креатив", "sub": ["design", "music", "writing", "game", "video"]},
    {"name": "education", "display": "📚 Образование", "sub": ["lesson", "exam", "explain", "course", "summary"]},
    {"name": "lifestyle", "display": "🏠 Лайфстайл", "sub": ["hobby", "diy", "gardening", "pets", "home"]},
    {"name": "health", "display": "🏥 Здоровье", "sub": ["nutrition", "exercise", "mental", "yoga", "meditation"]},
    {"name": "travel", "display": "✈️ Путешествия", "sub": ["planning", "destinations", "tips", "culture"]},
    {"name": "food", "display": "🍳 Кулинария", "sub": ["recipes", "baking", "drinks", "diet"]},
    {"name": "fitness", "display": "💪 Фитнес", "sub": ["workout", "cardio", "strength", "stretching"]},
    {"name": "psychology", "display": "🧠 Психология", "sub": ["therapy", "coaching", "mindfulness", "emotions"]},
    {"name": "finance", "display": "💰 Финансы", "sub": ["investing", "saving", "budgeting", "crypto"]},
    {"name": "gaming", "display": "🎮 Игры", "sub": ["strategies", "rpg", "fps", "guides"]},
    {"name": "music", "display": "🎵 Музыка", "sub": ["production", "songwriting", "instruments", "theory"]},
    {"name": "art", "display": "🎨 Искусство", "sub": ["painting", "drawing", "digital", "sculpture"]},
    {"name": "photography", "display": "📸 Фотография", "sub": ["editing", "lighting", "composition", "color"]},
    {"name": "writing", "display": "✍️ Писательство", "sub": ["fiction", "poetry", "blogging", "journalism"]}
]

SUBCATEGORY_NAMES = {
    "smm": "SMM", "seo": "SEO", "email": "Email", "copywriting": "Копирайтинг", "ads": "Реклама", "branding": "Брендинг", "analytics": "Аналитика",
    "python": "Python", "javascript": "JS", "sql": "SQL", "algorithms": "Алгоритмы", "devops": "DevOps", "testing": "Тестирование", "frontend": "Frontend", "backend": "Backend",
    "startup": "Стартапы", "finance": "Финансы", "sales": "Продажи", "management": "Управление", "strategy": "Стратегия", "hr": "HR",
    "general": "Общий", "technical": "Технический", "legal": "Юридический", "medical": "Медицинский",
    "physics": "Физика", "biology": "Биология", "math": "Математика", "history": "История", "chemistry": "Химия", "astronomy": "Астрономия",
    "tiktok": "TikTok", "instagram": "Instagram", "youtube": "YouTube", "telegram": "Telegram", "twitter": "Twitter", "linkedin": "LinkedIn",
    "design": "Дизайн", "music": "Музыка", "writing": "Письмо", "game": "Игры", "video": "Видео",
    "lesson": "Уроки", "exam": "Тесты", "explain": "Объяснения", "course": "Курсы", "summary": "Конспекты",
    "hobby": "Хобби", "diy": "DIY", "gardening": "Садоводство", "pets": "Питомцы", "home": "Дом",
    "nutrition": "Питание", "exercise": "Упражнения", "mental": "Ментальное", "yoga": "Йога", "meditation": "Медитация",
    "planning": "Планирование", "destinations": "Направления", "tips": "Советы", "culture": "Культура",
    "recipes": "Рецепты", "baking": "Выпечка", "drinks": "Напитки", "diet": "Диеты",
    "workout": "Тренировки", "cardio": "Кардио", "strength": "Силовые", "stretching": "Растяжка",
    "therapy": "Терапия", "coaching": "Коучинг", "mindfulness": "Осознанность", "emotions": "Эмоции",
    "investing": "Инвестиции", "saving": "Сбережения", "budgeting": "Бюджет", "crypto": "Криптовалюты",
    "strategies": "Стратегии", "rpg": "RPG", "fps": "FPS", "guides": "Гайды",
    "production": "Продакшн", "songwriting": "Песни", "instruments": "Инструменты", "theory": "Теория",
    "painting": "Живопись", "drawing": "Рисование", "digital": "Цифровое", "sculpture": "Скульптура",
    "editing": "Редактирование", "lighting": "Освещение", "composition": "Композиция", "color": "Цвет",
    "fiction": "Художественное", "poetry": "Поэзия", "blogging": "Блогинг", "journalism": "Журналистика"
}

TOPICS = [
    "нейросети", "искусственный интеллект", "маркетинг", "программирование", "бизнес",
    "перевод", "наука", "соцсети", "креатив", "образование", "лайфстайл", "здоровье",
    "путешествия", "кулинария", "фитнес", "психология", "финансы", "игры", "музыка",
    "искусство", "фотография", "писательство"
]

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        return None
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 1200}
    }
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data, timeout=45)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return None
    except Exception:
        return None

def call_groq(prompt):
    if not GROQ_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 1200
    }
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=45)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        return None
    except Exception:
        return None

def call_any_api(prompt):
    result = call_gemini(prompt)
    if result:
        print("   ✅ Used Gemini")
        return result
    print("   ⚠️ Gemini failed, trying Groq...")
    result = call_groq(prompt)
    if result:
        print("   ✅ Used Groq")
        return result
    return None

def parse_prompts_from_html():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    pattern = r'const prompts = (\[[\s\S]*?\]);'
    match = re.search(pattern, content)
    
    if not match:
        print("❌ Could not find 'const prompts = [...]' in index.html")
        return []
    
    try:
        prompts = eval(match.group(1))
        print(f"✅ Found {len(prompts)} prompts")
        return prompts
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return []

def save_prompts_to_html(prompts):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    
    prompts_json = json.dumps(prompts, ensure_ascii=False, indent=4)
    pattern = r'(const prompts = )\[[\s\S]*?\];'
    new_content = re.sub(pattern, r'\1' + prompts_json + ';', content)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ Saved {len(prompts)} prompts")

def generate_5_prompts():
    selected_categories = random.sample(CATEGORIES, min(5, len(CATEGORIES)))
    
    categories_info = []
    categories_text = []
    for cat in selected_categories:
        sub = random.choice(cat["sub"])
        topic = random.choice(TOPICS)
        categories_info.append({
            "category": cat["name"],
            "category_display": cat["display"],
            "subcategory": sub,
            "subcategory_display": SUBCATEGORY_NAMES.get(sub, sub),
            "topic": topic
        })
        categories_text.append(f"{len(categories_text)+1}. {cat['display']} / {SUBCATEGORY_NAMES.get(sub, sub)} / {topic}")
    
    prompt_text = f"""Создай 5 уникальных промтов для нейросетей.

Нужны промты на темы:
{chr(10).join(categories_text)}

Формат ответа (ТОЛЬКО JSON массив, без пояснений):
[
  {{
    "title": "название (10-60 символов, русский)",
    "preview": "краткое описание (100-150 символов)",
    "full": "полная инструкция с [переменными]. 300-600 символов."
  }}
]

Требования:
- Каждый промт уникальный и полезный
- Добавляй [переменные в квадратных скобках]
- Структурируй ответ
- Язык: русский"""
    
    print("🎯 Generating 5 prompts...")
    response = call_any_api(prompt_text)
    
    if not response:
        return []
    
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()
    
    try:
        data = json.loads(response)
        if not isinstance(data, list):
            return []
        
        result = []
        for i, item in enumerate(data[:5]):
            if i < len(categories_info):
                result.append({
                    **item,
                    "category": categories_info[i]["category"],
                    "subcategory": categories_info[i]["subcategory"]
                })
        return result
    except Exception as e:
        print(f"❌ JSON error: {e}")
        return []

def main():
    print(f"🚀 Started at {datetime.now()}")
    print(f"📡 Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"📡 Groq: {'✅' if GROQ_API_KEY else '❌'}")
    
    existing = parse_prompts_from_html()
    if not existing:
        print("❌ Could not read prompts")
        return
    
    if len(existing) == 0:
        print("📋 No existing prompts found. Starting fresh...")
        next_id = 1
    else:
        next_id = max(p["id"] for p in existing) + 1
    
    new_prompts = generate_5_prompts()
    if not new_prompts:
        print("❌ Generation failed")
        return
    
    for i, p in enumerate(new_prompts):
        p["id"] = next_id + i
        existing.append(p)
        print(f"  ✅ Added: {p['title']}")
    
    save_prompts_to_html(existing)
    print(f"📊 Total prompts: {len(existing)}")

if __name__ == "__main__":
    main()
