import os
import yfinance as yf
from google import genai
from google.genai import types
from datetime import datetime
import requests

# 1. استقبال الزوج المختار من مدخلات جيتهاب
symbol = os.environ.get("SELECTED_SYMBOL", "GC=F")

# 2. تهيئة العميل
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 3. إدارة الجلسة وتجاوز الحظر السحابي
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# سحب بيانات الزوج المختار
ticker_data = yf.Ticker(symbol, session=session)
hist = ticker_data.history(period="5d", interval="1h")

if hist.empty:
    hist = yf.download(symbol, period="5d", interval="1h", session=session)

hist_clean = hist.tail(15)

data_lines = []
for index, row in hist_clean.iterrows():
    line = f"Time: {index.strftime('%Y-%m-%d %H:%M')}, Close: {row['Close']:.2f}, High: {row['High']:.2f}, Low: {row['Low']:.2f}"
    data_lines.append(line)
market_data_cleaned = "\n".join(data_lines)

# توليد طوابع زمنية دقيقة
current_timestamp_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
current_timestamp_ar = datetime.now().strftime("%Y-%m-%d في تمام الساعة %H:%M:%S")

# 4. صياغة التعليمات الهيكلية لتكون مرنة مع أي زوج مالي
SYSTEM_INSTRUCTIONS = f"""
You are an institutional quantitative financial analyst. Your task is to analyze the provided digital data for the selected asset ({symbol}) and generate a dry, rigorous, and highly structured technical report.

The output must follow this exact sequence and structure without any introductory or conversational text, and absolutely NO dotted lines (-------) or redundant spaces:

# Institutional Asset ({symbol}) Technical Analysis Report
**Execution Timestamp:** {current_timestamp_en}

[Generate the entire technical analysis here in formal financial English. Cover Market Structure (BOS/CHoCH), Order Blocks, Fair Value Gaps (FVG), and Liquidity Sweeps based on the numerical data].

## Key Tactical Levels
- **Execution Entry Zone**: [Identify the exact price range based on the demand/supply block]
- **Invalidation Level (Stop Loss)**: [Exact mathematical risk limitation level]
- **Institutional Targets (Take Profit)**: [Target 1 and Target 2 based on BSL/SSL]
- **Key Support Levels**: [List at least two specific numeric support prices]
- **Key Resistance Levels**: [List at least two specific numeric resistance prices]

# ملخص التقرير المالي الفني للأصل ({symbol})
**توقيت التنفيذ الفعلي:** {current_timestamp_ar}

## هيكل السوق والسيولة الكامنة
[اكتب هنا ملخصاً فنياً صارماً وجافاً باللغة العربية يشرح حركة السعر وتغير الهيكل السعري ومناطق تصفية السيولة بناءً على التحليل أعلاه].

## المستويات التكتيكية الحسمة
- **منطقة الدخول التنفيذية (Entry Zone)**: [المستوى الرقمي]
- **مستوى إلغاء الفكرة (Stop Loss)**: [المستوى الرقمي]
- **الأهداف المؤسسية (Take Profits)**: [المستويات الرقمية المستهدفة]
- **مستويات الدعم الرئيسية (Support)**: [المستويات الرقمية]
- **مستويات المقاومة الرئيسية (Resistance)**: [المستويات الرقمية]
"""

# 5. استدعاء الموديل
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"Generate the institutional English report followed by the Arabic summary based on this clean data for {symbol}. Ensure strict alignment with the requested tactical levels and timestamps: \n\n{market_data_cleaned}",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        temperature=0.1
    ),
)

# 6. حفظ التقرير باسم يتوافق مع الرمز المختار والتاريخ الحاضر لسهولة الفرز
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")
# تنظيف اسم الملف في حال احتواء الرمز على رموز خاصة كالفوركس
file_symbol = symbol.replace("=", "").replace("-", "")
with open(f"reports/{file_symbol}-{date_str}.md", "w", encoding="utf-8") as f:
    f.write(response.text.strip())

print(f"تم توليد تقرير {symbol} بنجاح.")
