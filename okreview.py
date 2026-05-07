import streamlit as st
import pandas as pd
import re
from collections import Counter
import plotly.express as px
import io

# ================= 頁面配置 (資安與 UI) =================
# 建議配合 .streamlit/config.toml 使用以達到最佳資安效果
st.set_page_config(
    page_title="負評相關熱點分布",
    page_icon="🎯",
    layout="wide"
)

# 透過左右留白，提升視覺精緻度並降低滿版壓迫感
spacer_left, main_col, spacer_right = st.columns([1, 10, 1])

with main_col:
    st.title("🎯 評論相關熱點分布分析系統")
    st.info("本系統已啟用資安防護機制，包含原始碼漏洞掃描與 XSRF 保護。")
    st.markdown("---")

    # 1. 建立電商專用停用詞黑名單 (持續優化中)
    # 增加更多無意義的電商常見詞，讓熱點更精準
    STOP_WORDS = {
        'the', 'and', 'to', 'a', 'of', 'it', 'in', 'is', 'i', 'that', 'for', 'this', 
        'with', 'my', 'was', 'on', 'not', 'but', 'as', 'have', 'are', 'be', 'so', 
        'they', 'you', 'just', 'like', 'very', 'all', 'would', 'out', 'if', 'about',
        'or', 'me', 'from', 'can', 'has', 'had', 'up', 'do', 'than', 'because', 'when',
        'what', 'which', 'your', 'were', 'there', 'their', 'an', 'we', 'at', 'them',
        'product', 'item', 'amazon', 'bought', 'buy', 'purchased', 'get', 'got', 
        'one', 'really', 'even', 'much', 'good', 'bad', 'don', 'didn', 'doesn',
        'use', 'used', 'using', 'time', 'work', 'worked', 'money', 'back', 'return',
        'review', 'reviews', 'tried', 'try', 'way', 'make', 'made', 'did', 'well',
        'seller', 'service', 'package', 'shipping', 'received', 'delivery'
    }

    # 2. 核心統計函式 (具備資料清洗邏輯)
    def get_word_freq(df, stop_words):
        if df.empty:
            return pd.DataFrame(columns=['熱點關鍵字', '出現頻次'])
        
        # 僅提取 Content 欄位，排除空值並確保為字串
        all_content = df['Content'].dropna().astype(str).tolist()
        
        # 合併後統一轉小寫，並使用正則表達式過濾非字母字元
        # 僅保留長度為 3 以上的單字
        all_text = " ".join(all_content).lower()
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        
        # 過濾黑名單詞彙
        meaningful_words = [word for word in words if word not in stop_words]
        
        # 統計前 20 大熱門詞彙
        word_counts = Counter(meaningful_words).most_common(20)
        return pd.DataFrame(word_counts, columns=['熱點關鍵字', '出現頻次'])

    # 3. 檔案上傳區 (支援多種格式)
    uploaded_file = st.file_uploader("📥 請上傳 Review 報表 (支援 CSV, XLSX, XLS)", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            # 檔案讀取邏輯
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                # 處理 Excel 多分頁：自動尋找關鍵分頁
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                # 優先抓取名稱包含 'Review' 的分頁，若無則抓取第一頁
                target_sheet = next((s for s in sheet_names if 'Review' in s), sheet_names[0])
                df = pd.read_excel(uploaded_file, sheet_name=target_sheet)

            # 檢查必要欄位 (Rating, Content)
            if 'Rating' in df.columns and 'Content' in df.columns:
                
                # 數據分層
                df_all = df
                df_positive = df[df['Rating'] >= 4]
                df_negative = df[df['Rating'] <= 3]

                # 建立 UI 分頁標籤
                tab1, tab2, tab3 = st.tabs(["📊 全域熱點分布", "🟢 好評核心亮點", "🔴 負評痛點分布"])

                # --- Tab 1: 全域熱點 ---
                with tab1:
                    st.subheader("整體評論關鍵字排行")
                    df_freq_all = get_word_freq(df_all, STOP_WORDS)
                    if not df_freq_all.empty:
                        fig = px.bar(
                            df_freq_all, 
                            x='熱點關鍵字', 
                            y='出現頻次', 
                            color='出現頻次', 
                            color_continuous_scale='Blues',
                            template='plotly_white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("數據量不足，無法生成分布圖。")

                # --- Tab 2: 好評熱點 ---
                with tab2:
                    st.subheader("買家滿意度核心 (4-5星)")
                    df_freq_pos = get_word_freq(df_positive, STOP_WORDS)
                    if not df_freq_pos.empty:
                        # 使用泡泡圖呈現
                        fig = px.scatter(
                            df_freq_pos, 
                            x="熱點關鍵字", 
                            y="出現頻次", 
                            size="出現頻次", 
                            color="出現頻次", 
                            color_continuous_scale='Greens', 
                            size_max=60
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("目前尚無符合條件的好評數據。")

                # --- Tab 3: 負評熱點 ---
                with tab3:
                    st.subheader("產品待優化熱點 (1-3星)")
                    df_freq_neg = get_word_freq(df_negative, STOP_WORDS)
                    if not df_freq_neg.empty:
                        # 使用熱力感泡泡圖呈現
                        fig = px.scatter(
                            df_freq_neg, 
                            x="熱點關鍵字", 
                            y="出現頻次", 
                            size="出現頻次", 
                            color="出現頻次", 
                            color_continuous_scale='Reds', 
                            size_max=60
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("恭喜！目前尚無明顯的負評熱點。")
            
            else:
                st.error("⚠️ 檔案格式錯誤：找不到 'Rating' 或 'Content' 欄位。")
                st.write("目前偵測到的欄位有：", list(df.columns))

        except Exception as e:
            # 資安考量：僅顯示通用錯誤，不洩漏詳細 Traceback
            st.error(f"檔案解析失敗。請確保檔案內容格式正確且未受密碼保護。")
            # 開發偵錯用 (可選): st.write(str(e))
