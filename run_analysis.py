import os
import yfinance as yf
from google import genai
from google.genai import types
from datetime import datetime
import requests

# 1. استقبال الزوج وتصحيح الرمز تلقائياً إذا كان ذهب لضمان السعر الفوري المحدث
input_symbol = os.environ.get("SELECTED_SYMBOL", "GC=F")
symbol = "XAUUSD=X" if input_symbol in ["GC=F", "XAUUSD", "XAUUSD=X"] else input_symbol

# 2. تهيئة عميل Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 3. إدارة الجلسة لمنع الحظر وجلب بيانات حية نقية
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# سحب البيانات لآخر 3 أيام بفريم الساعة لضمان الدقة وتجنب التداخل التاريخي
ticker_data = yf.Ticker(symbol, session=session)
hist = ticker_data.history(period="3d", interval="1h")

if hist.empty:
    hist = yf.download(symbol, period="3d", interval="1h", session=session)

# أخذ آخر 12 شمعة لتطابق حركة الشارت اللحظية تماماً
hist_clean = hist.tail(12)

data_lines = []
for index, row in hist_clean.iterrows():
    line = f"Time: {index.strftime('%Y-%m-%d %H:%M')}, Close: {row['Close']:.2f}, High: {row['High']:.2f}, Low: {row['Low']:.2f}"
    data_lines.append(line)
market_data_cleaned = "\n".join(data_lines)

# توليد طوابع زمنية دقيقة للحظة التنفيذ
current_timestamp_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
current_timestamp_ar = datetime.now().strftime("%Y-%m-%d في تمام الساعة %H:%M:%S")

# 4. صياغة التوجيهات الهيكلية الصارمة للدمج بين SMC ونظرية داو بناءً على السعر الحقيقي
SYSTEM_INSTRUCTIONS = f"""
You are an institutional quantitative financial analyst expert in both Smart Money Concepts (SMC) and Classical Dow Theory. Your task is to analyze the provided price data for ({symbol}) and generate a rigorous technical report.

The output must follow this exact sequence and structure without any introductory text, and absolutely NO dotted lines (-------) or redundant spaces:

# Institutional {symbol} Structural Convergence Report
**Execution Timestamp:** {current_timestamp_en}

## 1. Dow Theory Phase & Trend Validation
[Analyze the trend based on Dow Theory principles: accumulation/distribution phases, peak-and-trough progression (Higher Highs/Higher Lows or Lower Highs/Lower Lows), and closing price confirmations based on the data].

## 2. Smart Money Concepts (SMC) Liquidity & Order Flow Matrix
[Analyze the market using SMC mechanics: Identify structural shifts (BOS/CHoCH), liquidity pools (BSL/SSL sweeps), Order Blocks (OB), and Fair Value Gaps (FVG) based on the data].

## 3. Confluence Tactical Levels
- **Execution Entry Zone**: [Exact numeric range based on OB/FVG alignment]
- **Structural Invalidation (Stop Loss)**: [Exact numeric level protecting the setup]
- **Take Profit Objectives**: Target 1: [Numeric Price], Target 2: [Numeric Price]
- **Key Support Levels**: [Two specific numeric prices]
- **Key Resistance Levels**: [Two specific numeric prices]

# ملخص التقرير المالي الفني التوافقي (SMC / Dow Theory)
**توقيت التنفيذ الفعلي:** {current_timestamp_ar}

## أولاً: التحليل الهيكلي التوافقي (مفصل)
[اكتب تحليل مفصل وشامل باللغة العربية يربط بين اتجاه داو الكلاسيكي وتدفق السيولة ومناطق العرض والطلب الخاصة بـ SMC بناءً على المعطيات الرقمية الممررة].

## ثانياً: المستويات التكتيكية الحاسمة (مختصر في نقاط)
- **منطقة الدخول التنفيذية (Entry Zone)**: [المستوى الرقمي المحدث]
- **مستوى إلغاء الفكرة (Stop Loss)**: [المستوى الرقمي المحدث]
- **الأهداف المؤسسية (Take Profits)**: [المستويات الرقمية المستهدفة المحدثة]
- **مستويات الدعم الرئيسية (Support)**: [المستويات الرقمية المحدثة]
- **مستويات المقاومة الرئيسية (Resistance)**: [المستويات الرقمية المحدثة]
"""

# 5. استدعاء النموذج لتوليد التحليل المزدوج بالأسعار الصحيحة
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"Generate the dual SMC and Dow Theory report based on this real-time data for {symbol}:\n\n{market_data_cleaned}",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        temperature=0.1
    ),
)

# 6. حفظ التقرير بآلية تسمية منضبطة ومستقرة
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")

if symbol in ["XAUUSD=X", "GC=F"]:
    filename = f"XAUUSD-{date_str}.md"
else:
    filename = f"{symbol.replace('=', '').replace('-', '')}-{date_str}.md"

with open(f"reports/{filename}", "w", encoding="utf-8") as f:
    f.write(response.text.strip())

print(f"تم تصحيح جلب البيانات وتوليد التقرير الحقيقي بنجاح وحفظه باسم {filename}.")
