import streamlit as st

# 頁面設定
st.set_page_config(page_title="賀卡與輓聯產生器", layout="wide")

st.title("🖨️ 賀卡與輓聯自動產生器 (A4 格式)")

# --- 側邊欄：資料設定 ---
st.sidebar.header("📝 內容設定")

# 1. 類別選擇
card_type = st.sidebar.radio("選擇卡片類型", ["喪禮（輓聯）", "慶賀／開幕"])

# 2. 版面方向
orientation = st.sidebar.radio("版面方向", ["直式", "橫式"])

# --- 上款設定 ---
st.sidebar.subheader("一、上款設定")
if card_type == "喪禮（輓聯）":
    mourn_template = st.sidebar.selectbox("敬悼格式選擇", [
        "敬悼 X 媽X夫人 仙逝",
        "敬悼 X 媽X老夫人 仙逝",
        "敬悼 X公X先生 千古",
        "敬悼 X公X老先生 千古",
        "自訂上款"
    ])
    if mourn_template == "自訂上款":
        upper_text = st.sidebar.text_input("輸入自訂上款", "敬悼 佛弟子林文姬居士蓮前")
    else:
        # 讓使用者可以替換其中的 X
        custom_name = st.sidebar.text_input("填入姓氏或全名（取代範本中的 X）", "林")
        if "媽X夫人" in mourn_template:
            upper_text = f"敬悼 {custom_name} 媽{custom_name}夫人 仙逝"
        elif "媽X老夫人" in mourn_template:
            upper_text = f"敬悼 {custom_name} 媽{custom_name}老夫人 仙逝"
        elif "X公X先生" in mourn_template:
            upper_text = f"敬悼 {custom_name}公{custom_name}先生 千古"
        else:
            upper_text = f"敬悼 {custom_name}公{custom_name}老先生 千古"
else:
    upper_text = st.sidebar.text_input("上款（祝賀對象）", "恭祝 XXXX")

# --- 中款設定 ---
st.sidebar.subheader("二、中款（主旨詞）設定")
if card_type == "喪禮（輓聯）":
    gender = st.sidebar.radio("性別", ["女", "男"])
    
    if gender == "女":
        female_age = st.sidebar.selectbox("女性年齡／身份", [
            "少女、年輕女性（約 49 歲以下 / 未婚）",
            "中壯年女性（約 50 至 79 歲）",
            "高齡女性（80 歲以上）",
            "自訂中款"
        ])
        if "少女" in female_age:
            middle_options = ["遽促芳齡", "玉殞香消", "芳華早謝", "蘭摧蕙折", "妝台月冷"]
        elif "中壯年" in female_age:
            middle_options = ["淑德永昭", "懿範長存", "慈容永念", "德業長昭", "巾幗模範"]
        elif "高齡" in female_age:
            middle_options = ["萱範長存", "母儀千古", "駕返瑤池", "萱蔭長留", "壺範垂型"]
        else:
            middle_options = []
            
    else:  # 男
        male_age = st.sidebar.selectbox("男性年齡／身份", [
            "49歲以下（年輕、早逝）",
            "50至69歲（壯年至中老年）",
            "70歲至79歲（古稀）",
            "80歲以上（高壽、期頤）",
            "自訂中款"
        ])
        if "49歲以下" in male_age:
            middle_options = ["星隕少微", "玉樹長埋", "壯志未酬", "天不假年", "長才未盡", "玉折蘭摧"]
        elif "50至69歲" in male_age:
            middle_options = ["棟折梁摧", "典則空留", "英氣頓杳", "德望昭然", "風範長存"]
        elif "70歲至79歲" in male_age:
            middle_options = ["哲人其萎", "斗柄西移", "德業長昭", "典範長存"]
        elif "80歲以上" in male_age:
            middle_options = ["德高望重", "魯般圮毀", "仁者壽", "德望永昭"]
        else:
            middle_options = []

    if middle_options:
        selected_mid = st.sidebar.selectbox("選擇常用中款詞語", middle_options + ["自訂輸入"])
        if selected_mid == "自訂輸入":
            middle_text = st.sidebar.text_input("輸入自訂中款", "往生極樂")
        else:
            middle_text = selected_mid
    else:
        middle_text = st.sidebar.text_input("輸入自訂中款", "往生極樂")

else:  # 慶賀
    celeb_options = ["鴻圖大展", "駿業宏開", "生意興隆", "財源廣進", "大業千秋", "自訂輸入"]
    selected_celeb = st.sidebar.selectbox("選擇慶賀常用詞", celeb_options)
    if selected_celeb == "自訂輸入":
        middle_text = st.sidebar.text_input("輸入自訂慶賀詞", "鴻圖大展")
    else:
        middle_text = selected_celeb

# --- 下款設定 ---
st.sidebar.subheader("三、下款設定")
company_name = st.sidebar.text_input("公司 / 單位名稱位置（可留空）", "桃園市議員")
person_name = st.sidebar.text_input("名字位置", "李宗豪")
suffix_default = "敬輓" if card_type == "喪禮（輓聯）" else "敬賀"
suffix_type = st.sidebar.selectbox("結尾敬意", [suffix_default, "敬獻", "自訂"])
suffix_text = suffix_type if suffix_type != "自訂" else st.sidebar.text_input("自訂結尾詞", "敬輓")

# 組合下款（直式時：公司名稱、名字、敬輓由上至下排列於左側）
if company_name and person_name:
    lower_text = f"{company_name}<br>{person_name} {suffix_text}"
elif company_name:
    lower_text = f"{company_name} {suffix_text}"
elif person_name:
    lower_text = f"{person_name} {suffix_text}"
else:
    lower_text = suffix_text


# --- 主畫面預覽（A4 比例與排版） ---
st.subheader("📄 A4 預覽畫面")

if orientation == "直式":
    # A4 直式比例
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
        <!-- 左側：下款（最下左 敬輓） -->
        <div style="writing-mode: vertical-rl; font-size: 20px; letter-spacing: 2px; align-self: flex-end;">
            {lower_text}
        </div>
        <!-- 中間：中款（大字置中） -->
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
    # A4 橫式比例
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
        <!-- 上方：上款 -->
        <div style="display: flex; justify-content: space-between; font-size: 20px;">
            <div></div>
            <div>{upper_text}</div>
        </div>
        <!-- 中間：主旨大字 -->
        <div style="text-align: center; font-size: 50px; font-weight: bold; letter-spacing: 8px; margin: auto 0;">
            {middle_text}
        </div>
        <!-- 下方：下款 -->
        <div style="display: flex; justify-content: space-between; align-items: flex-end; font-size: 20px;">
            <div>{company_name}</div>
            <div>{person_name} {suffix_text}</div>
        </div>
    </div>
    """

st.markdown(layout_html, unsafe_allow_html=True)

st.info("💡 提示：您可隨時於左側選單切換男女年齡層、自訂欄位內容，或切換直式／橫式排版。")
