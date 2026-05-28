import os
import yfinance as yf
from google import genai
from google.genai import types
from datetime import datetime
import requests

# 1. تهيئة العميل
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. حل مشكلة الحظر السحابي عبر إضافة رأس متصفح حقيقي وإدارة الجلسة
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# سحب بيانات الذهب وتجاوز الحظر
gold = yf.Ticker("GC=F", session=session)
hist = gold.history(period="5d", interval="1h")

# التحقق من نجاح سحب البيانات لمنع توقف السكريبت
if hist.empty:
    # حل بديل سريع في حال استمرار حظر الـ Ticker الأساسي
    hist = yf.download("GC=F", period="5d", interval="1h", session=session)

hist_clean = hist.tail(10)

# تحويل البيانات إلى أسطر نصية نقية
data_lines = []
for index, row in hist_clean.iterrows():
    line = f"الوقت: {index.strftime('%Y-%m-%d %H:%M')}, الإغلاق: {row['Close']:.2f}, الأعلى: {row['High']:.2f}, الأدنى: {row['Low']:.2f}"
    data_lines.append(line)
market_data_cleaned = "\n".join(data_lines)

# 3. تعليمات صارمة للتنسيق
SYSTEM_INSTRUCTIONS = """
أنت محلل مالي كمي مؤسسي محترف. مهمتك تحويل البيانات الرقمية لأسعار الذهب إلى تقارير مالية متماسكة باللغة العربية.
شروط التنسيق الصارمة:
1. ممنوع منعا باتاً استخدام الخطوط المنقطة مثل (-------) أو الفواصل التقليدية الممتدة.
2. استخدم العناوين الرئيسية (#) والفرعية (##) ونقاط القوائم المنظمة فقط.
3. التقرير يجب أن يكون متصلاً، جافاً، وخالياً من الفراغات السطرية الزائدة أو الهوامش الفارغة.
4. الاعتماد كلياً على المفاهيم الفنية: الهيكل السعري، مناطق العرض والطلب، والسيولة الكامنة.
"""

# 4. استدعاء الموديل
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"اكتب التقرير المالي الفني مباشرة بناءً على هذه البيانات الرقمية المصفاة، دون وضع أي خطوط منقطة أو مساحات فارغة عشوائية:\n\n{market_data_cleaned}",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        temperature=0.1
    ),
)

# 5. حفظ التقرير
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")
with open(f"reports/XAUUSD-{date_str}.md", "w", encoding="utf-8") as f:
    f.write(response.text.strip())

print("تم توليد التقرير المالي النظيف بنجاح.")
