#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

# 允許的 Streamlit 帳號列表
ALLOWED_EMAILS = [
    'jin6622345@yahoo.com.tw',
    'jin420317@gmail.com'
]

def check_streamlit_user():
    """檢查目前登入的 Streamlit 帳號是否有權限"""
    # 檢查是否登入
    if not st.session_state.get('user'):
        try:
            user = st.experimental_user
            if user is not None and user.email:
                st.session_state['user'] = user
            else:
                st.error("請先登入 Streamlit 帳號")
                st.write("請點擊右上角的登入按鈕進行登入")
                st.stop()
        except:
            st.error("無法驗證用戶身份")
            st.write("請確保你已登入 Streamlit 帳號")
            st.stop()
    
    # 檢查是否在允許清單中
    if st.session_state['user'].email not in ALLOWED_EMAILS:
        st.error("抱歉，你的帳號沒有使用此應用程式的權限")
        st.write("如需使用權限，請聯繫管理員")
        st.stop()
    
    return True
    
def get_pagespeed_insights(url, api_key):
    """獲取 PageSpeed Insights 數據"""
    api_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    params = {
        'url': url,
        'key': api_key,
        'strategy': 'mobile',
        'category': ['accessibility', 'best-practices', 'performance', 'seo']
    }
    
    try:
        response = requests.get(api_url, params=params)
        result = response.json()
        
        return {
            'url': url,
            'performance': result['lighthouseResult']['categories']['performance']['score'] * 100,
            'accessibility': result['lighthouseResult']['categories']['accessibility']['score'] * 100,
            'best_practices': result['lighthouseResult']['categories']['best-practices']['score'] * 100,
            'seo': result['lighthouseResult']['categories']['seo']['score'] * 100
        }
    except Exception as e:
        st.error(f"分析 {url} 時發生錯誤: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="PageSpeed Insights 自動查詢工具", layout="wide")
    
    st.title("PageSpeed Insights 自動查詢工具")
    
def main():
    st.set_page_config(page_title="PageSpeed Insights 分析工具", layout="wide")
    
    # 檢查用戶權限
    check_streamlit_user()
    
    # 顯示歡迎訊息
    st.write(f"### 歡迎，{st.experimental_user.email}")
    
    # 原有的 PageSpeed Insights 分析功能
    st.title("PageSpeed Insights 分析工具")
    
    # 初始化 session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'sheet_names' not in st.session_state:
        st.session_state.sheet_names = None
    
    # API Key 輸入
    api_key = st.text_input("請輸入 Google PageSpeed Insights API Key", 
                           type="password",
                           help="如果沒有 API Key，請前往 https://developers.google.com/speed/docs/insights/v5/get-started?hl=zh-tw 取得")
    
    # 檔案上傳
    uploaded_file = st.file_uploader("上傳包含網址的 Excel 檔案", type=['xlsx', 'xls'])
    
    # 如果有上傳檔案，讀取工作表名稱
    if uploaded_file:
        try:
            # 讀取所有工作表名稱
            excel_file = pd.ExcelFile(uploaded_file)
            st.session_state.sheet_names = excel_file.sheet_names
            
            # 讓用戶選擇工作表
            selected_sheet = st.selectbox(
                "請選擇要分析的工作表",
                st.session_state.sheet_names
            )
            
            # 預覽選擇的工作表內容
            preview_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            st.write("工作表預覽：")
            st.dataframe(preview_df.head())
            
        except Exception as e:
            st.error(f"讀取 Excel 檔案時發生錯誤: {str(e)}")
            return
    
    # 分析按鈕
    analyze_button = st.button("開始分析")
    
    if analyze_button and uploaded_file and api_key:
        try:
            # 讀取選擇的工作表
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            
            # 確保數據是單一欄位的 URL 列表
            if len(df.columns) > 1:
                st.warning("請確保工作表只包含一個欄位的 URL 列表")
                return
                
            urls = df[df.columns[0]].dropna().tolist()
            
            st.write(f"共發現 {len(urls)} 個網址")
            
            # 創建進度條
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_placeholder = st.empty()
            
            results = []
            for i, url in enumerate(urls):
                status_text.text(f"正在分析 {url}")
                result = get_pagespeed_insights(url, api_key)
                if result:
                    results.append(result)
                    
                # 更新進度
                progress = (i + 1) / len(urls)
                progress_bar.progress(progress)
                
                # 即時顯示結果
                if results:
                    results_df = pd.DataFrame(results)
                    results_placeholder.dataframe(results_df)
                
                # 避免 API 請求過於頻繁
                time.sleep(1)
            
            status_text.text("分析完成！")
            
            # 儲存結果到 session state
            st.session_state.results = results
            st.session_state.analysis_complete = True
            
        except Exception as e:
            st.error(f"處理檔案時發生錯誤: {str(e)}")
    
    # 如果分析完成，顯示結果和下載按鈕
    if st.session_state.analysis_complete and st.session_state.results:
        results_df = pd.DataFrame(st.session_state.results)
        
        # 顯示結果表格
        st.dataframe(results_df)
        
        # 下載按鈕
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="下載 CSV 檔案",
            data=csv,
            file_name=f"pagespeed_results_{selected_sheet}.csv",
            mime="text/csv"
        )

    # 重置按鈕
    if st.session_state.analysis_complete:
        if st.button("重新開始"):
            st.session_state.results = None
            st.session_state.analysis_complete = False
            st.session_state.sheet_names = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()

