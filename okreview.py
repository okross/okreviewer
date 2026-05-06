import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px

# 頁面設定
st.set_page_config(page_title="負評相關熱點分布", layout="wide")
st.title("🎯 負評相關熱點分布")

# 1. 建立電商專用停用詞黑名單 (Stop Words)
STOP_WORDS = {
    # 基礎英文
    'the', 'and', 'to', 'a', 'of', 'it', 'in', 'is', 'i', 'that', 'for', 'this', 
    'with', 'my', 'was', 'on', 'not', 'but', 'as', 'have', 'are', 'be', 'so', 
    'they', 'you', 'just', 'like', 'very', 'all', 'would', 'out', 'if', 'about',
    'or', 'me', 'from', 'can', 'has', 'had', 'up', 'do', 'than', 'because', 'when',
    'what', 'which', 'your', 'were', 'there', 'their', 'an', 'we', 'at', 'them',
    # 電商常見無意義詞
    'product', 'item', 'amazon', 'bought', 'buy', 'purchased', 'get', 'got', 
    'one', 'really', 'even', 'much', 'good', 'bad', 'don', 'didn', 'doesn',
    'use', 'used', 'using', 'time', 'work', 'worked', 'money', 'back', 'return',
    'review', 'reviews', 'tried', 'try', 'way', 'make', 'made', 'did', 'well'
}

# 2. 檔案上傳區
uploaded_file = st.file_uploader("上傳 Review 報表 (支援 CSV, XLSX, XLS)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # 根據副檔名讀取資料
        target_sheet = "CSV"
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # 處理 Excel 多分頁邏輯 (對標賣家精靈格式)
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            # 自動尋找目標分頁
            target_sheet = sheet_names[0]
            for sheet in sheet_names:
                if 'Review' in sheet:
                    target_sheet = sheet
                    break
            df = pd.read_excel(uploaded_file, sheet_name=target_sheet)

        # 3. 檢查關鍵欄位
        if 'Rating' in df.columns and 'Content' in df.columns:
            
            # 4. 篩選 1~3 星的負評
            negative_reviews = df[df['Rating'] <= 3].copy()
            st.success(f"讀取成功！從 [{target_sheet}] 識別出 {len(negative_reviews)} 筆負評資料。")
            
            if not negative_reviews.empty:
                # 5. 文字清洗與統計
                # 合併所有負評內容並轉小寫
                all_text = " ".join(negative_reviews['Content'].dropna().astype(str).tolist()).lower()
                # 提取長度大於等於 3 的單字
                words = re.findall(r'\b[a-z]{3,}\b', all_text)
                # 過濾停用詞
                meaningful_words = [word for word in words if word not in STOP_WORDS]
                
                # 計算詞頻，取前 20 名
                word_counts = Counter(meaningful_words).most_common(20)
                df_words = pd.DataFrame(word_counts, columns=['熱點關鍵字', '出現頻次'])
                
                # 6. 視覺化排版
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("🔥 負評熱詞排行")
                    st.dataframe(df_words, use_container_width=True)
                    
                with col2:
                    st.subheader("🫧 熱點頻次分布")
                    fig = px.scatter(
                        df_words, 
                        x="熱點關鍵字", 
                        y="出現頻次", 
                        size="出現頻次", 
                        color="出現頻次",
                        hover_name="熱點關鍵字", 
                        size_max=60,
                        color_continuous_scale=px.colors.sequential.Reds 
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("篩選後沒有找到 1~3 星的評論。")
                
        else:
            st.error(f"檔案格式不符！請確保包含 'Rating' 與 'Content' 欄位。")
            st.info(f"目前的欄位有：{list(df.columns)}")

    except Exception as e:
        st.error(f"處理檔案時發生錯誤: {e}")
