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
  tab1, tab2, tab3, tab4, tab5 = st.tabs(
      [
          "🌸 1. 蘭花品種資料庫",
          "📦 2. 進貨與庫存管理",
          "🔄 3. 退貨管理區",
          "💰 4. 訂單與帳務管理",
          "🖨️ 5. A4 橫式輓聯與卡片",
      ]
  )

  # -----------------------------------------
  # TAB 1: 蘭花資料庫
  # -----------------------------------------
  with tab1:
    st.header("🌸 蘭花品種寫入與資料庫管理")
    st.markdown("請先在此建立各種蘭花品種檔案與照片，後續進貨時可直接選取。")

    with st.form("db_form"):
      col_d1, col_d2 = st.columns(2)
      with col_d1:
        db_id = st.text_input("品種編號", value=get_next_id("DB", "蘭花資料庫"))
        db_name = st.text_input("蘭花品種名稱 (例如: 大辣椒、V3)")
      with col_d2:
        db_note = st.text_input("品種特色說明", value="標準優良品種")
        db_file = st.file_uploader(
            "📷 上傳品種標準照片", type=["jpg", "jpeg", "png"]
        )

      db_submitted = st.form_submit_button("儲存至蘭花資料庫")
      if db_submitted:
        img_path = ""
        if db_file is not None:
          file_ext = db_file.name.split(".")[-1]
          img_filename = f"{db_id}_{datetime.datetime.now().strftime('%H%M%S')}.{file_ext}"
          img_path = os.path.join("photos", img_filename)
          with open(img_path, "wb") as f:
            f.write(db_file.getbuffer())

        row_db = [db_id, db_name, db_note, img_path]
        if append_data("蘭花資料庫", row_db):
          st.success(f"成功將品種「{db_name}」加入資料庫！")
          st.rerun()

    st.markdown("---")
    st.subheader("📋 現有蘭花資料庫總覽")
    df_db = get_data("蘭花資料庫")
    if not df_db.empty:
      st.dataframe(df_db, use_container_width=True)

      # 顯示圖片預覽
      for index, row in df_db.iterrows():
        cols = st.columns([1, 3])
        with cols[0]:
          img_p = row.get("相片路徑", "")
          if img_p and os.path.exists(img_p):
            st.image(img_p, width=120)
          else:
            st.info("無相片")
        with cols[1]:
          st.markdown(
              f"**品種編號**: {row.get('品種編號', '')}  \n**品種名稱**: {row.get('品種名稱', '')}  \n**特色說明**: {row.get('品種特色說明', '')}"
          )
        st.markdown("---")
    else:
      st.info("目前資料庫尚無品種資料。")

  # -----------------------------------------
  # TAB 2: 進貨與庫存管理
  # -----------------------------------------
  with tab2:
    st.header("📦 新增進貨與庫存管理")

    df_db = get_data("蘭花資料庫")
    db_names_list = (
        df_db["品種名稱"].tolist()
        if not df_db.empty and "品種名稱" in df_db.columns
        else []
    )

    category = st.selectbox("選擇進貨類別", ["蘭花", "陶瓷盆"])

    if category == "蘭花":
      with st.form("flower_form"):
        col1, col2 = st.columns(2)
        with col1:
          item_id = st.text_input(
              "項目編號", value=get_next_id("FL", "進貨表")
          )
          input_mode = st.radio("品種選擇方式", ["從資料庫選取", "自行輸入"], horizontal=True)
          if input_mode == "從資料庫選取" and db_names_list:
            flower_name = st.selectbox("選擇資料庫品種", db_names_list)
          else:
            flower_name = st.text_input("自行輸入品種名稱")

          spike_type = st.selectbox("梗數規格", ["單梗", "雙梗", "多梗"])
          color = st.selectbox("花朵顏色", ["白", "紅", "粉", "黃", "其他"])
        with col2:
          size = st.selectbox("花朵大小", ["大", "中", "小"])
          height = st.selectbox("株高規格", ["高", "中", "矮"])
          qty = st.number_input("進貨數量 (棵數)", min_value=1, value=10)
          cost = st.number_input("總進貨成本 (元)", min_value=0.0, value=1000.0)
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
                  "落地盆-喪 (100)",
                  "落地盆-喜 (200)",
                  "羅馬盆 (280)",
              ],
          )
        with col2:
          qty = st.number_input("進貨數量", min_value=1, value=10)
          date = st.date_input("進貨日期", datetime.date.today())

        cost_map = {
            "桌上盆 (成本100)": 100,
            "落地盆-喪 (100)": 100,
            "落地盆-喜 (200)": 200,
            "羅馬盆 (280)": 280,
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
    st.subheader("📦 現有進貨清單與管理")
    df_inv = get_data("進貨表")
    if not df_inv.empty:
      st.dataframe(df_inv, use_container_width=True)
      inv_ids = df_inv[df_inv.columns[0]].astype(str).tolist()
      selected_inv_id = st.selectbox("選擇要刪除的進貨項目編號", inv_ids, key="del_inv")
      if st.button("🗑️ 刪除此筆進貨紀錄"):
        if delete_data("進貨表", selected_inv_id):
          st.success(f"已成功刪除編號：{selected_inv_id}")
          st.rerun()
    else:
      st.info("目前尚無進貨資料。")

  # -----------------------------------------
  # TAB 3: 退貨管理區
  # -----------------------------------------
  with tab3:
    st.header("🔄 退貨與不良品管理區")
    st.markdown(
        "可處理**進貨不良退貨（向花農退貨）**或**批發客戶退貨**，皆以【棵數 ×"
        " 每棵單價】計算總退款金額。"
    )

    df_inv_chk = get_data("進貨表")
    inv_items_list = (
        (
            df_inv_chk["項目編號"].astype(str)
            + " - "
            + df_inv_chk["品項名稱/品種"]
        ).tolist()
        if not df_inv_chk.empty and "項目編號" in df_inv_chk.columns
        else []
    )

    with st.form("return_form"):
      col_r1, col_r2 = st.columns(2)
      with col_r1:
        ret_id = st.text_input("退貨編號", value=get_next_id("RET", "退貨表"))
        ret_type = st.selectbox(
            "退貨類型",
            [
                "進貨不良退貨 (向花農退貨)",
                "批發客戶退貨 (客戶退回批發批次)",
            ],
        )
        target_item = st.selectbox(
            "關聯進貨批次/品項",
            inv_items_list if inv_items_list else ["無可用項目"],
        )
      with col_r2:
        bad_qty = st.number_input("不良/退貨株數 (棵)", min_value=1, value=2)
        unit_price = st.number_input(
            "每棵單價 / 成本 (元)", min_value=0.0, value=150.0
        )
        ret_date = st.date_input("處理日期", datetime.date.today())
        reason = st.text_input("退貨原因說明", value="運送碰撞 / 開花不良")

      total_return_amount = float(bad_qty) * float(unit_price)
      st.info(
          f"💡 系統計算總退貨金額：**{total_return_amount} 元** ({bad_qty}棵 ×"
          f" {unit_price}元)"
      )

      ret_submitted = st.form_submit_button("確認送出退貨紀錄")
      if ret_submitted:
        row_ret = [
            ret_id,
            ret_type,
            target_item,
            int(bad_qty),
            float(unit_price),
            float(total_return_amount),
            str(ret_date),
            reason,
        ]
        if append_data("退貨表", row_ret):
          st.success("成功記錄退貨資料！")
          st.rerun()

    st.subheader("📋 現有退貨紀錄清單")
    df_ret = get_data("退貨表")
    if not df_ret.empty:
      st.dataframe(df_ret, use_container_width=True)
      ret_ids = df_ret[df_ret.columns[0]].astype(str).tolist()
      selected_ret_id = st.selectbox("選擇要刪除的退貨編號", ret_ids, key="del_ret")
      if st.button("🗑️ 刪除此筆退貨紀錄"):
        if delete_data("退貨表", selected_ret_id):
          st.success(f"已刪除退貨編號：{selected_ret_id}")
          st.rerun()
    else:
      st.info("目前尚無退貨紀錄。")

  # -----------------------------------------
  # TAB 4: 訂單與帳務管理
  # -----------------------------------------
  with tab4:
    st.header("💰 訂單登錄與帳務管理（支援批發與零售）")

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
        cust_type = st.selectbox("客戶類型", ["批發", "花店", "個人"])
        customer = st.text_input("訂購人 / 批發商名稱")
      with col2:
        if flower_list:
          orchid_used = st.selectbox("選擇使用蘭花", flower_list)
        else:
          orchid_used = st.text_input("使用蘭花名稱")

        if cust_type == "批發":
          batch_qty = st.number_input(
              "批發賣出總株數 (棵)", min_value=1, value=50
          )
          unit_sell_price = st.number_input(
              "每棵批發單價 (元)", min_value=0.0, value=250.0
          )
          pot_used = "批發免盆"
        else:
          stalks_count = st.slider("株數選擇", 3, 20, 10)
          unit_sell_price = st.number_input(
              "總售價 (元)", min_value=0.0, value=1500.0
          )
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
        cost_price = st.number_input("預估總成本 (元)", min_value=0.0, value=600.0)
        if cust_type == "批發":
          sell_price = float(batch_qty) * float(unit_sell_price)
          st.info(f"批發總金額自動計算：{sell_price} 元")
        else:
          sell_price = unit_sell_price

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
          item_spec_str = f"{orchid_used} | 批發 {batch_qty}棵 (單價{unit_sell_price}元)"
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

    st.subheader("📋 訂單與帳務總覽 (狀態更新與刪除)")
    df_order = get_data("訂單表")
    if not df_order.empty:
      st.dataframe(df_order, use_container_width=True)
      order_ids_list = df_order["訂單編號"].tolist()

      col_o1, col_o2 = st.columns(2)
      with col_o1:
        st.subheader("📝 更新訂單狀態")
        with st.form("update_status_form"):
          selected_upd_id = st.selectbox("選擇要修改的訂單編號", order_ids_list)
          new_shipped = st.selectbox("更新出貨狀態", ["未出貨", "已出貨"])
          new_payment = st.selectbox("更新付款狀態", ["未付款", "已付款"])
          update_submitted = st.form_submit_button("確認更新狀態")

          if update_submitted:
            matched_row = df_order[df_order["訂單編號"] == selected_upd_id]
            if not matched_row.empty:
              r_list = matched_row.values.tolist()[0]
              r_list[-2] = new_shipped
              r_list[-1] = new_payment
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

  # -----------------------------------------
  # TAB 5: A4 橫式輓聯與卡片
  # -----------------------------------------
  with tab5:
    st.header("🖨️ A4 橫式輓聯與卡片產生器 (標楷體)")
    st.markdown(
        "【敬輓】已嚴格設定在【名字正下方】垂直堆疊。你可以透過下方拉桿任意調整各區塊文字大小。"
    )

    card_mode = st.selectbox("選擇卡片類型", ["喪禮傳統輓聯", "喜慶 / 開幕賀卡"])

    if card_mode == "喪禮傳統輓聯":
      card_style_bg = st.selectbox(
          "卡片背景風格",
          ["典雅紫藍暈染風 (如範例圖)", "簡約純白底色"],
      )

      with st.expander("⚙️ 自由調整字體大小設定", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
          sz_upper = st.slider("上款字體大小", 30, 100, 50)
        with f_col2:
          sz_mid = st.slider("中款字體大小", 60, 200, 120)
        with f_col3:
          sz_lower = st.slider("下款/姓名字體大小", 30, 100, 50)
        with f_col4:
          sz_kwan = st.slider("敬輓字體大小", 30, 100, 45)

      col_r, col_m, col_l = st.columns(3)

      with col_r:
        st.markdown("**【上款設定】**")
        upper_text = st.text_input("輸入上款 (如: 敬悼)", value="敬悼")

      with col_m:
        st.markdown("**【中款 / 輓辭設定】**")
        mid_text = st.text_input("輸入中款輓辭 (如: 上品上生)", value="上品上生")

      with col_l:
        st.markdown("**【下款與敬輓設定】**")
        sender_company = st.text_input(
            "左下機關/公司 (例如: 臺北市政府)", value="臺北市政府"
        )
        sender_name = st.text_input(
            "右下落款名字 (例如: 王大明)", value="王大明"
        )
        kwan_text = st.text_input("敬輓字樣", value="敬輓")

      st.markdown("---")

      bg_css = (
          "background: linear-gradient(135deg, #e3e8f8 0%, #f3e6f8 100%);"
          if "紫藍暈染" in card_style_bg
          else "background: white;"
      )

      # A4 橫向：寬 297mm，高 210mm
      a4_landscape_html = f"""
            <style>
            .a4-landscape {{
                width: 297mm;
                height: 210mm;
                padding: 20mm 25mm;
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
            .row-center {{ font-size: {sz_mid}px; font-weight: bold; letter-spacing: 16px; text-align: center; margin: auto 0; }}
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
                @page {{ size: A4 landscape; }}
                body * {{ visibility: hidden; }}
                .a4-landscape, .a4-landscape * {{ visibility: visible; }}
                .a4-landscape {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; width: 297mm; height: 210mm; }}
            }}
            </style>
            <div class="a4-landscape">
                <div class="row-upper"><span>{upper_text}</span></div>
                <div class="row-center"><span>{mid_text}</span></div>
                <div class="row-bottom-area">
                    <div class="row-lower-left"><span>{sender_company}</span></div>
                    <div class="row-lower-right">
                        <div>{sender_name}</div>
                        <div style="font-size: {sz_kwan}px; margin-top: 6px;">{kwan_text}</div>
                    </div>
                </div>
            </div>
            """

      st.markdown(a4_landscape_html, unsafe_allow_html=True)

    else:
      st.markdown("### 🌸 喜慶 / 開幕賀卡設定")
      recipient_c = st.text_input("收花人 / 對象", value="大吉大利商行 啟")
      blessing_c = st.text_area("祝賀內文", value="祝 開張大吉 生意興隆 財源廣進")
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
                @page {{ size: A4 portrait; }}
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
        "💡 列印提示：按下 **Ctrl + P**，印表機紙張方向請選擇「**橫向 (Landscape)**」，即可完美列印出 A4 橫式輓聯！"
    )
