import streamlit as st
from weasyprint import HTML
import tempfile
import os

st.set_page_config(page_title="A4 賀卡/輓聯產生器", layout="wide", page_icon="📜")

st.title("📜 A4 專業賀卡與輓聯產生器")
st.markdown("支援**直式與橫式 A4** 排版、依年齡/性別精準對應中款、**下款三格獨立輸入**，以及**上中下款全方位位置調整**！")

# 側邊欄設定
st.sidebar.header("⚙️ 版面與模式設定")

card_mode = st.sidebar.radio("卡片類型", ["喪禮致意 (輓聯/花圈)", "慶賀開幕 (花牌/賀卡)"])
orientation = st.sidebar.radio("版面方向", ["直式 (Portrait)", "橫式 (Landscape)"])

st.sidebar.markdown("---")
st.sidebar.header("📐 上中下款獨立位置微調")
st.sidebar.markdown("您可以針對各個區塊獨立微調其位置，滿足不同的版面視覺需求：")

# 上款位置微調
st.sidebar.subheader("📌 上款位置微調")
upper_offset_x = st.sidebar.slider("上款 左右微調 (px)", -100, 100, 0, 5)
upper_offset_y = st.sidebar.slider("上款 上下微調 (px)", -100, 100, 0, 5)

# 中款位置微調
st.sidebar.subheader("📌 中款位置微調")
middle_offset_x = st.sidebar.slider("中款 左右微調 (px)", -100, 100, 0, 5)
middle_offset_y = st.sidebar.slider("中款 上下微調 (px)", -100, 100, 0, 5)

# 下款位置微調
st.sidebar.subheader("📌 下款位置微調")
lower_offset_x = st.sidebar.slider("下款 左右微調 (px)", -100, 100, 0, 5)
lower_offset_y = st.sidebar.slider("下款 上下微調 (px)", -100, 100, 0, 5)


# 根據模式設定內容
upper_text = ""
middle_text = ""

if card_mode == "喪禮致意 (輓聯/花圈)":
  st.sidebar.subheader("👤 逝者資訊與上款設定")
  gender = st.sidebar.radio("性別", ["女性", "男性"])

  if gender == "女性":
    age_group = st.sidebar.selectbox(
        "年齡層",
        [
            "少女、年輕女性（約 49 歲以下 / 未婚）",
            "中壯年女性（約 50 至 79 歲）",
            "高齡女性（80 歲以上）",
        ],
    )
    if "49" in age_group:
      default_middle_list = [
          "遽促芳齡",
          "玉殞香消",
          "芳華早謝",
          "蘭摧蕙折",
          "妝台月冷",
      ]
    elif "50" in age_group or "79" in age_group:
      default_middle_list = [
          "淑德永昭",
          "懿範長存",
          "慈容永念",
          "德業長昭",
          "巾幗模範",
      ]
    else:
      default_middle_list = [
          "萱範長存",
          "母儀千古",
          "駕返瑤池",
          "萱蔭長留",
          "壺範垂型",
      ]
  else:
    age_group = st.sidebar.selectbox(
        "年齡層",
        [
            "49歲以下（年輕、早逝）",
            "50至69歲（壯年至中老年）",
            "70至79歲（古稀）",
            "80歲以上（高壽、期頤）",
        ],
    )
    if "49" in age_group:
      default_middle_list = [
          "星隕少微",
          "玉樹長埋",
          "壯志未酬",
          "天不假年",
          "長才未盡",
          "玉折蘭摧",
      ]
    elif "69" in age_group or "50" in age_group:
      default_middle_list = [
          "棟折梁摧",
          "典則空留",
          "英氣頓杳",
          "德望昭然",
          "風範長存",
      ]
    elif "79" in age_group or "70" in age_group:
      default_middle_list = ["哲人其萎", "斗柄西移", "德業長昭", "典范長存"]
    else:
      default_middle_list = ["德高望重", "魯般圮毀", "仁者壽", "德望永昭"]

  # 上款設定
  respect_prefix = st.sidebar.text_input("上款敬辭", "敬悼")
  name_subject = st.sidebar.text_input(
      "逝者姓名與稱謂",
      "佛弟林文姬居士" if gender == "女性" else "林XX老先生",
  )
  suffix_action = st.sidebar.selectbox(
      "結尾尊稱", ["仙逝", "千古", "蓮前", "靈前", "永別"]
  )

  upper_text = f"{respect_prefix} {name_subject} {suffix_action}"

  # 中款設定
  st.sidebar.subheader("🔤 中款詞語設定")
  middle_choice = st.sidebar.selectbox(
      "常用中款挑選", ["自訂"] + default_middle_list
  )
  if middle_choice == "自訂":
    middle_text = st.sidebar.text_input("自訂中款內容", "往生極樂")
  else:
    middle_text = middle_choice

else:
  st.sidebar.subheader("🎉 慶賀開幕設定")
  upper_text = st.sidebar.text_input("上款內容", "恭祝 某某股份有限公司")

  celebration_list = ["鴻圖大展", "駿業宏開", "生意興隆", "財源廣進", "大業千秋"]
  middle_choice = st.sidebar.selectbox(
      "常用中款詞語", ["自訂"] + celebration_list
  )
  if middle_choice == "自訂":
    middle_text = st.sidebar.text_input("自訂中款內容", "鴻圖大展")
  else:
    middle_text = middle_choice

# 下款三格設定（多人送禮可分開填寫）
st.sidebar.subheader("✍️ 下款三格設定 (多人送禮/署名)")
lower_line1 = st.sidebar.text_input("下款第一格 (例如：機關/公司/職稱)", "桃園市議員")
lower_line2 = st.sidebar.text_input("下款第二格 (例如：第一位名字/主獻者)", "李宗豪")
lower_line3 = st.sidebar.text_input(
    "下款第三格 (例如：第二位名字 或 敬輓/敬賀)",
    "敬輓" if card_mode.startswith("喪禮") else "敬賀",
)

# 字體大小設定
st.sidebar.subheader("🔠 字體大小設定")
font_size_upper = st.sidebar.slider("上款字體大小 (pt)", 14, 36, 22)
font_size_middle = st.sidebar.slider("中款字體大小 (pt)", 24, 72, 44)
font_size_lower = st.sidebar.slider("下款字體大小 (pt)", 14, 32, 20)

# 主畫面預覽
st.subheader("👁️ A4 排版即時預覽")

is_portrait = "直式" in orientation

# HTML/CSS 排版 (支援獨立上下左右位移轉換)
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4 {'portrait' if is_portrait else 'landscape'};
    margin: 15mm;
  }}
  body {{
    font-family: 'Noto Sans CJK TC', 'Microsoft JhengHei', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #fcfbfa;
    color: #111;
  }}
  .page {{
    width: {'210mm' if is_portrait else '297mm'};
    height: {'297mm' if is_portrait else '210mm'};
    box-sizing: border-box;
    padding: 20mm;
    position: relative;
    background: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    margin: auto;
    overflow: hidden;
  }}
  
  /* 直式排版 (Vertical) */
  .layout-portrait {{
    height: 100%;
    width: 100%;
    position: relative;
  }}
  .layout-portrait .col-right {{
    position: absolute;
    right: 25mm;
    top: 50%;
    transform: translateY(-50%) translate({-upper_offset_x}px, {upper_offset_y}px);
    writing-mode: vertical-rl;
    font-size: {font_size_upper}pt;
    font-weight: bold;
    letter-spacing: 3px;
  }}
  .layout-portrait .col-center {{
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%) translate({-middle_offset_x}px, {middle_offset_y}px);
    writing-mode: vertical-rl;
    font-size: {font_size_middle}pt;
    font-weight: bold;
    letter-spacing: 8px;
    text-align: center;
  }}
  .layout-portrait .col-left {{
    position: absolute;
    left: 25mm;
    top: 50%;
    transform: translateY(-50%) translate({-lower_offset_x}px, {lower_offset_y}px);
    writing-mode: vertical-rl;
    font-size: {font_size_lower}pt;
    letter-spacing: 2px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* 橫式排版 (Landscape) */
  .layout-landscape {{
    height: 100%;
    width: 100%;
    position: relative;
  }}
  .layout-landscape .col-top-right {{
    position: absolute;
    top: 25mm;
    right: 25mm;
    transform: translate({-upper_offset_x}px, {upper_offset_y}px);
    font-size: {font_size_upper}pt;
    font-weight: bold;
    letter-spacing: 2px;
  }}
  .layout-landscape .col-center {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) translate({middle_offset_x}px, {middle_offset_y}px);
    font-size: {font_size_middle}pt;
    font-weight: bold;
    letter-spacing: 8px;
    text-align: center;
    width: 100%;
  }}
  .layout-landscape .col-bottom-left {{
    position: absolute;
    bottom: 25mm;
    left: 25mm;
    transform: translate({lower_offset_x}px, {-lower_offset_y}px);
    font-size: {font_size_lower}pt;
    letter-spacing: 2px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
</style>
</head>
<body>
<div class="page">
  {"<div class='layout-portrait'>" if is_portrait else "<div class='layout-landscape'>"}
    
    <!-- 上款 -->
    <div class="{'col-right' if is_portrait else 'col-top-right'}">{upper_text}</div>
    
    <!-- 中款 -->
    <div class="col-center">{middle_text}</div>
    
    <!-- 下款三格 -->
    <div class="{'col-left' if is_portrait else 'col-bottom-left'}">
      <div>{lower_line1}</div>
      <div>{lower_line2}</div>
      <div>{lower_line3}</div>
    </div>

  </div>
</div>
</body>
</html>
"""

# 顯示網頁即時預覽
st.components.v1.html(html_content, height=750, scrolling=True)

# 下載 PDF 按鈕
if st.button("📥 產生並下載 A4 高畫質 PDF", type="primary"):
  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
    pdf_path = tmp.name

  html_file = pdf_path.replace(".pdf", ".html")
  with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

  HTML(html_file).write_pdf(pdf_path)

  with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

  st.download_button(
      label="點此下載產生的 A4 PDF 檔案",
      data=pdf_bytes,
      file_name="a4_card_output.pdf",
      mime="application/pdf",
  )
  st.success("✅ PDF 產生成功！請點擊上方按鈕下載。")
