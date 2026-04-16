import json
import re
import requests
from datetime import datetime
import os
import random

# API ключи из Secrets GitHub
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# API endpoints
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
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
    "SEO оптимизация", "SMM продвижение", "email маркетинг", "продажи",
    "управление проектами", "копирайтинг", "брендинг", "аналитика", "тестирование"
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
    print("   ❌ Both APIs failed")
    return None

def parse_prompts_from_html():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'const prompts = (\[[\s\S]*?\]);'
    match = re.search(pattern, content)
    if not match:
        return []
    try:
        return eval(match.group(1))
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
    print(f"✅ Saved {len(prompts)} prompts to index.html")

def generate_5_prompts():
    """Генерирует 5 уникальных промтов за один запрос"""
    
    # Случайные категории для разнообразия
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
        categories_text.append(f"{len(categories_text)+1}. Категория: {cat['display']}, Подкатегория: {SUBCATEGORY_NAMES.get(sub, sub)}, Тема: {topic}")
    
    categories_list = "\n".join(categories_text)
    
    prompt_text = f"""Ты — генератор промтов для нейросетей. Создай 5 (ПЯТЬ) уникальных промтов.

Вот какие нужны промты:
{categories_list}

Формат ответа (только JSON массив из 5 объектов, без пояснений):
[
  {{
    "title": "название (10-60 символов, русский)",
    "preview": "краткое описание (100-150 символов, русский)",
    "full": "полная инструкция с [переменными]. Длина 300-600 символов. Используй списки и шаги."
  }}
]

Требования:
- Каждый промт должен быть уникальным и полезным
- Добавляй [переменные в квадратных скобках]
- Структурируй ответ (списки, шаги)
- Не повторяй шаблонные фразы
- Язык: русский"""
    
    print("🎯 Generating 5 prompts in one request...")
    response = call_any_api(prompt_text)
    
    if not response:
        print("❌ API call failed")
        return []
    
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
        prompts_data = json.loads(response)
        if not isinstance(prompts_data, list):
            print("❌ Response is not a list")
            return []
        
        # Добавляем категории к каждому промту
        result = []
        for i, prompt_data in enumerate(prompts_data[:5]):
            if i < len(categories_info):
                result.append({
                    **prompt_data,
                    "category": categories_info[i]["category"],
                    "subcategory": categories_info[i]["subcategory"]
                })
        return result
    except json.JSONDecodeError as e:
        print(f"❌ JSON error: {e}")
        print(f"Response preview: {response[:200]}...")
        return []

def main():
    print(f"🚀 Starting auto-generation at {datetime.now()}")
    print(f"📡 Gemini API key: {'✅ set' if GEMINI_API_KEY else '❌ missing'}")
    print(f"📡 Groq API key: {'✅ set' if GROQ_API_KEY else '❌ missing'}")
    
    existing_prompts = parse_prompts_from_html()
    if not existing_prompts:
        print("❌ Could not load prompts from index.html")
        return
    
    print(f"📊 Existing prompts: {len(existing_prompts)}")
    
    # Генерируем 5 новых промтов
    new_prompts = generate_5_prompts()
    
    if not new_prompts:
        print("❌ Generation failed, no new prompts added")
        return
    
    next_id = max(p["id"] for p in existing_prompts) + 1
    for i, prompt in enumerate(new_prompts):
        prompt["id"] = next_id + i
        existing_prompts.append(prompt)
        print(f"  ✅ Added: {prompt['title']}")
    
    save_prompts_to_html(existing_prompts)
    print(f"📊 Total prompts now: {len(existing_prompts)}")

if __name__ == "__main__":
    main()
