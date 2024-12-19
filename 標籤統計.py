#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
import pandas as pd
import io

def process_tags(df, tag_column):
    # 創建一個 Dict 來統計標籤的出現次數
    tag_counts = {}
    
    for tags in df[tag_column]:
        # 檢查是否有遺漏值
        if pd.notna(tags):
            # 將標籤以逗號分隔成列表
            tags_list = str(tags).split(',')  # 確保轉換成字串
            for tag in tags_list:
                # 去除前後的空白並統計標籤的出現次數
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # 將 Dict 轉 Dataframe
    tags_stat = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['次數'])
    tags_stat.index.name = '標籤'
    
    return tags_stat

# 設置網頁標題
st.title('標籤數量統計器')

# 添加說明
st.write('這個應用程式可以幫助你統計Excel或CSV檔案中各標籤的出現次數。')
st.write('請上傳一個包含標籤欄位的檔案。')

# 檔案上傳器 - 新增 CSV 支援
uploaded_file = st.file_uploader("選擇檔案", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # 根據檔案類型讀取檔案
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            # 新增編碼選項，處理可能的中文編碼問題
            encoding_option = st.selectbox('選擇CSV檔案編碼：', 
                                         ['utf-8', 'big5', 'gb18030'], 
                                         help='如果檔案含有中文字且顯示亂碼，請嘗試切換不同編碼')
            df = pd.read_csv(uploaded_file, encoding=encoding_option)
        else:
            df = pd.read_excel(uploaded_file)
        
        # 顯示檔案內容預覽
        st.write("資料預覽：")
        st.dataframe(df.head())
        st.write("資料筆數：", len(df))
        
        # 讓使用者選擇標籤欄位
        column_names = df.columns.tolist()
        tag_column = st.selectbox('請選擇包含標籤的欄位：', column_names)
        
        if st.button('開始統計'):
            # 處理標籤統計
            result_df = process_tags(df, tag_column)
            
            # 顯示統計結果
            st.write("統計結果：")
            st.dataframe(result_df)

    except Exception as e:
        st.error(f'處理檔案時發生錯誤：{str(e)}')


# In[ ]:




