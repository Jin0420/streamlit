#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

def process_tags(df, tag_column):
    """處理標籤統計"""
    tag_counts = {}
    
    for tags in df[tag_column]:
        if pd.notna(tags):
            tags_list = str(tags).split(',')
            for tag in tags_list:
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    tags_stat = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['次數'])
    tags_stat.index.name = '標籤'
    
    return tags_stat

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

def pagespeed_tool():
    """PageSpeed Insights 工具介面"""
    st.header("PageSpeed Insights 自動查詢工具")
    st.write('這個工具可以幫助你自動查詢多個網址的 PageSpeed Insights 效能指標。')
    
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
    uploaded_file = st.file_uploader("上傳包含網址的 Excel 檔案", type=['xlsx', 'xls'], key="pagespeed_uploader")
    
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
    analyze_button = st.button("開始查詢")
    
    if analyze_button and uploaded_file and api_key:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            
            if len(df.columns) > 1:
                st.warning("請確保工作表只包含一個欄位的 URL 列表")
                return
                
            urls = df[df.columns[0]].dropna().tolist()
            
            st.write(f"共發現 {len(urls)} 個網址")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_placeholder = st.empty()
            
            results = []
            for i, url in enumerate(urls):
                status_text.text(f"正在查詢 {url}")
                result = get_pagespeed_insights(url, api_key)
                if result:
                    results.append(result)
                    
                progress = (i + 1) / len(urls)
                progress_bar.progress(progress)
                
                if results:
                    results_df = pd.DataFrame(results)
                    results_placeholder.dataframe(results_df)
                
                time.sleep(1)
            
            status_text.text("查詢完成！")
            st.session_state.results = results
            st.session_state.analysis_complete = True           
        except Exception as e:
            st.error(f"處理檔案時發生錯誤: {str(e)}")

def tag_statistics_tool():
    """標籤統計工具介面"""
    st.header("標籤次數統計工具")
    
    st.write('這個工具可以幫助你統計標籤出現的次數。')
    st.write('請上傳一個包含標籤欄位的檔案。')
    
    uploaded_file = st.file_uploader("選擇檔案", type=['xlsx', 'xls', 'csv'], key="tags_uploader")
    
    if uploaded_file is not None:
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                encoding_option = st.selectbox('選擇CSV檔案編碼：', 
                                             ['utf-8', 'big5', 'gb18030'], 
                                             help='如果檔案含有中文字且顯示亂碼，請嘗試切換不同編碼')
                df = pd.read_csv(uploaded_file, encoding=encoding_option)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("資料預覽：")
            st.dataframe(df.head())
            
            column_names = df.columns.tolist()
            tag_column = st.selectbox('請選擇包含標籤的欄位：', column_names)
            
            if st.button('開始統計'):
                result_df = process_tags(df, tag_column)
                st.write("統計結果：")
                st.dataframe(result_df)
        except Exception as e:
            st.error(f'處理檔案時發生錯誤：{str(e)}')

def main():   
    # 工具選單
    tool_option = st.sidebar.selectbox(
        "請選擇工具",
        ["PageSpeed Insights 自動查詢", "標籤數量統計"],
        key='tool_selector'
    )
    
    # 根據選擇顯示對應工具
    if tool_option == "PageSpeed Insights 自動查詢":
        pagespeed_tool()
    else:
        tag_statistics_tool()

if __name__ == "__main__":
    main()

