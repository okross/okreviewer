import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="Review 痛點分析器 Pro", layout="wide")
st.title("🎯 負評痛點關鍵字分析 (支援 Excel/CSV)")

# 停用詞設定 (維持之前的邏輯)
STOP_WORDS = {
    'the', 'and', 'to', 'a', 'of', 'it', 'in', 'is', 'i', 'that', 'for', 'this', 
    'with', 'my', 'was', 'on', 'not', 'but', 'as', 'have', 'are', 'be', 'so', 
    'they', 'you', 'just', 'like', 'very', 'all', 'would', 'out', 'if', 'about',
    'or', 'me', 'from', 'can', 'has', 'had', 'up', 'do', 'than', 'because', 'when',
    'product', 'item', 'amazon', 'bought', 'buy', 'purchased', 'get', 'got', 
    'one', 'really', 'even', 'much', 'good', 'bad', 'don', 'didn', 'doesn',
    'use', 'used', 'using', 'time', 'work', 'worked', 'money', 'back', 'return',
    'review', 'reviews', 'tried', 'try', 'way', 'make', 'made', 'did', 'well'
}

# 1. 檔案上傳區：增加 xlsx 和 xls 支援
uploaded_file = st.file_uploader("上傳 Review 報表", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # 根據副檔名判斷讀取方式
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # 讀取 Excel 檔案
            # 賣家精靈的檔案通常有多個 Sheet，我們嘗試抓取名稱包含 'Review' 的 Sheet
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            # 自動尋找目標 Sheet，如果沒找到就選第一個
            target_sheet = sheet_names[0]
            for sheet in sheet_names:
                if 'Review' in sheet:
                    target_sheet = sheet
                    break
            
            df = pd.read_excel(uploaded_file, sheet_name=target_sheet)

        # 2. 檢查欄位是否存在
        if 'Rating' in df.columns and 'Content' in df.columns:
            
            # 3. 數據過濾
            negative_reviews = df[df['Rating'] <= 3].copy()
            st.success(f"檔案讀取成功！從分頁 [{target_sheet if not uploaded_file.name.endswith('.csv') else 'CSV'}] 找到 {len(negative_reviews)} 筆負評。")
            
            if not negative_reviews.empty:
                # 4. 文字清洗
                all_text = " ".join(negative_reviews['Content'].dropna().astype(str).tolist()).lower()
                words = re.findall(r'\b[a-z]{3,}\b', all_text)
                meaningful_words = [word for word in words if word not in STOP_WORDS]
                
                # 5. 統計與視覺化
                word_counts = Counter(meaningful_words).most_common(20)
                df_words = pd.DataFrame(word_counts, columns=['Keyword', 'Frequency'])
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("🔥 痛點排行榜")
                    st.table(df_words) # 使用 table 更整齊
                    
                with col2:
                    st.subheader("🫧 痛點泡泡圖")
                    fig = px.scatter(
                        df_words, x="Keyword", y="Frequency", size="Frequency", 
                        color="Frequency", hover_name="Keyword", size_max=60,
                        color_continuous_scale=px.colors.sequential.Reds
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"找不到關鍵欄位。目前的欄位有：{', '.join(df.columns)}")
            st.info("提示：請確保 Excel 中的欄位名稱包含 'Rating' 與 'Content'。")

    except Exception as e:
        st.error(f"讀取檔案時發生錯誤: {e}")
