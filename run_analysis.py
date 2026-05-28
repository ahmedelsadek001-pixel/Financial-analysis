import os
import yfinance as yf
import google.generativeai as genai
from datetime import datetime

# الإعداد الآمن للذكاء الاصطناعي عبر خوادم جيتهاب
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# سحب بيانات الذهب الحية من السحاب مباشرة (بديل MT5 السحابي)
gold = yf.Ticker("GC=F")
hist = gold.history(period="5d", interval="1h")
data_string = hist.tail(24).to_string() 

# استدعاء قواعد التحليل الصارمة باللغة العربية
SYSTEM_INSTRUCTIONS = """
أنت محلل مالي كمي مؤسسي. وظيفتك تحويل البيانات الرقمية للأسعار إلى تقارير مالية صارمة وجافة باللغة العربية.
قواعدك:
1. الاعتماد كلياً على الهيكل السعري (BOS/CHoCH)، السيولة (BSL/SSL)، ومناطق الـ Order Blocks والـ FVG.
2. يمنع استخدام أي لغة عاطفية أو إنشائية.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=SYSTEM_INSTRUCTIONS
)

prompt = f"حلل البيانات السعرية التالية للذهب واستخرج التقرير الفني المنسق وفقاً للقالب المعتمد:\n\n{data_string}"
response = model.generate_content(prompt)

# إنشاء مجلد التقارير وحفظ الملف تلقائياً بداخل المستودع
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")
with open(f"reports/XAUUSD-{date_str}.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("تم توليد التقرير بنجاح.")
