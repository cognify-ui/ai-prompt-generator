import json
import re
import requests
from datetime import datetime
import os
import random
import time

# API ключи
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Gemini API
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Groq API
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Категории
CATEGORIES = [
    {"name": "marketing", "display": "📢 Маркетинг", "sub": ["smm", "seo", "email", "copywriting", "ads", "branding", "analytics"]},
    {"name": "coding", "display": "💻 Программирование", "sub": ["python", "javascript", "sql", "algorithms", "devops", "testing", "frontend", "backend"]},
    {"name": "business", "display": "💼 Бизнес", "sub": ["startup", "finance", "sales", "management", "strategy", "hr"]},
    {"name": "translate", "display": "🌐 Перевод", "sub": ["general", "technical", "marketing", "legal", "medical"]},
    {"name": "science", "display": "🔬 Наука", "sub": ["physics", "biology", "math", "history", "chemistry", "astronomy"]},
    {"name": "social", "display": "📱 Соцсети", "sub": ["tiktok", "instagram", "youtube", "telegram", "twitter", "linkedin"]},
    {"name": "creative", "display": "🎨 Креатив", "sub": ["design", "music", "writing", "game", "video"]},
    {"name": "education", "display": "📚 Образование", "sub": ["lesson", "exam", "explain", "course", "summary"]}
]

SUBCATEGORY_NAMES = {
    "smm": "SMM", "seo": "SEO", "email": "Email", "copywriting": "Копирайтинг", "ads": "Реклама", "branding": "Брендинг", "analytics": "Аналитика",
    "python": "Python", "javascript": "JS", "sql": "SQL", "algorithms": "Алгоритмы", "devops": "DevOps", "testing": "Тестирование", "frontend": "Frontend", "backend": "Backend",
    "startup": "Стартапы", "finance": "Финансы", "sales": "Продажи", "management": "Управление", "strategy": "Стратегия", "hr": "HR",
    "general": "Общий", "technical": "Технический", "legal": "Юридический", "medical": "Медицинский",
    "physics": "Физика", "biology": "Биология", "math": "Математика", "history": "История", "chemistry": "Химия", "astronomy": "Астрономия",
    "tiktok": "TikTok", "instagram": "Instagram", "youtube": "YouTube", "telegram": "Telegram", "twitter": "Twitter", "linkedin": "LinkedIn",
    "design": "Дизайн", "music": "Музыка", "writing": "Письмо", "game": "Игры", "video": "Видео",
    "lesson": "Уроки", "exam": "Тесты", "explain": "Объяснения", "course": "Курсы", "summary": "Конспекты"
}

TOPICS = [
    "нейросети", "искусственный интеллект", "машинное обучение", "чат-боты",
    "генерация контента", "анализ данных", "автоматизация", "обработка текста",
    "генерация изображений", "распознавание речи", "перевод", "резюмирование",
    "классификация", "прогнозирование", "рекомендательные системы", "SEO оптимизация",
    "SMM продвижение", "email маркетинг", "продажи", "управление проектами"
]

def call_gemini(prompt):
    """Вызов Gemini API"""
    if not GEMINI_API_KEY:
        print("⚠️ No Gemini API key")
        return None
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 800}
    }
    
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"⚠️ Gemini error {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Gemini exception: {e}")
        return None

def call_groq(prompt):
    """Вызов Groq API (бесплатно, быстро)"""
    if not GROQ_API_KEY:
        print("⚠️ No Groq API key")
        return None
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"⚠️ Groq error {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Groq exception: {e}")
        return None

def call_any_api(prompt):
    """Пытается вызвать Gemini, если не работает — Groq"""
    print("🔄 Trying Gemini...")
    result = call_gemini(prompt)
    if result:
        print("✅ Gemini succeeded")
        return result
    
    print("🔄 Gemini failed, trying Groq...")
    result = call_groq(prompt)
    if result:
        print("✅ Groq succeeded")
        return result
    
    print("❌ Both APIs failed")
    return None

def parse_prompts_from_html():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'const prompts = (\[[\s\S]*?\]);'
    match = re.search(pattern, content)
    if not match:
        return []
    try:
        prompts = eval(match.group(1))
        return prompts
    except:
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

def generate_new_prompt():
    category = random.choice(CATEGORIES)
    subcategory = random.choice(category["sub"])
    topic = random.choice(TOPICS)
    
    prompt_text = f"""Ты — генератор промтов для нейросетей. Создай ОДИН уникальный промт.

Категория: {category['display']}
Подкатегория: {SUBCATEGORY_NAMES.get(subcategory, subcategory)}
Тема: {topic}

Формат (только JSON, без пояснений):
{{
  "title": "название (10-60 символов, русский)",
  "preview": "краткое описание (100-150 символов, русский)",
  "full": "полная инструкция с [переменными]. Длина 300-600 символов. Используй списки и шаги. Русский язык."
}}

Требования:
- Промт должен быть практичным и полезным
- Добавь [переменные в квадратных скобках]
- Структурируй ответ (списки, шаги)
- Не повторяй шаблонные фразы"""
    
    print(f"🎯 Generating: {category['display']} / {SUBCATEGORY_NAMES.get(subcategory, subcategory)} / {topic}")
    
    response = call_any_api(prompt_text)
    if not response:
        return None
    
    # Очистка ответа
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()
    
    try:
        prompt_data = json.loads(response)
        return {
            **prompt_data,
            "category": category["name"],
            "subcategory": subcategory
        }
    except json.JSONDecodeError as e:
        print(f"❌ JSON error: {e}")
        print(f"Response: {response[:200]}...")
        return None

def main():
    print(f"🚀 Starting auto-generation at {datetime.now()}")
    print(f"📡 Gemini: {'✅' if GEMINI_API_KEY else '❌'}")
    print(f"📡 Groq: {'✅' if GROQ_API_KEY else '❌'}")
    
    existing_prompts = parse_prompts_from_html()
    if not existing_prompts:
        print("❌ Could not load prompts")
        return
    
    print(f"📊 Existing: {len(existing_prompts)}")
    
    # Генерируем 1 новый промт
    new_prompt = generate_new_prompt()
    
    if not new_prompt:
        print("❌ Generation failed")
        return
    
    next_id = max(p["id"] for p in existing_prompts) + 1
    new_prompt["id"] = next_id
    
    existing_prompts.append(new_prompt)
    save_prompts_to_html(existing_prompts)
    
    print(f"✅ Added: {new_prompt['title']}")
    print(f"📊 Total: {len(existing_prompts)}")

if __name__ == "__main__":
    main()
