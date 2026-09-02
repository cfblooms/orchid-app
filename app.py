import datetime
import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="蘭花庫存與記帳系統", page_icon="🌸", layout="wide"
)

# ==========================================
# ⚙️ 雲端連線設定（直接寫在這裡，手機跟電腦就不用每次重打！）
# ==========================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyqYxnd5EyM3JK_DHriIBOV1AcUvq6s7fGHWfTj14uFgxc8cD5XcomqGUP072Bnjb49/exec"

# 自動建立本地相片儲存資料夾
if not os.path.exists("photos"):
  os.makedirs("photos")


# 讀取資料函式
def get_data(sheet_name):
  if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
    return pd.DataFrame()
  try:
    response = requests.get(f"{WEB_APP_URL}?sheet={sheet_name}")
    data = response.json()
    if isinstance(data, list) and len(data) > 0:
      return pd.DataFrame(data)
    return pd.DataFrame()
  except Exception as e:
    return pd.DataFrame()


# 寫入資料函式
def append_data(sheet_name, row_data):
  if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
    st.error("請先在程式碼最上方填入正確的 Apps Script 網址！")
    return False
  try:
    payload = {"sheet": sheet_name, "data": row_data}
    response = requests.post(WEB_APP_URL, json=payload)
    res_json = response.json()
    if res_json.get("status") == "success":
      return True
    else:
      st.error(f"寫入失敗: {res_json.get('message')}")
      return False
  except Exception as e:
    st.error(f"連線失敗: {e}")
    return False


# 自動生成依日期的流水編號 (例如: FL060401, POT060401, OR060401)
def get_next_id(prefix, sheet_name):
  today_str = datetime.datetime.now().strftime("%m%d")
  df = get_data(sheet_name)
  if df.empty or len(df.columns) == 0:
    return f"{prefix}{today_str}01"
  try:
    id_col = df.columns[0]
    base_pattern = f"{prefix}{today_str}"
    matching = df[df[id_col].astype(str).str.startswith(base_pattern, na=False)]
    count = len(matching) + 1
    return f"{prefix}{today_str}{count:02d}"
  except Exception:
    return f"{prefix}{today_str}01"


st.title("🌸 蘭花庫存、記帳與 A5 賀卡系統")

if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
  st.warning(
      "⚠️ 提醒：請記得修改 `app.py` 程式碼最上方的 `WEB_APP_URL`，填入你的"
      " Apps Script 網址！"
  )
else:
  tab1, tab2, tab3 = st.tabs(
      ["📦 1. 進貨與庫存 (規格化)", "💰 2. 訂單與記帳", "🖨️ 3. A5 賀卡產生器"]
  )

  with tab1:
    st.header("新增進貨 (精準規格與照片上傳區)")

    category = st.selectbox("選擇進貨類別", ["蘭花", "陶瓷盆"])

    if category == "蘭花":
      with st.form("flower_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("FL", "進貨表")
          )
          flower_name = st.text_input("花的品種名稱 (例如: 大辣椒、V3)")
          spike_type = st.selectbox("梗數規格", ["單梗", "雙梗"])
          color = st.selectbox("花朵顏色", ["白", "紅", "粉", "其他"])
        with col2:
          height = st.selectbox("株高", ["高", "矮"])
          size = st.selectbox("花朵大小", ["大朵", "小朵"])
          stalks = st.slider("株數選擇", 3, 20, 10)
          cost = st.number_input("總進貨成本 (元)", min_value=0, value=800)
          date = st.date_input("進貨日期", datetime.date.today())

        uploaded_file = st.file_uploader(
            "📷 上傳蘭花照片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"]
        )

        image_info = ""
        if uploaded_file is not None:
          st.image(uploaded_file, caption="上傳照片預覽", width=250)
          file_ext = uploaded_file.name.split(".")[-1]
          image_filename = f"{item_id}_{datetime.datetime.now().strftime('%H%M%S')}.{file_ext}"
          image_path = os.path.join("photos", image_filename)
          with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
          image_info = image_path

        submitted = st.form_submit_button("確認新增蘭花進貨")
        if submitted:
          spec_desc = f"規格:{spike_type} | 顏色:{color} | 高矮:{height} | 大小:{size} | 照片檔:{image_info if image_info else '無'}"
          row = [
              item_id,
              "蘭花",
              flower_name,
              spec_desc,
              int(stalks),
              float(cost),
              str(date),
          ]
          if append_data("進貨表", row):
            st.success("成功新增蘭花進貨紀錄與照片！")
            st.rerun()

    else:  # 陶瓷盆
      with st.form("pot_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("POT", "進貨表")
          )
          pot_type = st.selectbox(
              "盆器類型與固定成本",
              ["桌上盆 (成本100)", "落地盆 (成本150)", "羅馬盆 (成本280)"],
          )
        with col2:
          qty = st.number_input("進貨數量", min_value=1, value=10)
          date = st.date_input("進貨日期", datetime.date.today())

        cost_map = {
            "桌上盆 (成本100)": 100,
            "落地盆 (成本150)": 150,
            "羅馬盆 (成本280)": 280,
        }
        unit_cost = cost_map[pot_type]
        total_cost = unit_cost * int(qty)
        st.info(f"💡 系統自動計算總成本：{total_cost} 元 ({unit_cost}元/個)")

        submitted_pot = st.form_submit_button("確認新增盆器進貨")
        if submitted_pot:
          row = [
              item_id,
              "陶瓷盆",
              pot_type.split(" ")[0],
              "固定規格",
              int(qty),
              float(total_cost),
              str(date),
          ]
          if append_data("進貨表", row):
            st.success("成功新增盆器進貨紀錄！")
            st.rerun()

    st.subheader("現有進貨清單")
    df_inv = get_data("進貨表")
    if not df_inv.empty:
      st.dataframe(df_inv, use_container_width=True)
    else:
      st.info("目前尚無進貨資料。")

  with tab2:
    st.header("訂單登錄與帳務管理")

    df_inv_check = get_data("進貨表")
    flower_list = []
    if not df_inv_check.empty and "類別" in df_inv_check.columns:
      flower_df = df_inv_check[df_inv_check["類別"] == "蘭花"]
      if not flower_df.empty:
        flower_list = (
            flower_df["品項名稱/品種"] + " (" + flower_df["規格細節"] + ")"
        ).tolist()

    with st.form("order_form"):
      col1, col2, col3 = st.columns(3)
      with col1:
        order_id = st.text_input(
            "訂單編號", value=get_next_id("OR", "訂單表")
        )
        cust_type = st.selectbox("客戶類型", ["花店", "個人"])
        customer = st.text_input("訂購人 (花店名稱或個人姓名)")
      with col2:
        if flower_list:
          orchid_used = st.selectbox("選擇使用蘭花 (直接帶入)", flower_list)
        else:
          orchid_used = st.text_input(
              "使用蘭花 (請先至進貨表新增或手動輸入)"
          )

        pot_used = st.selectbox(
            "選擇使用盆器", ["桌上盆 (100)", "落地盆 (150)", "羅馬盆 (280)", "無盆"]
        )
        cost_price = st.number_input(
            "預估總成本 (元)", min_value=0, value=600
        )
      with col3:
        sell_price = st.number_input("售價 (元)", min_value=0, value=1500)
        order_date = st.date_input("下單日期", datetime.date.today())
        expected_date = st.date_input(
            "預計出貨日期", datetime.date.today() + datetime.timedelta(days=3)
        )

      col4, col5 = st.columns(2)
      with col4:
        shipped = st.selectbox("已出貨狀態", ["未出貨", "已出貨"])
      with col5:
        payment = st.selectbox("付款狀態", ["未付款", "已付款"])

      order_submitted = st.form_submit_button("確認新增訂單")
      if order_submitted:
        row = [
            order_id,
            cust_type,
            customer,
            orchid_used,
            pot_used,
            float(cost_price),
            float(sell_price),
            str(order_date),
            str(expected_date),
            shipped,
            payment,
        ]
        if append_data("訂單表", row):
          st.success("成功新增訂單紀錄！")
          st.rerun()

    st.subheader("訂單與帳務總覽")
    df_order = get_data("訂單表")
    if not df_order.empty:
      st.dataframe(df_order, use_container_width=True)
    else:
      st.info("目前尚無訂單資料。")

  with tab3:
    st.header("🖨️ A5 賀卡產生器")
    df_card = get_data("訂單表")
    if not df_card.empty and "訂單編號" in df_card.columns:
      selected_order = st.selectbox(
          "選擇要印製賀卡的訂單編號", df_card["訂單編號"].tolist()
      )

      recipient = st.text_input("收花人", value="")
      blessing = st.text_area(
          "祝賀文字", value="祝開張大吉 生意興隆財源廣進"
      )
      sender = st.text_input("送花人落款", value="")

      st.markdown("---")
      card_html = f"""
            <style>
            .a5-card {{
                width: 148mm;
                height: 210mm;
                padding: 20mm;
                margin: auto;
                border: 2px dashed #ccc;
                background: white;
                font-family: "Microsoft JhengHei", sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                color: #333;
            }}
            .card-title {{
                font-size: 24px;
                font-weight: bold;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .card-body {{
                font-size: 20px;
                line-height: 1.8;
                flex-grow: 1;
                white-space: pre-wrap;
            }}
            .card-footer {{
                font-size: 18px;
                text-align: right;
                border-top: 1px solid #ddd;
                padding-top: 15px;
            }}
            @media print {{
                body * {{ visibility: hidden; }}
                .a5-card, .a5-card * {{ visibility: visible; }}
                .a5-card {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; }}
            }}
            </style>
            <div class="a5-card">
                <div>
                    <div class="card-title">致：{recipient if recipient else "（請填寫收花人）"}</div>
                    <div class="card-body">{blessing}</div>
                </div>
                <div class="card-footer">
                    <strong>祝賀人：{sender if sender else "（請填寫送花人）"}</strong>
                </div>
            </div>
            """
      st.markdown(card_html, unsafe_allow_html=True)
      st.info(
          "💡 提示：按 Ctrl+P 列印，將紙張大小設定為 **A5**、邊距設為「無」，即可印出完美賀卡！"
      )
    else:
      st.info("請先在「訂單」頁籤新增訂單，才能在此處列印賀卡。")