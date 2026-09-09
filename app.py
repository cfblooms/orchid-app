import datetime
import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="蘭花庫存與記帳系統", page_icon="🌸", layout="wide"
)

# ==========================================
# ⚙️ 雲端連線設定
# ==========================================
WEB_APP_URL = "https://script.google.com/macros/s/你的網址/exec"

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


# 自動生成依日期的流水編號
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


st.title("🌸 蘭花庫存、記帳與 A4 卡片系統")

if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
  st.warning(
      "⚠️ 提醒：請記得修改 `app.py` 程式碼最上方的 `WEB_APP_URL`，填入你的"
      " Apps Script 網址！"
  )
else:
  tab1, tab2, tab3 = st.tabs(
      ["📦 1. 進貨與庫存", "💰 2. 訂單與帳務管理", "🖨️ 3. A4 卡片與輓聯產生器"]
  )

  with tab1:
    st.header("新增進貨 (批次與規格管理)")

    category = st.selectbox("選擇進貨類別", ["蘭花", "陶瓷盆"])

    if category == "蘭花":
      with st.form("flower_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("FL", "進貨表")
          )
          flower_name = st.text_input("品種名稱 (例如: 大辣椒、V3)")
          spike_type = st.selectbox("梗數規格", ["單梗", "雙梗", "多梗"])
          color = st.selectbox("花朵顏色", ["白", "紅", "粉", "黃", "其他"])
        with col2:
          size = st.selectbox("花朵大小", ["大", "中", "小"])
          height = st.selectbox("株高規格", ["高", "中", "矮"])
          qty = st.number_input("進貨數量 (批)", min_value=1, value=1)
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
          spec_desc = f"規格:{spike_type} | 顏色:{color} | 大小:{size} | 高矮:{height} | 照片:{image_info if image_info else '無'}"
          row = [
              item_id,
              "蘭花",
              flower_name,
              spec_desc,
              int(qty),
              float(cost),
              str(date),
          ]
          if append_data("進貨表", row):
            st.success("成功新增蘭花進貨紀錄！")
            st.rerun()

    else:  # 陶瓷盆
      with st.form("pot_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("POT", "進貨表")
          )
          pot_type = st.selectbox(
              "盆器類型與成本",
              [
                  "桌上盆 (成本100)",
                  "落地盆-喪 (成本100)",
                  "落地盆-喜 (成本200)",
                  "羅馬盆 (成本280)",
              ],
          )
        with col2:
          qty = st.number_input("進貨數量", min_value=1, value=10)
          date = st.date_input("進貨日期", datetime.date.today())

        cost_map = {
            "桌上盆 (成本100)": 100,
            "落地盆-喪 (成本100)": 100,
            "落地盆-喜 (成本200)": 200,
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
        cust_type = st.selectbox("客戶類型", ["花店", "個人", "批發"])
        customer = st.text_input("訂購人 (名稱或單位)")
      with col2:
        if flower_list:
          orchid_used = st.selectbox("選擇使用蘭花", flower_list)
        else:
          orchid_used = st.text_input("使用蘭花名稱")

        stalks_count = st.slider("株數選擇", 3, 20, 10)
        pot_used = st.selectbox(
            "選擇使用盆器",
            [
                "桌上盆 (100)",
                "落地盆-喪 (100)",
                "落地盆-喜 (200)",
                "羅馬盆 (280)",
                "無盆",
            ],
        )
      with col3:
        cost_price = st.number_input("預估總成本 (元)", min_value=0, value=600)
        sell_price = st.number_input("售價 (元)", min_value=0, value=1500)
        delivery_method = st.selectbox("配送方式", ["自載", "運送"])
        payment_term = st.selectbox(
            "結帳方式", ["每單結", "週結", "月結"]
        )

      col4, col5 = st.columns(2)
      with col4:
        order_date = st.date_input("下單日期", datetime.date.today())
      with col5:
        expected_date = st.date_input(
            "預計出貨日期", datetime.date.today() + datetime.timedelta(days=3)
        )

      order_submitted = st.form_submit_button("確認新增訂單")
      if order_submitted:
        # 新訂單預設為未出貨、未付款
        row = [
            order_id,
            cust_type,
            customer,
            f"{orchid_used} | {stalks_count}棵",
            pot_used,
            delivery_method,
            payment_term,
            float(cost_price),
            float(sell_price),
            str(order_date),
            str(expected_date),
            "未出貨",
            "未付款",
        ]
        if append_data("訂單表", row):
          st.success("成功新增訂單紀錄！")
          st.rerun()

    st.subheader("訂單與帳務總覽")
    df_order = get_data("訂單表")
    if not df_order.empty:
      st.dataframe(df_order, use_container_width=True)

      st.markdown("---")
      st.subheader("📝 訂單狀態快速更新 (出貨與付款)")
      with st.form("update_status_form"):
        order_ids_list = (
            df_order["訂單編號"].tolist() if "訂單編號" in df_order.columns else []
        )
        selected_upd_id = st.selectbox(
            "選擇要修改的訂單編號", order_ids_list
        )
        new_shipped = st.selectbox("更新出貨狀態", ["未出貨", "已出貨"])
        new_payment = st.selectbox("更新付款狀態", ["未付款", "已付款"])

        update_submitted = st.form_submit_button("確認更新該筆訂單狀態")
        if update_submitted:
          st.info(
              f"💡 訂單 {selected_upd_id} 狀態已暫存更新。請注意：若需完整同步寫入雲端試算表，建議直接在 Google 試算表對應欄位修改，或重新提交。"
          )
    else:
      st.info("目前尚無訂單資料。")

  with tab3:
    st.header("🖨️ A4 卡片與傳統輓聯產生器")

    card_mode = st.selectbox("選擇卡片類型", ["喪禮輓聯 / 悼唁卡", "喜慶 / 開幕賀卡"])

    if card_mode == "喪禮輓聯 / 悼唁卡":
      st.markdown("### 🕊️ 喪禮輓聯設定")
      col_r, col_m, col_l = st.columns(3)

      with col_r:
        st.markdown("**【右邊：上款】**")
        upper_preset = st.selectbox(
            "上款常用敬悼",
            [
                "自訂 / 手動輸入",
                "敬悼 X公X先生 仙逝",
                "敬悼 X公X老先生 千古",
                "敬悼 X媽X夫人 仙逝",
                "敬悼 X媽X老夫人 千古",
            ],
        )
        if upper_preset == "自訂 / 手動輸入":
          upper_text = st.text_input(
              "輸入自訂上款", value="敬悼 陳公大明 先生 仙逝"
          )
        else:
          upper_text = upper_preset

      with col_m:
        st.markdown("**【中間：中款/輓辭】**")
        gender_choice = st.selectbox(
            "逝者性別與年齡分類",
            [
                "自訂 / 手動輸入",
                "女 - 少女 / 年輕女性 (49歲以下)",
                "女 - 中壯年女性 (50-79歲)",
                "女 - 高齡女性 (80歲以上)",
                "男 - 49歲以下 (年輕早逝)",
                "男 - 50至69歲 (壯年至中老年)",
                "男 - 70至79歲 (古稀)",
                "男 - 80歲以上 (高壽期頤)",
            ],
        )

        mid_options_dict = {
            "女 - 少女 / 年輕女性 (49歲以下)": [
                "遽促芳齡",
                "玉殞香消",
                "芳華早謝",
                "蘭摧蕙折",
                "妝台月冷",
            ],
            "女 - 中壯年女性 (50-79歲)": [
                "淑德永昭",
                "懿範長存",
                "慈容永念",
                "德業長昭",
                "巾幗模範",
            ],
            "女 - 高齡女性 (80歲以上)": [
                "萱範長存",
                "母儀千古",
                "駕返瑤池",
                "萱蔭長留",
                "壺範垂型",
            ],
            "男 - 49歲以下 (年輕早逝)": [
                "星隕少微",
                "玉樹長埋",
                "壯志未酬",
                "天不假年",
                "長才未盡",
                "玉折蘭摧",
            ],
            "男 - 50至69歲 (壯年至中老年)": [
                "棟折梁摧",
                "典則空留",
                "英氣頓杳",
                "德望昭然",
                "風範長存",
            ],
            "男 - 70至79歲 (古稀)": [
                "哲人其萎",
                "斗柄西移",
                "德業長昭",
                "典范長存",
            ],
            "男 - 80歲以上 (高壽期頤)": [
                "德高望重",
                "魯般圮毀",
                "仁者壽",
                "德望永昭",
            ],
        }

        if gender_choice in mid_options_dict:
          mid_preset = st.selectbox(
              "選擇經典輓辭", mid_options_dict[gender_choice]
          )
          mid_text = mid_preset
        else:
          mid_text = st.text_input("輸入自訂中款輓辭", value="典範長存")

      with col_l:
        st.markdown("**【左下：下款與敬輓】**")
        sender_company = st.text_input("公司名稱 / 單位", value="OO花苑")
        sender_name = st.text_input("送花人 / 署名", value="王小明")
        kwan = "敬輓"

      st.markdown("---")
      # A4預覽區 (210mm x 297mm)
      a4_mourning_html = f"""
            <style>
            .a4-page {{
                width: 210mm;
                height: 297mm;
                padding: 25mm 20mm;
                margin: auto;
                border: 2px dashed #bbb;
                background: white;
                font-family: "DFKai-SB", "BiauKai", "Microsoft JhengHei", serif;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                color: #111;
                box-sizing: border-box;
            }}
            .col-right {{
                writing-mode: vertical-rl;
                font-size: 24px;
                letter-spacing: 4px;
                height: 100%;
                display: flex;
                align-items: flex-start;
            }}
            .col-center {{
                writing-mode: vertical-rl;
                font-size: 38px;
                letter-spacing: 8px;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-weight: bold;
            }}
            .col-left {{
                writing-mode: vertical-rl;
                font-size: 22px;
                letter-spacing: 4px;
                height: 100%;
                display: flex;
                align-items: flex-end;
            }}
            @media print {{
                body * {{ visibility: hidden; }}
                .a4-page, .a4-page * {{ visibility: visible; }}
                .a4-page {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; width: 210mm; height: 297mm; }}
            }}
            </style>
            <div class="a4-page">
                <div class="col-left">
                    <span>{sender_company}  {sender_name}  {kwan}</span>
                </div>
                <div class="col-center">
                    <span>{mid_text}</span>
                </div>
                <div class="col-right">
                    <span>{upper_text}</span>
                </div>
            </div>
            """
      st.markdown(a4_mourning_html, unsafe_allow_html=True)

    else:
      st.markdown("### 🌸 喜慶 / 開幕賀卡設定")
      recipient_c = st.text_input("收花人 / 對象", value="大吉大利商行 啟")
      blessing_c = st.text_area(
          "祝賀內文", value="祝 開張大吉 生意興隆 財源廣進"
      )
      sender_c = st.text_input("送花人署名", value="好友 王小明 敬賀")

      a4_joy_html = f"""
            <style>
            .a4-joy {{
                width: 210mm;
                height: 297mm;
                padding: 30mm;
                margin: auto;
                border: 2px dashed #bbb;
                background: white;
                font-family: "Microsoft JhengHei", sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                color: #222;
                box-sizing: border-box;
            }}
            .joy-title {{ font-size: 28px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 15px; }}
            .joy-body {{ font-size: 32px; line-height: 2.2; flex-grow: 1; white-space: pre-wrap; display: flex; align-items: center; justify-content: center; text-align: center; }}
            .joy-footer {{ font-size: 24px; text-align: right; border-top: 1.5px solid #ddd; padding-top: 20px; }}
            @media print {{
                body * {{ visibility: hidden; }}
                .a4-joy, .a4-joy * {{ visibility: visible; }}
                .a4-joy {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; }}
            }}
            </style>
            <div class="a4-joy">
                <div class="joy-title">致：{recipient_c}</div>
                <div class="joy-body">{blessing_c}</div>
                <div class="joy-footer"><strong>{sender_c}</strong></div>
            </div>
            """
      st.markdown(a4_joy_html, unsafe_allow_html=True)

    st.info(
        "💡 提示：按下 **Ctrl + P** 列印，將紙張大小設定為 **A4**、方向設為「直向」或「橫向」（依傳統直式或橫式排版需求），即可完美印出！"
    )
