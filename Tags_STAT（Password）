#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
import pandas as pd
import io
import hashlib

# 設定密碼（這裡使用雜湊值以增加安全性）
CORRECT_PASSWORD_HASH = "70eded5c719db84ae23a66c1dde35dff5836eabf"  # password123 的 SHA-1 雜湊值

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """檢查輸入的密碼是否正確"""
        input_password = st.session_state["password"]
        if hashlib.sha1(input_password.encode()).hexdigest() == CORRECT_PASSWORD_HASH:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 清除密碼
        else:
            st.session_state["password_correct"] = False

    # 首次訪問或密碼錯誤時顯示輸入表單
    if "password_correct" not in st.session_state:
        st.text_input(
            "請輸入密碼", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # 密碼錯誤時顯示錯誤訊息
    elif not st.session_state["password_correct"]:
        st.text_input(
            "請輸入密碼", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("密碼錯誤，請重試")
        return False
    
    return True

def process_tags(df, tag_column):
    # 創建一個 Dict 來統計標籤的出現次數
    tag_counts = {}
    
    for tags in df[tag_column]:
        # 檢查是否有遺漏值
        if pd.notna(tags):
            # 將標籤以逗號分隔成列表
            tags_list = str(tags).split(',')
            for tag in tags_list:
                # 去除前後的空白並統計標籤的出現次數
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # 將 Dict 轉 Dataframe
    tags_stat = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['次數'])
    tags_stat.index.name = '標籤'
    
    return tags_stat

# 主程式開始
st.title('標籤次數統計器')

# 檢查密碼
if check_password():
    # 添加說明
    st.write('這個應用程式可以幫助你統計Excel或CSV檔案中的標籤出現次數。')
    st.write('請上傳一個包含標籤欄位的檔案。')

    # 檔案上傳器
    uploaded_file = st.file_uploader("選擇檔案", type=['xlsx', 'xls', 'csv'])

    if uploaded_file is not None:
        try:
            # 根據檔案類型讀取檔案
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                encoding_option = st.selectbox('選擇CSV檔案編碼：', 
                                             ['utf-8', 'big5', 'gb18030'], 
                                             help='如果檔案含有中文字且顯示亂碼，請嘗試切換不同編碼')
                df = pd.read_csv(uploaded_file, encoding=encoding_option)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 顯示檔案內容預覽
            st.write("資料預覽：")
            st.dataframe(df.head())
            
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
