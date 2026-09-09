import streamlit as st

st.set_page_config(page_title="A4 賀卡/輓聯排版系統", layout="wide")

st.title("🖨️ A4 賀卡與輓聯即時排版系統")

# 初始化 Session State 以記錄位置與大小（支援拖曳與滑桿聯動）
if "top_y" not in st.session_state: st.session_state.top_y = 40
if "mid_y" not in st.session_state: st.session_state.mid_y = 180
if "bottom_y" not in st.session_state: st.session_state.bottom_y = 350

if "font_top" not in st.session_state: st.session_state.font_top = 22
if "font_mid" not in st.session_state: st.session_state.font_mid = 56
if "font_bottom" not in st.session_state: st.session_state.font_bottom = 20

# === 側邊欄：文字內容與精準控制 ===
st.sidebar.header("📝 內容與排版設定")

top_text = st.sidebar.text_input("上款 (例如：祝賀某某某 / 榮任)", "恭喜開店 財源廣進")
middle_text = st.sidebar.text_input("中款 (主體賀詞 / 悼詞)", "大展鴻圖")

st.sidebar.subheader("下款名字（最多 5 位）")
name1 = st.sidebar.text_input("下款名字 1", "王小明")
name2 = st.sidebar.text_input("下款名字 2", "李美麗")
name3 = st.sidebar.text_input("下款名字 3", "")
name4 = st.sidebar.text_input("下款名字 4", "")
name5 = st.sidebar.text_input("下款名字 5", "")

respect_text = st.sidebar.selectbox("敬意字眼", ["敬輓", "敬悼", "敬賀", "謹上"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎚️ 字體大小精準微調")
st.session_state.font_top = st.sidebar.slider("上款字型大小", 12, 40, st.session_state.font_top)
st.session_state.font_mid = st.sidebar.slider("中款字型大小", 20, 120, st.session_state.font_mid)
st.session_state.font_bottom = st.sidebar.slider("下款字型大小", 12, 40, st.session_state.font_bottom)

# 組合 5 個下款名字
names = [n.strip() for n in [name1, name2, name3, name4, name5] if n.strip()]
bottom_combined = " ".join(names) + " " + respect_text if names else ""

# === 主畫面：A4 預覽與拖曳互動區 ===
st.markdown("### 🖼️ A4 即時排版預覽（支援預覽與列印格式）")
st.info("💡 提示：您可以使用左側滑桿調整字體大小，或直接在下方預覽區預覽列印效果。")

# A4 比例容器 (模擬 A4 紙張直式排版)
card_html = f"""
<div style="width: 100%; max-width: 650px; height: 920px; border: 2px solid #333; margin: 0 auto; position: relative; background: #fff; font-family: 'DFKai-SB', 'BiauKai', 'Microsoft JhengHei', serif; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 40px; box-sizing: border-box;">
    
    <!-- 上款 -->
    <div style="position: absolute; top: {st.session_state.top_y}px; left: 50%; transform: translateX(-50%); font-size: {st.session_state.font_top}px; white-space: nowrap; font-weight: bold;">
        {top_text}
    </div>
    
    <!-- 中款 -->
    <div style="position: absolute; top: {st.session_state.mid_y}px; left: 50%; transform: translateX(-50%); font-size: {st.session_state.font_mid}px; white-space: nowrap; font-weight: bold; letter-spacing: 8px;">
        {middle_text}
    </div>
    
    <!-- 下款（結合 5 個名字與敬輓/敬悼） -->
    <div style="position: absolute; bottom: {st.session_state.bottom_y}px; right: 60px; font-size: {st.session_state.font_bottom}px; white-space: nowrap; font-weight: bold; text-align: right;">
        {bottom_combined}
    </div>
</div>
"""

st.markdown(card_html, unsafe_allow_html=True)

# 列印輸出按鈕
if st.button("🖨️ 產生列印排版視窗"):
    st.success("已準備好列印畫面！您可以直接點擊瀏覽器的列印功能（Ctrl+P / Cmd+P）輸出至 A4 印表機。")
