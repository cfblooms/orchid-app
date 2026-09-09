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
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNmqySFSFKuGzqEzTc9A52SwkmTToCf2N-4pXI0EmOPFgriV1Bana3rLjgo-Q3WqtM/exec"

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


# 寫入資料函式 (新增)
def append_data(sheet_name, row_data):
  try:
    payload = {"sheet": sheet_name, "action": "append", "data": row_data}
    response = requests.post(WEB_APP_URL, json=payload)
    res_json = response.json()
    return res_json.get("status") == "success"
  except Exception as e:
    st.error(f"連線失敗: {e}")
    return False


# 更新資料函式
def update_data(sheet_name, record_id, row_data):
  try:
    payload = {
        "sheet": sheet_name,
        "action": "update",
        "id": record_id,
        "data": row_data,
    }
    response = requests.post(WEB_APP_URL, json=payload)
    res_json = response.json()
    return res_json.get("status") == "success"
  except Exception as e:
    st.error(f"更新失敗: {e}")
    return False


# 刪除資料函式
def delete_data(sheet_name, record_id):
  try:
    payload = {"sheet": sheet_name, "action": "delete", "id": record_id}
    response = requests.post(WEB_APP_URL, json=payload)
    res_json = response.json()
    return res_json.get("status") == "success"
  except Exception as e:
    st.error(f"刪除失敗: {e}")
    return False


# 自動生成流水編號
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
  st.warning("⚠️ 提醒：請確認雲端網址是否正確。")
else:
  tab1, tab2, tab3 = st.tabs(
      ["📦 1. 進貨與庫存管理", "💰 2. 訂單與帳務管理", "🖨️ 3. A4 卡片與傳統輓聯"]
  )

  with tab1:
    st.header("新增進貨與庫存管理")

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

        submitted = st.form_submit_button("確認新增蘭花進貨")
        if submitted:
          spec_desc = f"規格:{spike_type} | 顏色:{color} | 大小:{size} | 高矮:{height}"
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

    else:
      with st.form("pot_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("POT", "進貨表")
          )
          pot_type = st.selectbox(
              "盆器類型",
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
        total_cost = cost_map[pot_type] * int(qty)

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

    st.markdown("---")
    st.subheader("📦 現有進貨清單 (修改與刪除)")
    df_inv = get_data("進貨表")
    if not df_inv.empty:
      st.dataframe(df_inv, use_container_width=True)

      inv_ids = (
          df_inv[df_inv.columns[0]].astype(str).tolist()
          if len(df_inv.columns) > 0
          else []
      )
      selected_inv_id = st.selectbox("選擇要管理的進貨項目編號", inv_ids)

      col_del, col_edit = st.columns(2)
      with col_del:
        if st.button("🗑️ 刪除此筆進貨紀錄"):
          if delete_data("進貨表", selected_inv_id):
            st.success(f"已成功刪除進貨編號：{selected_inv_id}")
            st.rerun()

      with col_edit:
        st.info("💡 如需修改，可直接刪除後重新新增正確資料。")
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

        if cust_type == "批發":
          batch_qty = st.number_input("批發數量 (批)", min_value=1, value=1)
          pot_used = "批發免盆"
        else:
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
        payment_term = st.selectbox("結帳方式", ["每單結", "週結", "月結"])

      col4, col5 = st.columns(2)
      with col4:
        order_date = st.date_input("下單日期", datetime.date.today())
      with col5:
        expected_date = st.date_input(
            "預計出貨日期", datetime.date.today() + datetime.timedelta(days=3)
        )

      order_submitted = st.form_submit_button("確認新增訂單")
      if order_submitted:
        if cust_type == "批發":
          item_spec_str = f"{orchid_used} | 批發 {batch_qty} 批"
        else:
          item_spec_str = f"{orchid_used} | {stalks_count}棵"

        row = [
            order_id,
            cust_type,
            customer,
            item_spec_str,
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

    st.subheader("💰 訂單與帳務總覽 (狀態更新與刪除)")
    df_order = get_data("訂單表")
    if not df_order.empty:
      st.dataframe(df_order, use_container_width=True)

      st.markdown("---")
      order_ids_list = (
          df_order["訂單編號"].tolist() if "訂單編號" in df_order.columns else []
      )

      col_o1, col_o2 = st.columns(2)
      with col_o1:
        st.subheader("📝 更新訂單狀態")
        with st.form("update_status_form"):
          selected_upd_id = st.selectbox(
              "選擇要修改的訂單編號", order_ids_list
          )
          new_shipped = st.selectbox("更新出貨狀態", ["未出貨", "已出貨"])
          new_payment = st.selectbox("更新付款狀態", ["未付款", "已付款"])
          update_submitted = st.form_submit_button("確認更新狀態")

          if update_submitted:
            # 找到該筆訂單原本的資料並更新狀態欄位
            matched_row = df_order[df_order["訂單編號"] == selected_upd_id]
            if not matched_row.empty:
              r_list = matched_row.values.tolist()[0]
              r_list[-2] = new_shipped  # 倒數第二欄：出貨狀態
              r_list[-1] = new_payment  # 最後一欄：付款狀態
              if update_data("訂單表", selected_upd_id, r_list):
                st.success(f"訂單 {selected_upd_id} 狀態已更新！")
                st.rerun()

      with col_o2:
        st.subheader("🗑️ 刪除訂單")
        with st.form("delete_order_form"):
          selected_del_id = st.selectbox(
              "選擇要刪除的訂單編號", order_ids_list, key="del_order_sel"
          )
          del_submitted = st.form_submit_button("確認刪除此訂單")
          if del_submitted:
            if delete_data("訂單表", selected_del_id):
              st.success(f"已成功刪除訂單：{selected_del_id}")
              st.rerun()
    else:
      st.info("目前尚無訂單資料。")

  with tab3:
    st.header("🖨️ A4 傳統輓聯與卡片產生器 (標楷體)")

    card_mode = st.selectbox("選擇卡片類型", ["喪禮傳統輓聯", "喜慶 / 開幕賀卡"])

    if card_mode == "喪禮傳統輓聯":
      st.markdown("### 🕊️ 傳統輓聯設定 (直式 / 橫式)")

      orientation = st.radio(
          "選擇列印排版方向", ["直式排版 (傳統直書)", "橫式排版 (如圖片風格)"], horizontal=True
      )

      card_style_bg = st.selectbox(
          "卡片背景風格",
          ["典雅紫藍暈染風 (如範例圖)", "簡約純白底色 (適合彩色列印機)"],
      )

      with st.expander("⚙️ 調整字體大小設定", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
          sz_upper = st.slider("上款字體大小", 40, 120, 72)
        with f_col2:
          sz_mid = st.slider("中款字體大小", 100, 250, 180)
        with f_col3:
          sz_lower = st.slider("下款字體大小", 40, 120, 80)
        with f_col4:
          sz_kwan = st.slider("敬輓字體大小", 40, 120, 70)

      col_r, col_m, col_l = st.columns(3)

      with col_r:
        st.markdown("**【上款設定】**")
        upper_preset = st.selectbox(
            "上款常用敬悼",
            [
                "自訂 / 手動輸入",
                "敬悼 林媽莊老夫人仙逝",
                "敬悼 林公春吉先生 千古",
                "敬悼 臺北市政府",
                "敬悼 X公X先生 仙逝",
            ],
        )
        if upper_preset == "自訂 / 手動輸入":
          upper_text = st.text_input("輸入自訂上款", value="敬悼")
        else:
          upper_text = upper_preset

      with col_m:
        st.markdown("**【中款 / 輓辭設定】**")
        gender_choice = st.selectbox(
            "逝者性別與年齡分類",
            [
                "自訂 / 手動輸入",
                "上品上生",
                "女 - 德高望重",
                "男 - 80歲以上 (高壽期頤)",
            ],
        )
        if gender_choice == "自訂 / 手動輸入":
          mid_text = st.text_input("輸入自訂中款輓辭", value="上品上生")
        else:
          mid_text = gender_choice

      with col_l:
        st.markdown("**【下款與敬輓設定】**")
        sender_company = st.text_input("公司名稱 / 機關", value="臺北市政府")
        sender_name = st.text_input("姓名 / 落款", value="")
        kwan_text = st.text_input("敬輓字樣", value="敬輓")

      st.markdown("---")

      bg_css = (
          "background: linear-gradient(135deg, #e3e8f8 0%, #f3e6f8 100%);"
          if "紫藍暈染" in card_style_bg
          else "background: white;"
      )

      if orientation == "直式排版 (傳統直書)":
        a4_html = f"""
                <style>
                .a4-page {{
                    width: 210mm;
                    height: 297mm;
                    padding: 20mm 15mm;
                    margin: auto;
                    border: 2px dashed #bbb;
                    {bg_css}
                    font-family: "DFKai-SB", "BiauKai", "標楷體", "KaiTi", serif;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    box-sizing: border-box;
                    box-shadow: 0 0 15px rgba(0,0,0,0.1);
                    color: #000;
                }}
                .col-right {{ writing-mode: vertical-rl; font-size: {sz_upper}px; letter-spacing: 4px; height: 90%; display: flex; align-items: flex-start; }}
                .col-center {{ writing-mode: vertical-rl; font-size: {sz_mid}px; letter-spacing: 12px; height: 90%; display: flex; justify-content: center; align-items: center; font-weight: bold; }}
                .col-left-group {{ height: 90%; display: flex; gap: 15px; align-items: flex-end; }}
                .col-kwan {{ writing-mode: vertical-rl; font-size: {sz_kwan}px; letter-spacing: 4px; }}
                .col-lower {{ writing-mode: vertical-rl; font-size: {sz_lower}px; letter-spacing: 4px; }}
                @media print {{
                    body * {{ visibility: hidden; }}
                    .a4-page, .a4-page * {{ visibility: visible; }}
                    .a4-page {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; width: 210mm; height: 297mm; }}
                }}
                </style>
                <div class="a4-page">
                    <div class="col-left-group">
                        <div class="col-kwan"><span>{kwan_text}</span></div>
                        <div class="col-lower"><span>{sender_name}</span></div>
                        <div class="col-lower"><span>{sender_company}</span></div>
                    </div>
                    <div class="col-center"><span>{mid_text}</span></div>
                    <div class="col-right"><span>{upper_text}</span></div>
                </div>
                """
      else:  # 橫式排版 (如圖片風格：上中下，敬輓在名字下方)
        a4_html = f"""
                <style>
                .a4-page-h {{
                    width: 210mm;
                    height: 297mm;
                    padding: 30mm 25mm;
                    margin: auto;
                    border: 2px dashed #bbb;
                    {bg_css}
                    font-family: "DFKai-SB", "BiauKai", "標楷體", "KaiTi", serif;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    box-sizing: border-box;
                    box-shadow: 0 0 15px rgba(0,0,0,0.1);
                    color: #000;
                }}
                .row-upper {{ font-size: {sz_upper}px; letter-spacing: 4px; text-align: left; }}
                .row-center {{ font-size: {sz_mid}px; font-weight: bold; letter-spacing: 12px; text-align: center; margin: auto 0; }}
                .row-bottom-area {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                }}
                .row-lower-left {{ font-size: {sz_lower}px; letter-spacing: 4px; }}
                .row-lower-right {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    font-size: {sz_lower}px;
                    letter-spacing: 4px;
                }}
                @media print {{
                    body * {{ visibility: hidden; }}
                    .a4-page-h, .a4-page-h * {{ visibility: visible; }}
                    .a4-page-h {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; width: 210mm; height: 297mm; }}
                }}
                </style>
                <div class="a4-page-h">
                    <div class="row-upper"><span>{upper_text}</span></div>
                    <div class="row-center"><span>{mid_text}</span></div>
                    <div class="row-bottom-area">
                        <div class="row-lower-left"><span>{sender_company}</span></div>
                        <div class="row-lower-right">
                            <div style="font-size: {sz_lower}px; letter-spacing: 4px;">{sender_name}</div>
                            <div style="font-size: {sz_kwan}px; letter-spacing: 4px; margin-top: 8px;">{kwan_text}</div>
                        </div>
                    </div>
                </div>
                """

      st.markdown(a4_html, unsafe_allow_html=True)

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
                font-family: "DFKai-SB", "BiauKai", "標楷體", serif;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-sizing: border-box;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                color: #222;
            }}
            .joy-title {{ font-size: 32px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 15px; }}
            .joy-body {{ font-size: 40px; line-height: 2.2; flex-grow: 1; display: flex; align-items: center; justify-content: center; text-align: center; white-space: pre-wrap; }}
            .joy-footer {{ font-size: 28px; text-align: right; border-top: 1.5px solid #ddd; padding-top: 20px; }}
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
        "💡 提示：按下 **Ctrl + P** 列印，將紙張大小設定為 **A4**、方向選擇直式或橫式，即可完美印出！"
    )
