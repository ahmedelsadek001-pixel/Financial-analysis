import os
import yfinance as yf
from google import genai
from google.genai import types
from datetime import datetime

# 1. تهيئة العميل الجديد باستخدام مكتبة google-genai الحديثة
api_key = os.environ.get("AIzaSyDISaieVf7cbuDhVvrtv461KToRg_F5Xqg")
client = genai.Client(api_key=api_key)

# 2. سحب بيانات أسعار الذهب الحية من الإنترنت مباشرة
gold = yf.Ticker("GC=F")
hist = gold.history(period="5d", interval="1h")
data_string = hist.tail(24).to_string() 

# 3. صياغة القواعد والتعليمات المؤسسية الصارمة للتحليل الفني
SYSTEM_INSTRUCTIONS = """
أنت محلل مالي كمي مؤسسي محترف. وظيفتك تحويل البيانات الرقمية لأسعار الذهب القادمة إلى تقارير مالية صارمة وجافة باللغة العربية.
قواعدك الصارمة:
1. الاعتماد كلياً على الهيكل السعري (BOS/CHoCH)، والسيولة (BSL/SSL)، ومناطق الـ Order Blocks والـ FVG.
2. يمنع منعاً باتاً استخدام لغة عاطفية أو إنشائية أو ترويجية.
"""

# 4. استدعاء الموديل الحديث وإرسال البيانات للتحليل
response = client.models.generate_content(
    model='gemini-2.5-flash', # الموديل الأحدث المدعوم والمستقر تماماً
    contents=f"حلل البيانات السعرية اللحظية التالية للذهب واستخرج التقرير الفني المنسق والمجدول:\n\n{data_string}",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        temperature=0.2 # درجة حرارة منخفضة لضمان دقة وجفاف التقرير المالي بدون ابتكار
    ),
)

# 5. إنشاء المجلد وحفظ ملف التقرير التلقائي بصيغة التاريخ الحالية
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")
with open(f"reports/XAUUSD-{date_str}.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"تم توليد التقرير المالي بنجاح وحفظه في المجلد المحدد.")
