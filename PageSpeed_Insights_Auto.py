#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import requests
import time

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

    # 初始化 session state
    if 'results' not in st.session_state:
        st.session_state.results = None

    # API Key 輸入
    api_key = st.text_input(
        "請輸入 Google PageSpeed Insights API Key", 
        type="password", 
        help="如果沒有 API Key，請前往 https://developers.google.com/speed/docs/insights/v5/get-started?hl=zh-tw 取得"
    )

    # 檔案上傳
    uploaded_file = st.file_uploader("上傳包含網址的 Excel 檔案", type=['xlsx', 'xls'])
    if uploaded_file:
        try:
            # 讀取 Excel 檔案
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            selected_sheet = st.selectbox("請選擇要分析的工作表", sheet_names)
            preview_df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            st.write("工作表預覽：")
            st.dataframe(preview_df.head())
        except Exception as e:
            st.error(f"讀取 Excel 檔案時發生錯誤: {e}")
            return

    # 分析按鈕
    analyze_button = st.button("開始分析")
    if analyze_button and api_key and uploaded_file:
        try:
            # 分析選擇的工作表
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            urls = df[df.columns[0]].dropna().tolist()
            st.write(f"共發現 {len(urls)} 個網址")
            progress_bar = st.progress(0)
            results = []

            for i, url in enumerate(urls):
                result = get_pagespeed_insights(url, api_key)
                if result:
                    results.append(result)
                progress_bar.progress((i + 1) / len(urls))
                time.sleep(1)

            # 顯示結果
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)
        except Exception as e:
            st.error(f"分析過程中出現錯誤: {e}")

if __name__ == "__main__":
    main()

