import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

# 頁面設定
st.set_page_config(page_title="評論相關熱點分布", layout="wide")
st.title("🎯 評論相關熱點分布")

# 1. 建立電商專用停用詞黑名單
STOP_WORDS = {
    'the', 'and', 'to', 'a', 'of', 'it', 'in', 'is', 'i', 'that', 'for', 'this', 
    'with', 'my', 'was', 'on', 'not', 'but', 'as', 'have', 'are', 'be', 'so', 
    'they', 'you', 'just', 'like', 'very', 'all', 'would', 'out', 'if', 'about',
    'or', 'me', 'from', 'can', 'has', 'had', 'up', 'do', 'than', 'because', 'when',
    'what', 'which', 'your', 'were', 'there', 'their', 'an', 'we', 'at', 'them',
    'product', 'item', 'amazon', 'bought', 'buy', 'purchased', 'get', 'got', 
    'one', 'really', 'even', 'much', 'good', 'bad', 'don', 'didn', 'doesn',
    'use', 'used', 'using', 'time', 'work', 'worked', 'money', 'back', 'return',
    'review', 'reviews', 'tried', 'try', 'way', 'make', 'made', 'did', 'well'
}

# 2. 核心統計函式
def get_word_freq(df, stop_words):
    if df.empty:
        return pd.DataFrame(columns=['熱點關鍵字', '出現頻次'])
    # 合併內容並轉小寫
    all_text = " ".join(df['Content'].dropna().astype(str).tolist()).lower()
    # 提取單字
    words = re.findall(r'\b[a-z]{3,}\b', all_text)
    # 過濾停用詞
    meaningful_words = [word for word in words if word not in stop_words]
    # 取前 20 名
    word_counts = Counter(meaningful_words).most_common(20)
    return pd.DataFrame(word_counts, columns=['熱點關鍵字', '出現頻次'])

# 3. 檔案上傳
uploaded_file = st.file_uploader("上傳 Review 報表 (CSV/Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            target_sheet = next((s for s in excel_file.sheet_names if 'Review' in s), excel_file.sheet_names[0])
            df = pd.read_excel(uploaded_file, sheet_name=target_sheet)

        if 'Rating' in df.columns and 'Content' in df.columns:
            # 準備三種數據集
            df_all = df
            df_positive = df[df['Rating'] >= 4]
            df_negative = df[df['Rating'] <= 3]

            # 建立分頁
            tab1, tab2, tab3 = st.tabs(["📊 整體熱點", "🟢 好評熱點 (4-5星)", "🔴 負評熱點 (1-3星)"])

            with tab1:
                st.subheader("整體評論關鍵字分布")
                df_freq_all = get_word_freq(df_all, STOP_WORDS)
                if not df_freq_all.empty:
                    fig = px.bar(df_freq_all, x='熱點關鍵字', y='出現頻次', color='出現頻次', color_continuous_scale='Blues', title="整體熱點排行")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("無足夠數據進行分析")

            with tab2:
                st.subheader("好評核心賣點 (4-5星)")
                df_freq_pos = get_word_freq(df_positive, STOP_WORDS)
                if not df_freq_pos.empty:
                    fig = px.scatter(df_freq_pos, x="熱點關鍵字", y="出現頻次", size="出現頻次", color="出現頻次", color_continuous_scale='Greens', size_max=60, title="好評泡泡圖")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暫無好評數據")

            with tab3:
                st.subheader("負評痛點分布 (1-3星)")
                df_freq_neg = get_word_freq(df_negative, STOP_WORDS)
                if not df_freq_neg.empty:
                    fig = px.scatter(df_freq_neg, x="熱點關鍵字", y="出現頻次", size="出現頻次", color="出現頻次", color_continuous_scale='Reds', size_max=60, title="負評泡泡圖")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暫無負評數據")
        else:
            st.error("缺少 'Rating' 或 'Content' 欄位")
    except Exception as e:
        st.error(f"發生錯誤: {e}")
