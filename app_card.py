import datetime
import streamlit as st
import streamlit.components.v1 as components
from utils import (
    WEB_APP_URL,
    get_data,
    append_data,
    delete_data,
    get_next_id,
)

# 頁面設定
st.set_page_config(page_title="A4 賀卡與輓聯產生系統", layout="wide")

st.title("🖨️ A4 賀卡與輓聯自動產生與排版管理系統")

# 初始化 Session State 以記錄各個元件的位置與字體大小
for key, default_val in [
    ("top_x", 150), ("top_y", 40), ("font_top", 22),
    ("mid_x", 180), ("mid_y", 200), ("font_mid", 48),
    ("comp_x", 60), ("comp_y", 800), ("font_comp", 20),
    ("name_x", 250), ("name_y", 850), ("font_name", 20),
    ("suff_x", 500), ("suff_y", 850), ("font_suff", 20),
]:
    if key not in st.session_state:
        st.session_state[key] = default_val

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
                    "卡片類型", ["喪禮（輓聯）", "慶賀-開幕", "慶賀-搬家", "慶賀-宮廟"]
                )

            col_o4, col_o5 = st.columns(2)
            with col_o4:
                recipient_name = st.text_input(
                    "收花人", value="王小明先生 / 某某公司"
                )
            with col_o5:
                orientation = st.selectbox(
                    "版面方向", ["直式 (傳統直排)", "橫式 (現代橫排)"]
                )

            st.markdown("---")
            col_s1, col_s2 = st.columns(2)

            with col_s1:
                st.subheader("一、上款與對象設定")
                if card_type == "喪禮（輓聯）":
                    mourn_template = st.selectbox(
                        "格式選擇",
                        [
                            "X 媽X老夫人",
                            "X 媽X夫人",
                            "X公X老先生",
                            "X公X先生",
                            "X女士",
                            "X先生",
                            "自訂上款",
                        ],
                    )
                    if mourn_template == "自訂上款":
                        upper_text = st.text_input(
                            "輸入自訂上款", "佛弟子林文姬居士蓮前"
                        )
                    else:
                        custom_name = st.text_input(
                            "填入姓氏或全名（取代範本中的 X）", "林"
                        )
                        if mourn_template == "X 媽X老夫人":
                            base_title = f"{custom_name} 媽{custom_name}老夫人"
                        elif mourn_template == "X 媽X夫人":
                            base_title = f"{custom_name} 媽{custom_name}夫人"
                        elif mourn_template == "X公X老先生":
                            base_title = f"{custom_name}公{custom_name}老先生"
                        elif mourn_template == "X公X先生":
                            base_title = f"{custom_name}公{custom_name}先生"
                        elif mourn_template == "X女士":
                            base_title = f"{custom_name}女士"
                        else:
                            base_title = f"{custom_name}先生"

                        ending_choice = st.selectbox(
                            "上款結尾敬語",
                            ["仙逝", "千古", "靈前", "冥前", "便覽", "淑靈", "蓮前", "自訂"]
                        )
                        ending_text = (
                            ending_choice
                            if ending_choice != "自訂"
                            else st.text_input("輸入自訂結尾詞", "仙逝")
                        )
                        upper_text = f"{base_title} {ending_text}"
                else:
                    # 慶賀類（開幕、搬家、宮廟）
                    upper_prefix = st.selectbox("上款格式選擇", ["恭祝", "恭賀"])
                    default_target = "某某公司開幕誌慶" if "開幕" in card_type else ("某某府喬遷之喜" if "搬家" in card_type else "某某宮神威顯赫")
                    upper_target = st.text_input("上款主旨內容", default_target)
                    upper_text = f"{upper_prefix} {upper_target}"

                deliver_location = st.text_input(
                    "配送地點",
                    value="第一殯儀館明德廳 / 某某商辦大樓",
                )

            with col_s2:
                st.subheader("二、中款設定")
                if card_type == "喪禮（輓聯）":
                    gender = st.radio("性別選擇", ["女", "男"], horizontal=True)
                    if gender == "女":
                        age_group = st.selectbox(
                            "年齡層選擇",
                            [
                                "49歲以下（年輕、未婚或一般年輕女性，稱女士）",
                                "50至79歲（稱夫人／女士）",
                                "80歲以上（稱老夫人）",
                                "自訂中款",
                            ],
                        )
                        if "49歲以下" in age_group:
                            middle_options = ["芳華早謝", "遽促芳齡", "妝台月冷", "香消玉殞", "音容宛在"]
                        elif "50至79歲" in age_group:
                            middle_options = ["懿範長存", "淑德永昭", "萱萎北堂", "慈雲縹緲"]
                        elif "80歲以上" in age_group:
                            middle_options = ["母儀千古", "駕返瑤池", "慈輝永昭", "寶婺星沉"]
                        else:
                            middle_options = []
                    else:
                        age_group = st.selectbox(
                            "年齡層選擇",
                            [
                                "49 歲以下（稱「先生」）",
                                "50 至 69 歲（稱「先生」）",
                                "70 至 79 歲（稱「老先生」）",
                                "80 歲以上（稱「老先生」）",
                                "自訂中款",
                            ],
                        )
                        if "49 歲以下" in age_group:
                            middle_options = ["星隕少微", "壯志未酬", "天不假年", "英年仙去", "音容宛在"]
                        elif "50 至 69 歲" in age_group:
                            middle_options = ["長才未盡", "棟折梁摧", "典則空留", "悵望音容", "英氣頓杳"]
                        elif "70 至 79 歲" in age_group:
                            middle_options = ["駕鶴西歸", "道範長存", "碩德堪欽", "儀型足式", "高風亮節"]
                        elif "80 歲以上" in age_group:
                            middle_options = ["福壽全歸", "高山仰止", "碩德貽徽", "德望永昭", "典範長存"]
                        else:
                            middle_options = []

                    if middle_options:
                        selected_mid = st.selectbox(
                            "自動對應常用中款詞語", middle_options + ["自訂輸入"]
                        )
                        middle_text = (
                            st.text_input("輸入自訂中款", "往生極樂")
                            if selected_mid == "自訂輸入"
                            else selected_mid
                        )
                    else:
                        middle_text = st.text_input("輸入自訂中款", "往生極樂")
                else:
                    # 慶賀類（無需選擇身份）
                    if card_type == "慶賀-開幕":
                        celeb_options = [
                            "開幕誌慶",
                            "開張大吉",
                            "鴻圖大展",
                            "駿業宏開",
                            "生意興隆",
                            "財源廣進",
                            "客似雲來",
                        ]
                    elif card_type == "慶賀-搬家":
                        celeb_options = [
                            "喬遷之喜",
                            "里仁為美",
                            "金玉滿堂",
                        ]
                    elif card_type == "慶賀-宮廟":
                        celeb_options = [
                            "聖誕千秋・神威顯赫",
                        ]
                    else:
                        celeb_options = ["鴻圖大展"]

                    selected_celeb = st.selectbox(
                        "選擇常用中款詞語", celeb_options + ["自行輸入"]
                    )
                    middle_text = (
                        st.text_input("輸入自訂中款", celeb_options[0] if celeb_options else "鴻圖大展")
                        if selected_celeb == "自行輸入"
                        else selected_celeb
                    )

            st.markdown("---")
            st.subheader("三、下款設定（提供 5 個獨立名字格子）")
            company_name = st.text_input(
                "公司 / 單位名稱（下款用）", "桃園市議員"
            )
            
            st.markdown("請填寫送花人名字（最多 5 位）：")
            col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns(5)
            with col_n1: name1 = st.text_input("名字 1", "李宗豪")
            with col_n2: name2 = st.text_input("名字 2", "")
            with col_n3: name3 = st.text_input("名字 3", "")
            with col_n4: name4 = st.text_input("名字 4", "")
            with col_n5: name5 = st.text_input("名字 5", "")

            suffix_default = (
                "敬輓" if card_type == "喪禮（輓聯）" else "敬賀"
            )
            suffix_type = st.selectbox(
                "結尾敬意（敬輓 / 敬悼等）", [suffix_default, "敬獻", "自訂"]
            )
            suffix_text = (
                suffix_type
                if suffix_type != "自訂"
                else st.text_input("自訂結尾詞", "敬輓")
            )

            # 組合 5 個下款名字
            names = [n.strip() for n in [name1, name2, name3, name4, name5] if n.strip()]
            names_combined = " ".join(names)

            # 組合完整下款供資料庫記錄
            lower_text_db = f"{company_name}<br>{names_combined} {suffix_text}" if company_name else f"{names_combined} {suffix_text}"

            submitted_save = st.form_submit_button(
                "💾 儲存卡片至雲端並產生 A4 預覽"
            )

            if submitted_save:
                row_card = [
                    card_id,
                    selected_order_id,
                    card_type,
                    recipient_name,
                    middle_text,
                    upper_text,
                    lower_text_db,
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

        # --- 側邊欄：各元件水平(X)、垂直(Y)與字體大小微調控制 ---
        st.sidebar.markdown("---")
        st.sidebar.header("🎚️ 雙向排版與字體微調控制 (X, Y 軸)")
        
        with st.sidebar.expander("📌 上款位置與字體"):
            st.session_state.font_top = st.slider("上款字體大小", 12, 50, st.session_state.font_top, key="f_top")
            st.session_state.top_x = st.slider("上款水平位置 (X)", 0, 800, st.session_state.top_x, key="x_top")
            st.session_state.top_y = st.slider("上款垂直位置 (Y)", 0, 900, st.session_state.top_y, key="y_top")

        with st.sidebar.expander("📌 中款位置與字體"):
            st.session_state.font_mid = st.slider("中款字體大小", 20, 150, st.session_state.font_mid, key="f_mid")
            st.session_state.mid_x = st.slider("中款水平位置 (X)", 0, 800, st.session_state.mid_x, key="x_mid")
            st.session_state.mid_y = st.slider("中_款垂直位置 (Y)", 0, 900, st.session_state.mid_y, key="y_mid")

        with st.sidebar.expander("📌 下款單位 (公司) 位置與字體"):
            st.session_state.font_comp = st.slider("單位字體大小", 12, 40, st.session_state.font_comp, key="f_comp")
            st.session_state.comp_x = st.slider("單位水平位置 (X)", 0, 800, st.session_state.comp_x, key="x_comp")
            st.session_state.comp_y = st.slider("單位垂直位置 (Y)", 0, 900, st.session_state.comp_y, key="y_comp")

        with st.sidebar.expander("📌 下款名字 (5人) 位置與字體"):
            st.session_state.font_name = st.slider("名字字體大小", 12, 40, st.session_state.font_name, key="f_name")
            st.session_state.name_x = st.slider("名字水平位置 (X)", 0, 800, st.session_state.name_x, key="x_name")
            st.session_state.name_y = st.slider("名字垂直位置 (Y)", 0, 900, st.session_state.name_y, key="y_name")

        with st.sidebar.expander("📌 敬輓 / 敬賀 位置與字體"):
            st.session_state.font_suff = st.slider("敬意字體大小", 12, 40, st.session_state.font_suff, key="f_suff")
            st.session_state.suff_x = st.slider("敬意水平位置 (X)", 0, 800, st.session_state.suff_x, key="x_suff")
            st.session_state.suff_y = st.slider("敬意垂直位置 (Y)", 0, 900, st.session_state.suff_y, key="y_suff")

        # --- A4 即時排版預覽畫面 (自動適應直式 / 橫式格式) ---
        st.markdown("---")
        st.subheader("📄 A4 即時排版預覽")

        if "直式" in orientation:
            # 傳統直排版樣式（對應圖一）
            container_style = """
                width: 100%;
                max-width: 650px;
                height: 920px;
                background: white;
                color: black;
                border: 2px solid #333;
                position: relative;
                margin: 0 auto;
                font-family: 'DFKai-SB', 'BiauKai', 'STKaiti', serif;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            """
            layout_html = f"""
            <div style="{container_style}">
                <!-- 上款 (直排) -->
                <div style="position: absolute; top: {st.session_state.top_y}px; left: {st.session_state.top_x}px; font-size: {st.session_state.font_top}px; writing-mode: vertical-rl; text-orientation: upright; font-weight: bold; letter-spacing: 4px;">
                    {upper_text}
                </div>
                
                <!-- 中款 (直排大字) -->
                <div style="position: absolute; top: {st.session_state.mid_y}px; left: {st.session_state.mid_x}px; font-size: {st.session_state.font_mid}px; writing-mode: vertical-rl; text-orientation: upright; font-weight: bold; letter-spacing: 12px;">
                    {middle_text}
                </div>
                
                <!-- 下款單位 (直排) -->
                <div style="position: absolute; top: {st.session_state.comp_y}px; left: {st.session_state.comp_x}px; font-size: {st.session_state.font_comp}px; writing-mode: vertical-rl; text-orientation: upright; font-weight: bold; letter-spacing: 4px;">
                    {company_name}
                </div>

                <!-- 下款名字 (5人，直排) -->
                <div style="position: absolute; top: {st.session_state.name_y}px; left: {st.session_state.name_x}px; font-size: {st.session_state.font_name}px; writing-mode: vertical-rl; text-orientation: upright; font-weight: bold; letter-spacing: 4px;">
                    {names_combined}
                </div>

                <!-- 敬輓 / 敬賀 (直排) -->
                <div style="position: absolute; top: {st.session_state.suff_y}px; left: {st.session_state.suff_x}px; font-size: {st.session_state.font_suff}px; writing-mode: vertical-rl; text-orientation: upright; font-weight: bold; letter-spacing: 4px;">
                    {suffix_text}
                </div>
            </div>
            """
        else:
            # 現代橫排版樣式（對應圖二）
            container_style = """
                width: 100%;
                max-width: 850px;
                height: 600px;
                background: white;
                color: black;
                border: 2px solid #333;
                position: relative;
                margin: 0 auto;
                font-family: 'DFKai-SB', 'BiauKai', 'STKaiti', serif;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
                overflow: hidden;
            """
            layout_html = f"""
            <div style="{container_style}">
                <!-- 上款 -->
                <div style="position: absolute; top: {st.session_state.top_y}px; left: {st.session_state.top_x}px; font-size: {st.session_state.font_top}px; white-space: nowrap; font-weight: bold;">
                    {upper_text}
                </div>
                
                <!-- 中款 -->
                <div style="position: absolute; top: {st.session_state.mid_y}px; left: {st.session_state.mid_x}px; font-size: {st.session_state.font_mid}px; white-space: nowrap; font-weight: bold; letter-spacing: 8px;">
                    {middle_text}
                </div>
                
                <!-- 下款單位 -->
                <div style="position: absolute; top: {st.session_state.comp_y}px; left: {st.session_state.comp_x}px; font-size: {st.session_state.font_comp}px; white-space: nowrap; font-weight: bold;">
                    {company_name}
                </div>

                <!-- 下款名字 (5人) -->
                <div style="position: absolute; top: {st.session_state.name_y}px; left: {st.session_state.name_x}px; font-size: {st.session_state.font_name}px; white-space: nowrap; font-weight: bold;">
                    {names_combined}
                </div>

                <!-- 敬輓 / 敬賀 -->
                <div style="position: absolute; top: {st.session_state.suff_y}px; left: {st.session_state.suff_x}px; font-size: {st.session_state.font_suff}px; white-space: nowrap; font-weight: bold;">
                    {suffix_text}
                </div>
            </div>
            """

        # 透過 st.components.v1.html 渲染預覽
        components.html(layout_html, height=950, scrolling=False)

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
