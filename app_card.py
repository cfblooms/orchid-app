import datetime
import streamlit as st
from utils import (
    WEB_APP_URL,
    get_data,
    append_data,
    delete_data,
    get_next_id,
)

# 頁面設定
st.set_page_config(page_title="A4 賀卡與輓聯產生系統", layout="wide")

st.title("🖨️ A4 賀卡與輓聯自動產生與管理系統")

if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
    st.warning(
        "⚠️ 提醒：請先至 `utils.py` 設定您的 Google Apps Script 雲端網址。"
    )
else:
    # 讀取訂單表以供選擇訂單編號
    df_orders = get_data("訂單表")
    order_ids = (
        df_orders["訂單編號"].astype(str).tolist()
        if not df_orders.empty and "訂單編號" in df_orders.columns
        else []
    )

    tab_create, tab_manage = st.tabs(
        ["📝 1. 製作與新增卡片/輓聯", "📋 2. 現有賀卡與輓聯清單管理"]
    )

    # ---------------------------------------------------------
    # TAB 1: 製作與新增卡片/輓聯
    # ---------------------------------------------------------
    with tab_create:
        st.header("🎨 A4 卡片內容編排與資料庫寫入")

        with st.form("card_create_form"):
            st.subheader("📌 訂單與基本設定")
            col_o1, col_o2, col_o3 = st.columns(3)
            with col_o1:
                card_id = st.text_input(
                    "卡片編號 (自動生成)", value=get_next_id("CARD", "賀卡表")
                )
            with col_o2:
                if order_ids:
                    selected_order_id = st.selectbox(
                        "關聯訂單編號 (一單可有多張卡)", order_ids
                    )
                else:
                    selected_order_id = st.text_input(
                        "訂單編號 (目前無訂單資料可選，請自行輸入)"
                    )
            with col_o3:
                card_type = st.selectbox(
                    "卡片類型", ["喪禮（輓聯）", "慶賀／開幕"]
                )
                orientation = st.selectbox("版面方向", ["直式", "橫式"])

            st.markdown("---")
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                st.subheader("一、上款與對象設定")
                if card_type == "喪禮（輓聯）":
                    mourn_template = st.selectbox(
                        "敬悼格式選擇",
                        [
                            "敬悼 X 媽X夫人 仙逝",
                            "敬悼 X 媽X老夫人 仙逝",
                            "敬悼 X公X先生 千古",
                            "敬悼 X公X老先生 千古",
                            "自訂上款",
                        ],
                    )
                    if mourn_template == "自訂上款":
                        upper_text = st.text_input(
                            "輸入自訂上款", "敬悼 佛弟子林文姬居士蓮前"
                        )
                    else:
                        custom_name = st.text_input(
                            "填入姓氏或全名（取代範本中的 X）", "林"
                        )
                        if "媽X夫人" in mourn_template:
                            upper_text = (
                                f"敬悼 {custom_name} 媽{custom_name}夫人仙逝"
                            )
                        elif "媽X老夫人" in mourn_template:
                            upper_text = f"敬悼 {custom_name} 媽{custom_name}老夫人仙逝"
                        elif "X公X先生" in mourn_template:
                            upper_text = f"敬悼 {custom_name}公{custom_name}先生千古"
                        else:
                            upper_text = f"敬悼 {custom_name}公{custom_name}老先生千古"
                else:
                    upper_text = st.text_input(
                        "上款（祝賀對象）", "恭祝 某某公司開幕誌慶"
                    )

                deliver_location = st.text_input(
                    "配送地點 / 靈堂名稱",
                    value="第一殯儀館明德廳 / 某某商辦大樓",
                )
                recipient_name = st.text_input(
                    "收花人 / 逝者姓名", value="某某某 先生/女士"
                )

            with col_s2:
                st.subheader("二、中款與下款設定")
                if card_type == "喪禮（輓聯）":
                    gender = st.radio("性別", ["女", "男"], horizontal=True)
                    if gender == "女":
                        female_age = st.selectbox(
                            "女性年齡／身份",
                            [
                                "少女、年輕女性（約 49 歲以下 / 未婚）",
                                "中壯年女性（約 50 至 79 歲）",
                                "高齡女性（80 歲以上）",
                                "自訂中款",
                            ],
                        )
                        if "少女" in female_age:
                            middle_options = [
                                "遽促芳齡",
                                "玉殞香消",
                                "芳華早謝",
                                "蘭摧蕙折",
                            ]
                        elif "中壯年" in female_age:
                            middle_options = [
                                "淑德永昭",
                                "懿範長存",
                                "慈容永念",
                                "德業長昭",
                            ]
                        elif "高齡" in female_age:
                            middle_options = [
                                "萱範長存",
                                "母儀千古",
                                "駕返瑤池",
                                "萱蔭長留",
                            ]
                        else:
                            middle_options = []
                    else:
                        male_age = st.selectbox(
                            "男性年齡／身份",
                            [
                                "49歲以下（年輕、早逝）",
                                "50至69歲（壯年至中老年）",
                                "70歲至79歲（古稀）",
                                "80歲以上（高壽、期頤）",
                                "自訂中款",
                            ],
                        )
                        if "49歲以下" in male_age:
                            middle_options = [
                                "星隕少微",
                                "玉樹長埋",
                                "壯志未酬",
                                "天不假年",
                            ]
                        elif "50至69歲" in male_age:
                            middle_options = [
                                "棟折梁摧",
                                "典則空留",
                                "英氣頓杳",
                                "德望昭然",
                            ]
                        elif "70歲至79歲" in male_age:
                            middle_options = [
                                "哲人其萎",
                                "斗柄西移",
                                "德業長昭",
                                "典範長存",
                            ]
                        elif "80歲以上" in male_age:
                            middle_options = [
                                "德高望重",
                                "魯般圮毀",
                                "仁者壽",
                                "德望永昭",
                            ]
                        else:
                            middle_options = []

                    if middle_options:
                        selected_mid = st.selectbox(
                            "選擇常用中款詞語", middle_options + ["自訂輸入"]
                        )
                        middle_text = (
                            st.text_input("輸入自訂中款", "往生極樂")
                            if selected_mid == "自訂輸入"
                            else selected_mid
                        )
                    else:
                        middle_text = st.text_input("輸入自訂中款", "往生極樂")
                else:
                    celeb_options = [
                        "鴻圖大展",
                        "駿業宏開",
                        "生意興隆",
                        "財源廣進",
                        "大業千秋",
                        "自訂輸入",
                    ]
                    selected_celeb = st.selectbox(
                        "選擇慶賀常用詞", celeb_options
                    )
                    middle_text = (
                        st.text_input("輸入自訂慶賀詞", "鴻圖大展")
                        if selected_celeb == "自訂輸入"
                        else selected_celeb
                    )

                company_name = st.text_input(
                    "公司 / 單位名稱（下款用）", "桃園市議員"
                )
                person_name = st.text_input("名字位置", "李宗豪")
                suffix_default = (
                    "敬輓" if card_type == "喪禮（輓聯）" else "敬賀"
                )
                suffix_type = st.selectbox(
                    "結尾敬意", [suffix_default, "敬獻", "自訂"]
                )
                suffix_text = (
                    suffix_type
                    if suffix_type != "自訂"
                    else st.text_input("自訂結尾詞", "敬輓")
                )

            # 組合下款
            if company_name and person_name:
                lower_text = f"{company_name}<br>{person_name} {suffix_text}"
            elif company_name:
                lower_text = f"{company_name} {suffix_text}"
            elif person_name:
                lower_text = f"{person_name} {suffix_text}"
            else:
                lower_text = suffix_text

            submitted_save = st.form_submit_button(
                "💾 儲存卡片至雲端並產生 A4 預覽"
            )

            if submitted_save:
                # 依據賀卡表欄位格式寫入：
                # 欄位：卡片編號 | 訂單編號 | 卡片類型 | 收花人/靈堂 | 中款/賀詞 | 祝賀文字 | 送花人署名 | 配送地點 | 列印狀態
                row_card = [
                    card_id,
                    selected_order_id,
                    card_type,
                    recipient_name,
                    middle_text,
                    upper_text,
                    f"{company_name} {person_name} {suffix_text}",
                    deliver_location,
                    "未列印",
                ]
                if append_data("賀卡表", row_card):
                    st.success(
                        f"成功將卡片編號 {card_id} 儲存至雲端賀卡表（訂單編號：{selected_order_id}）！"
                    )
                else:
                    st.error(
                        "儲存失敗，請檢查網路或 Google Apps Script 部署狀態。"
                    )

        # --- A4 即時排版預覽畫面 ---
        st.markdown("---")
        st.subheader("📄 A4 即時排版預覽")

        if orientation == "直式":
            container_style = """
                width: 100%;
                max-width: 600px;
                aspect-ratio: 1 / 1.414;
                background: white;
                color: black;
                border: 1px solid #ccc;
                padding: 50px 40px;
                margin: 0 auto;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                font-family: 'DFKai-SB', 'BiauKai', 'STKaiti', serif;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            """
            layout_html = f"""
            <div style="{container_style}">
                <!-- 左側：下款 -->
                <div style="writing-mode: vertical-rl; font-size: 20px; letter-spacing: 2px; align-self: flex-end;">
                    {lower_text}
                </div>
                <!-- 中間：中款大字 -->
                <div style="writing-mode: vertical-rl; font-size: 44px; font-weight: bold; letter-spacing: 6px; align-self: center;">
                    {middle_text}
                </div>
                <!-- 右側：上款 -->
                <div style="writing-mode: vertical-rl; font-size: 22px; letter-spacing: 2px; align-self: flex-start;">
                    {upper_text}
                </div>
            </div>
            """
        else:
            container_style = """
                width: 100%;
                max-width: 800px;
                aspect-ratio: 1.414 / 1;
                background: white;
                color: black;
                border: 1px solid #ccc;
                padding: 40px;
                margin: 0 auto;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                font-family: 'DFKai-SB', 'BiauKai', 'STKaiti', serif;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            """
            layout_html = f"""
            <div style="{container_style}">
                <div style="display: flex; justify-content: space-between; font-size: 20px;">
                    <div></div>
                    <div>{upper_text}</div>
                </div>
                <div style="text-align: center; font-size: 50px; font-weight: bold; letter-spacing: 8px; margin: auto 0;">
                    {middle_text}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: flex-end; font-size: 20px;">
                    <div>{company_name}</div>
                    <div>{person_name} {suffix_text}</div>
                </div>
            </div>
            """

        st.markdown(layout_html, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 2: 現有賀卡與輓聯清單管理
    # ---------------------------------------------------------
    with tab_manage:
        st.header("📋 雲端賀卡與輓聯總覽")
        df_cards = get_data("賀卡表")

        if not df_cards.empty:
            st.dataframe(df_cards, use_container_width=True)

            card_ids_list = (
                df_cards["卡片編號"].astype(str).tolist()
                if "卡片編號" in df_cards.columns
                else []
            )
            if card_ids_list:
                selected_del_card = st.selectbox(
                    "選擇要刪除的卡片編號", card_ids_list
                )
                if st.button("🗑️ 刪除此張卡片紀錄"):
                    if delete_data("賀卡表", selected_del_card):
                        st.success(f"已成功刪除卡片編號：{selected_del_card}")
                        st.rerun()
        else:
            st.info(
                "目前雲端賀卡表中尚無資料，請至第一頁新增卡片或檢查 Google 試算表連線。"
            )