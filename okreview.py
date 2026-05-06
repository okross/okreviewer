import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="負評痛點分析器", layout="wide")
st.title("🎯 1~3星 負評痛點關鍵字分析")

# 1. 建立停用詞黑名單 (Stop Words)
# 我們不僅放基礎英文，還放入電商常見的無意義詞彙
STOP_WORDS = {
    # 基礎英文介系詞、代名詞、連接詞
    'the', 'and', 'to', 'a', 'of', 'it', 'in', 'is', 'i', 'that', 'for', 'this', 
    'with', 'my', 'was', 'on', 'not', 'but', 'as', 'have', 'are', 'be', 'so', 
    'they', 'you', 'just', 'like', 'very', 'all', 'would', 'out', 'if', 'about',
    'or', 'me', 'from', 'can', 'has', 'had', 'up', 'do', 'than', 'because', 'when',
    'what', 'which', 'your', 'were', 'there', 'their', 'an', 'we', 'at', 'them',
    # 電商常見起手式與無意義詞 (依據經驗加入)
    'product', 'item', 'amazon', 'bought', 'buy', 'purchased', 'get', 'got', 
    'one', 'really', 'even', 'much', 'good', 'bad', 'don', 'didn', 'doesn',
    'use', 'used', 'using', 'time', 'work', 'worked', 'money', 'back', 'return',
    'review', 'reviews', 'tried', 'try', 'way', 'make', 'made', 'did', 'well'
}

# 2. 檔案上傳區
uploaded_file = st.file_uploader("上傳你的 Review 報表 (CSV)", type=['csv'])

if uploaded_file is not None:
    # 讀取 CSV
    df = pd.read_csv(uploaded_file)
    
    # 確保有需要的欄位
    if 'Rating' in df.columns and 'Content' in df.columns:
        
        # 3. 篩選 1~3 星的負評
        negative_reviews = df[df['Rating'] <= 3].copy()
        st.write(f"總共找到 **{len(negative_reviews)}** 筆 1~3 星評論。")
        
        if not negative_reviews.empty:
            # 4. 文字清洗與字頻統計邏輯
            # 將所有負評內容合併成一個大字串
            all_text = " ".join(negative_reviews['Content'].dropna().astype(str).tolist()).lower()
            
            # 使用正則表達式 (Regex) 只提取出英文字母的單字，並過濾掉太短的字 (長度 < 3)
            words = re.findall(r'\b[a-z]{3,}\b', all_text)
            
            # 核心步驟：如果單字不在黑名單(STOP_WORDS)裡面，才保留下來
            meaningful_words = [word for word in words if word not in STOP_WORDS]
            
            # 計算詞頻，取出前 20 大最常出現的詞
            word_counts = Counter(meaningful_words).most_common(20)
            df_words = pd.DataFrame(word_counts, columns=['Keyword', 'Frequency'])
            
            # 5. 視覺化：呈現痛點分析
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("🔥 痛點排行榜")
                st.dataframe(df_words, use_container_width=True)
                
            with col2:
                st.subheader("🫧 痛點泡泡圖")
                fig = px.scatter(
                    df_words, 
                    x="Keyword", 
                    y="Frequency", 
                    size="Frequency", 
                    color="Frequency",
                    hover_name="Keyword", 
                    size_max=60,
                    color_continuous_scale=px.colors.sequential.Reds # 使用紅色系代表負評痛點
                )
                # 調整圖表外觀
                fig.update_layout(xaxis_title="痛點關鍵字", yaxis_title="被提及次數")
                st.plotly_chart(fig, use_container_width=True)
                
    else:
        st.error("上傳的 CSV 檔案缺少 'Rating' 或 'Content' 欄位，請檢查檔案格式！")
