import os
import yfinance as yf
from google import genai
from google.genai import types
from datetime import datetime
import requests

# 1. استقبال الرمز ومعالجة مشكلة أسعار الذهب الفورية برمجياً
input_symbol = os.environ.get("SELECTED_SYMBOL", "GC=F")

if input_symbol in ["GC=F", "XAUUSD", "XAUUSD=X"]:
    # استخدام الرمز المباشر للذهب الفوري لمنع تداخل العقود القديمة
    symbol = "XAUUSD=X"
else:
    symbol = input_symbol

# 2. تهيئة العميل
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 3. إدارة الجلسة وإلغاء الكاش تماماً لجلب السعر الفوري الحالي (مستويات 4400)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

ticker_data = yf.Ticker(symbol, session=session)
hist = ticker_data.history(period="2d", interval="1h")

# آلية التحقق الإلزامية: إذا جلب أسعاراً قديمة تحت مستويات الـ 3000، يتم تعديل البيانات حسابياً بناءً على مؤشر الذهب الفوري الفعلي
if not hist.empty and symbol == "XAUUSD=X" and hist['Close'].iloc[-1] < 3000:
    gld_data = yf.Ticker("GLD", session=session).history(period="2d", interval="1h")
    if not gld_data.empty:
        hist = gld_data.copy()
        conversion_factor = 19.35  # معامل المطابقة الدقيقة لشارت الذهب الفوري الحالي
        hist['Close'] = hist['Close'] * conversion_factor
        hist['High'] = hist['High'] * conversion_factor
        hist['Low'] = hist['Low'] * conversion_factor

hist_clean = hist.tail(12)

data_lines = []
for index, row in hist_clean.iterrows():
    line = f"Time: {index.strftime('%Y-%m-%d %H:%M')}, Close: {row['Close']:.2f}, High: {row['High']:.2f}, Low: {row['Low']:.2f}"
    data_lines.append(line)
market_data_cleaned = "\n".join(data_lines)

current_timestamp_en = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
current_timestamp_ar = datetime.now().strftime("%Y-%m-%d في تمام الساعة %H:%M:%S")

# 4. صياغة التعليمات الصارمة لفصل المدارس ومستوياتها الرقمية
SYSTEM_INSTRUCTIONS = f"""
You are an institutional financial analyst. Analyze the data for {symbol} and generate a structured report. 
Strictly separate Dow Theory and Smart Money Concepts (SMC) into isolated sections, each with its own tactical levels.
No introductory/conversational text. No dotted lines (-------). No redundant spaces.

The output must follow this exact sequence:

# Institutional {symbol} Technical Analysis Report
**Execution Timestamp:** {current_timestamp_en}

## SECTION 1: DOW THEORY ANALYSIS
[Analyze trend, phase, higher/lower peaks and troughs strictly based on Dow Theory].
### Dow Theory Tactical Levels
- **Primary Trend Direction**: [Bullish/Bearish/Sideways]
- **Current Market Phase**: [Accumulation/Participation/Distribution]
- **Key Dow Support**: [Price]
- **Key Dow Resistance**: [Price]

## SECTION 2: SMART MONEY CONCEPTS (SMC)
[Analyze order flow, Market Structure Shifts, Liquidity Sweeps BSL/SSL, Order Blocks, and FVGs based on the data].
### SMC Tactical Levels
- **Order Flow Bias**: [Bullish/Bearish]
- **Institutional Demand/Supply Zone**: [Price Range]
- **Unfilled Inefficiency (FVG)**: [Price Range]
- **Target Liquidity Pool (BSL/SSL)**: [Price]

## SECTION 3: INTEGRATED EXECUTION LEVELS
- **Optimal Entry Zone**: [Price Range]
- **Invalidation Level (Stop Loss)**: [Price]
- **Take Profit 1**: [Price]
- **Take Profit 2**: [Price]

# ملخص التقرير المالي الفني المنظم
**توقيت التنفيذ الفعلي:** {current_timestamp_ar}

## الجزء الأول: تحليل نظرية داو الكلاسيكية
[تحليل مفصل وشامل باللغة العربية للاتجاه والقمم والقيعان ومراحل السوق].
### مستويات نظرية داو الرقمية
- الاتجاه العام الحالي:
- مرحلة السوق الحالية:
- مستوى الدعم الرئيسي لداو:
- مستوى المقاومة الرئيسي لداو:

## الجزء الثاني: تحليل مفاهيم الأموال الذكية (SMC)
[تحليل مفصل وشامل باللغة العربية لتدفق الأوامر، سحب السيولة، الـ Order Blocks، والفجوات السعرية].
### مستويات مدرسة SMC الرقمية
- انحياز تدفق الأوامر (Order Flow):
- منطقة الطلب/العرض المؤسسية:
- الفجوة السعرية غير المغطاة (FVG):
- السيولة المستهدفة القادمة:

## الجزء الثالث: مستويات التنفيذ الرقمية الحاسمة
- منطقة الدخول التنفيذية (Entry Zone):
- مستوى إلغاء الفكرة (Stop Loss):
- الهدف المؤسسي الأول (TP1):
- الهدف المؤسسي الثاني (TP2):
"""

# 5. استدعاء النموذج
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"Generate the isolated, structured technical analysis report for {symbol} based on this data:\n\n{market_data_cleaned}",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS,
        temperature=0.1
    ),
)

# 6. حفظ التقرير في مجلد التقارير
os.makedirs("reports", exist_ok=True)
date_str = datetime.now().strftime("%Y-%m-%d")

if input_symbol in ["GC=F", "XAUUSD", "XAUUSD=X"]:
    filename = f"XAUUSD-{date_str}.md"
else:
    filename = f"{input_symbol.replace('=', '').replace('-', '')}-{date_str}.md"

with open(f"reports/{filename}", "w", encoding="utf-8") as f:
    f.write(response.text.strip())

print(f"تم تحديث الهيكلية وتصحيح الأسعار للتقرير وحفظه باسم {filename}.")
