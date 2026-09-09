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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🌸 1. 蘭花品種資料庫",
            "👥 2. 客戶資料庫",
            "📦 3. 進貨與庫存管理",
            "🔄 4. 退貨管理區",
            "💰 5. 訂單與帳務管理",
            "🖨️ 6. A4 輓聯與卡片",
        ]
    )

    # -----------------------------------------
    # TAB 1: 蘭花品種資料庫
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
        st.subheader("📋 現有蘭花資料庫總覽與修改/刪除")
        df_db = get_data("蘭花資料庫")
        if not df_db.empty:
            st.dataframe(df_db, use_container_width=True)

            db_ids = df_db[df_db.columns[0]].astype(str).tolist()
            selected_db_id = st.selectbox(
                "選擇要修改或刪除的品種編號", db_ids, key="sel_db_mod"
            )

            selected_db_row = df_db[
                df_db[df_db.columns[0]].astype(str) == selected_db_id
            ]
            if not selected_db_row.empty:
                r_vals = selected_db_row.iloc[0].tolist()
                cur_name = r_vals[1] if len(r_vals) > 1 else ""
                cur_note = r_vals[2] if len(r_vals) > 2 else ""
                cur_photo = r_vals[3] if len(r_vals) > 3 else ""

                with st.form("update_db_form"):
                    upd_db_name = st.text_input("修改品種名稱", value=cur_name)
                    upd_db_note = st.text_input("修改品種特色說明", value=cur_note)
                    upd_db_file = st.file_uploader(
                        "📷 重新上傳品種標準照片 (若不換則留空)",
                        type=["jpg", "jpeg", "png"],
                        key="upd_db_file",
                    )

                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        submitted_upd_db = st.form_submit_button("確認修改品種資料")
                    with col_u2:
                        submitted_del_db = st.form_submit_button("🗑️ 刪除此品種")

                    if submitted_upd_db:
                        img_path = cur_photo
                        if upd_db_file is not None:
                            file_ext = upd_db_file.name.split(".")[-1]
                            img_filename = f"{selected_db_id}_{datetime.datetime.now().strftime('%H%M%S')}.{file_ext}"
                            img_path = os.path.join("photos", img_filename)
                            with open(img_path, "wb") as f:
                                f.write(upd_db_file.getbuffer())
                        new_row_db = [selected_db_id, upd_db_name, upd_db_note, img_path]
                        if update_data("蘭花資料庫", selected_db_id, new_row_db):
                            st.success(f"品種編號 {selected_db_id} 修改成功！")
                            st.rerun()

                    if submitted_del_db:
                        if delete_data("蘭花資料庫", selected_db_id):
                            st.success(f"品種編號 {selected_db_id} 刪除成功！")
                            st.rerun()

            st.markdown("---")
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
    # TAB 2: 客戶資料庫
    # -----------------------------------------
    with tab2:
        st.header("👥 客戶資料庫管理 (批發商與花店)")
        st.markdown(
            "在此建立批發商與花店的客戶資料，方便後續訂單與退貨管理直接點選。"
        )

        with st.form("cust_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                cust_id = st.text_input("客戶編號", value=get_next_id("CUST", "客戶資料庫"))
                cust_name = st.text_input("客戶 / 店鋪名稱 (例如: 大吉花店、宏達批發)")
            with c_col2:
                cust_type = st.selectbox("客戶類別", ["批發商", "花店", "其他"])
                cust_phone = st.text_input("聯絡電話 / 備註", value="0912-345678")
                cust_line = st.text_input("Line 名稱", value="")

            cust_submitted = st.form_submit_button("儲存客戶資料")
            if cust_submitted:
                row_cust = [cust_id, cust_name, cust_type, cust_phone, cust_line]
                if append_data("客戶資料庫", row_cust):
                    st.success(f"成功新增客戶「{cust_name}」！")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 現有客戶清單與修改/刪除")
        df_cust = get_data("客戶資料庫")
        if not df_cust.empty:
            st.dataframe(df_cust, use_container_width=True)

            cust_ids = df_cust[df_cust.columns[0]].astype(str).tolist()
            selected_cust_id = st.selectbox(
                "選擇要修改或刪除的客戶編號", cust_ids, key="sel_cust_mod"
            )

            selected_cust_row = df_cust[
                df_cust[df_cust.columns[0]].astype(str) == selected_cust_id
            ]
            if not selected_cust_row.empty:
                r_c_vals = selected_cust_row.iloc[0].tolist()
                c_name = r_c_vals[1] if len(r_c_vals) > 1 else ""
                c_type = r_c_vals[2] if len(r_c_vals) > 2 else "批發商"
                c_phone = r_c_vals[3] if len(r_c_vals) > 3 else ""
                c_line = r_c_vals[4] if len(r_c_vals) > 4 else ""

                types_list = ["批發商", "花店", "其他"]
                default_type_idx = (
                    types_list.index(c_type) if c_type in types_list else 0
                )

                with st.form("update_cust_form"):
                    upd_c_name = st.text_input("修改客戶 / 店鋪名稱", value=c_name)
                    upd_c_type = st.selectbox(
                        "修改客戶類別", types_list, index=default_type_idx
                    )
                    upd_c_phone = st.text_input("修改聯絡電話 / 備註", value=c_phone)
                    upd_c_line = st.text_input("修改 Line 名稱", value=c_line)

                    col_uc1, col_uc2 = st.columns(2)
                    with col_uc1:
                        sub_upd_cust = st.form_submit_button("確認修改客戶資料")
                    with col_uc2:
                        sub_del_cust = st.form_submit_button("🗑️ 刪除此客戶")

                    if sub_upd_cust:
                        new_row_cust = [
                            selected_cust_id,
                            upd_c_name,
                            upd_c_type,
                            upd_c_phone,
                            upd_c_line,
                        ]
                        if update_data("客戶資料庫", selected_cust_id, new_row_cust):
                            st.success(f"客戶編號 {selected_cust_id} 修改成功！")
                            st.rerun()
                    if sub_del_cust:
                        if delete_data("客戶資料庫", selected_cust_id):
                            st.success(f"已成功刪除客戶編號：{selected_cust_id}")
                            st.rerun()
        else:
            st.info("目前尚無客戶資料。")

    # -----------------------------------------
    # TAB 3: 進貨與庫存管理
    # -----------------------------------------
    with tab3:
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
        st.subheader("📦 現有進貨清單與照片預覽")
        df_inv = get_data("進貨表")
        if not df_inv.empty:
            st.dataframe(df_inv, use_container_width=True)

            photo_lookup = {}
            if not df_db.empty and "品種名稱" in df_db.columns and "相片路徑" in df_db.columns:
                for _, r in df_db.iterrows():
                    photo_lookup[str(r["品種名稱"])] = r["相片路徑"]

            st.markdown("#### 🖼️ 各進貨品項對應照片檢視")
            for _, row in df_inv.iterrows():
                item_n = row.get("品項名稱/品種", "")
                img_path = photo_lookup.get(str(item_n), "")
                c1, c2 = st.columns([1, 4])
                with c1:
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, width=100)
                    else:
                        st.caption("無對應資料庫照片")
                with c2:
                    st.write(
                        f"**編號**: {row.get('項目編號', '')} | **類別**: {row.get('類別', '')} | **品種**: {item_n}"
                    )
                    st.write(
                        f"**數量**: {row.get('數量', '')} | **成本**: {row.get('總成本/金額', '')} | **日期**: {row.get('進貨日期', '')}"
                    )
                st.divider()

            inv_ids = df_inv[df_inv.columns[0]].astype(str).tolist()
            selected_inv_id = st.selectbox("選擇要刪除的進貨項目編號", inv_ids, key="del_inv")
            if st.button("🗑️ 刪除此筆進貨紀錄"):
                if delete_data("進貨表", selected_inv_id):
                    st.success(f"已成功刪除編號：{selected_inv_id}")
                    st.rerun()
        else:
            st.info("目前尚無進貨資料。")

    # -----------------------------------------
    # TAB 4: 退貨管理區
    # -----------------------------------------
    with tab4:
        st.header("🔄 退貨與不良品管理區")

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

        df_cust_chk = get_data("客戶資料庫")
        cust_names_list = (
            df_cust_chk["客戶名稱"].tolist()
            if not df_cust_chk.empty and "客戶名稱" in df_cust_chk.columns
            else []
        )

        with st.form("return_form"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                ret_id = st.text_input("退貨編號", value=get_next_id("RET", "退貨表"))
                ret_type = st.selectbox(
                    "退貨類型選擇",
                    [
                        "1. 我們向花農退貨 (退給供應商)",
                        "2. 批發商向我們退貨 (客戶退回)",
                    ],
                )

                party_mode = st.radio(
                    "對象名稱輸入方式", ["從客戶資料庫選取", "自行輸入"], horizontal=True
                )
                if party_mode == "從客戶資料庫選取" and cust_names_list:
                    party_name = st.selectbox("選擇客戶/花店", cust_names_list)
                else:
                    party_name = st.text_input("自行輸入對象名稱 (花農/批發商)", value="某某花農")

            with col_r2:
                target_item = st.selectbox(
                    "關聯進貨批次/品項",
                    inv_items_list if inv_items_list else ["無可用項目"],
                )
                bad_qty = st.number_input("退貨/不良株數 (棵)", min_value=1, value=2)
                unit_price = st.number_input(
                    "每棵單價 / 成本 (元)", min_value=0.0, value=150.0
                )
                ret_date = st.date_input("處理日期", datetime.date.today())
                reason = st.text_input("退貨原因說明", value="運送碰撞 / 開花不良")

            total_return_amount = float(bad_qty) * float(unit_price)
            st.info(
                f"💡 系統計算總金額：**{total_return_amount} 元** ({bad_qty}棵 ×"
                f" {unit_price}元)"
            )

            ret_submitted = st.form_submit_button("確認送出退貨紀錄")
            if ret_submitted:
                row_ret = [
                    ret_id,
                    ret_type,
                    party_name,
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

        st.subheader("📋 現有退貨紀錄清單與修改/刪除")
        df_ret = get_data("退貨表")
        if not df_ret.empty:
            st.dataframe(df_ret, use_container_width=True)

            ret_ids = df_ret[df_ret.columns[0]].astype(str).tolist()
            selected_ret_id = st.selectbox(
                "選擇要修改或刪除的退貨編號", ret_ids, key="sel_ret_mod"
            )

            sel_ret_row = df_ret[
                df_ret[df_ret.columns[0]].astype(str) == selected_ret_id
            ]
            if not sel_ret_row.empty:
                r_vals = sel_ret_row.iloc[0].tolist()
                r_type = r_vals[1] if len(r_vals) > 1 else ""
                p_name = r_vals[2] if len(r_vals) > 2 else ""
                t_item = r_vals[3] if len(r_vals) > 3 else ""
                b_qty = (
                    int(r_vals[4])
                    if len(r_vals) > 4 and str(r_vals[4]).isdigit()
                    else 1
                )
                u_price = (
                    float(r_vals[5])
                    if len(r_vals) > 5 and str(r_vals[5]).replace(".", "", 1).isdigit()
                    else 0.0
                )
                r_date_str = r_vals[7] if len(r_vals) > 7 else str(datetime.date.today())
                r_reason = r_vals[8] if len(r_vals) > 8 else ""

                try:
                    parsed_ret_date = datetime.datetime.strptime(
                        r_date_str, "%Y-%m-%d"
                    ).date()
                except:
                    parsed_ret_date = datetime.date.today()

                ret_types_list = [
                    "1. 我們向花農退貨 (退給供應商)",
                    "2. 批發商向我們退貨 (客戶退回)",
                ]
                d_r_type_idx = (
                    ret_types_list.index(r_type) if r_type in ret_types_list else 0
                )

                with st.form("update_ret_form"):
                    upd_ret_type = st.selectbox(
                        "修改退貨類型選擇", ret_types_list, index=d_r_type_idx
                    )
                    upd_party_name = st.text_input("修改對象名稱", value=p_name)
                    upd_target_item = st.text_input("修改關聯進貨品項/批次", value=t_item)
                    upd_bad_qty = st.number_input(
                        "修改退貨/不良株數 (棵)", min_value=1, value=b_qty
                    )
                    upd_unit_price = st.number_input(
                        "修改每棵單價 / 成本 (元)", min_value=0.0, value=u_price
                    )
                    upd_ret_date = st.date_input("修改處理日期", value=parsed_ret_date)
                    upd_reason = st.text_input("修改退貨原因說明", value=r_reason)

                    upd_tot_amt = float(upd_bad_qty) * float(upd_unit_price)
                    st.info(f"💡 系統重新計算總金額：**{upd_tot_amt} 元**")

                    col_ur1, col_ur2 = st.columns(2)
                    with col_ur1:
                        sub_upd_ret = st.form_submit_button("確認修改退貨紀錄")
                    with col_ur2:
                        sub_del_ret = st.form_submit_button("🗑️ 刪除此退貨紀錄")

                    if sub_upd_ret:
                        new_row_ret = [
                            selected_ret_id,
                            upd_ret_type,
                            upd_party_name,
                            upd_target_item,
                            int(upd_bad_qty),
                            float(upd_unit_price),
                            float(upd_tot_amt),
                            str(upd_ret_date),
                            upd_reason,
                        ]
                        if update_data("退貨表", selected_ret_id, new_row_ret):
                            st.success(f"退貨編號 {selected_ret_id} 修改成功！")
                            st.rerun()
                    if sub_del_ret:
                        if delete_data("退貨表", selected_ret_id):
                            st.success(f"已刪除退貨編號：{selected_ret_id}")
                            st.rerun()
        else:
            st.info("目前尚無退貨紀錄。")

    # -----------------------------------------
    # TAB 5: 訂單與帳務管理
    # -----------------------------------------
    with tab5:
        st.header("💰 訂單登錄與帳務管理（支援單筆完整修改、結帳與對帳列印）")

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
                    "未結",
                ]
                if append_data("訂單表", row):
                    st.success("成功新增訂單紀錄！")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 訂單總覽與修改 / 狀態更新 / 刪除")
        df_order = get_data("訂單表")
        if not df_order.empty:
            st.dataframe(df_order, use_container_width=True)
            order_ids_list = df_order["訂單編號"].astype(str).tolist()

            col_o1, col_o2 = st.columns(2)
            with col_o1:
                st.subheader("📝 修改指定訂單內容與狀態")
                selected_upd_id = st.selectbox(
                    "選擇要修改的訂單編號", order_ids_list, key="sel_ord_mod"
                )

                matched_row = df_order[
                    df_order["訂單編號"].astype(str) == selected_upd_id
                ]
                if not matched_row.empty:
                    r_vals = matched_row.iloc[0].tolist()
                    o_cust_type = r_vals[1] if len(r_vals) > 1 else "個人"
                    o_customer = r_vals[2] if len(r_vals) > 2 else ""
                    o_spec = r_vals[3] if len(r_vals) > 3 else ""
                    o_pot = r_vals[4] if len(r_vals) > 4 else "無盆"
                    o_delivery = r_vals[5] if len(r_vals) > 5 else "自載"
                    o_term = r_vals[6] if len(r_vals) > 6 else "每單結"
                    o_cost = (
                        float(r_vals[7])
                        if len(r_vals) > 7
                        and str(r_vals[7]).replace(".", "", 1).isdigit()
                        else 0.0
                    )
                    o_price = (
                        float(r_vals[8])
                        if len(r_vals) > 8
                        and str(r_vals[8]).replace(".", "", 1).isdigit()
                        else 0.0
                    )

                    o_date_str = (
                        r_vals[9] if len(r_vals) > 9 else str(datetime.date.today())
                    )
                    o_exp_str = (
                        r_vals[10] if len(r_vals) > 10 else str(datetime.date.today())
                    )
                    o_shipped = r_vals[11] if len(r_vals) > 11 else "未出貨"
                    o_payment = r_vals[12] if len(r_vals) > 12 else "未結"

                    try:
                        p_o_date = datetime.datetime.strptime(o_date_str, "%Y-%m-%d").date()
                    except:
                        p_o_date = datetime.date.today()
                    try:
                        p_e_date = datetime.datetime.strptime(o_exp_str, "%Y-%m-%d").date()
                    except:
                        p_e_date = datetime.date.today()

                    cust_types = ["批發", "花店", "個人"]
                    d_ctype_idx = (
                        cust_types.index(o_cust_type) if o_cust_type in cust_types else 2
                    )
                    shipped_opts = ["未出貨", "已出貨"]
                    d_ship_idx = (
                        shipped_opts.index(o_shipped) if o_shipped in shipped_opts else 0
                    )
                    payment_opts = ["未結", "已結"]
                    d_pay_idx = (
                        payment_opts.index(o_payment) if o_payment in payment_opts else 0
                    )

                    with st.form("update_order_full_form"):
                        upd_c_type = st.selectbox(
                            "修改客戶類型", cust_types, index=d_ctype_idx
                        )
                        upd_customer = st.text_input("修改訂購人/批發商名稱", value=o_customer)
                        upd_spec = st.text_input("修改品項與規格", value=o_spec)
                        upd_pot = st.text_input("修改盆器", value=o_pot)
                        upd_delivery = st.text_input("修改配送方式", value=o_delivery)
                        upd_term = st.text_input("修改結帳方式", value=o_term)
                        upd_cost = st.number_input(
                            "修改預估總成本 (元)", min_value=0.0, value=o_cost
                        )
                        upd_price = st.number_input(
                            "修改售價/金額 (元)", min_value=0.0, value=o_price
                        )
                        upd_o_date = st.date_input("修改下單日期", value=p_o_date)
                        upd_e_date = st.date_input("修改預計出貨日期", value=p_e_date)
                        upd_shipped = st.selectbox(
                            "修改出貨狀態", shipped_opts, index=d_ship_idx
                        )
                        upd_payment = st.selectbox(
                            "修改付款狀態", payment_opts, index=d_pay_idx
                        )

                        submitted_upd_ord = st.form_submit_button("確認更新此訂單")
                        if submitted_upd_ord:
                            updated_row_data = [
                                selected_upd_id,
                                upd_c_type,
                                upd_customer,
                                upd_spec,
                                upd_pot,
                                upd_delivery,
                                upd_term,
                                float(upd_cost),
                                float(upd_price),
                                str(upd_o_date),
                                str(upd_e_date),
                                upd_shipped,
                                upd_payment,
                            ]
                            if update_data("訂單表", selected_upd_id, updated_row_data):
                                st.success(f"訂單編號 {selected_upd_id} 修改成功！")
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
                            st.success(f"已成功刪除訂單編號：{selected_del_id}")
                            st.rerun()
        else:
            st.info("目前尚無訂單資料。")

    # -----------------------------------------
    # TAB 6: A4 輓聯與卡片 (升級版)
    # -----------------------------------------
    with tab6:
        st.header("🖨️ 6. A4 輓聯與開幕賀卡排版系統")
        st.markdown("在此可製作標準 A4 尺寸的輓聯或開幕卡片，支援直式、橫式排版與完整預設詞庫選項。")

        card_purpose = st.radio(
            "卡片類型選擇", ["輓聯 (喪禮/悼念)", "慶/開幕 (賀卡/開幕)"], horizontal=True
        )
        layout_style = st.radio(
            "排版方向選擇", ["直式 (傳統直排)", "橫式 (標準橫排)"], horizontal=True
        )

        st.markdown("---")

        if card_purpose == "輓聯 (喪禮/悼念)":
            st.subheader("🕊️ 輓聯細節設定")

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                funeral_gender = st.selectbox("逝者性別", ["男", "女"])
            with col_g2:
                if funeral_gender == "女":
                    age_category = st.selectbox(
                        "女逝者年齡/身份別 (選取後自動對應中款選項)",
                        [
                            "少女、年輕女性 (49歲以下 / 未婚)",
                            "中壯年女性 (50至79歲)",
                            "高齡女性 (80歲以上)",
                            "自訂中款",
                        ],
                    )
                else:
                    age_category = st.selectbox(
                        "男逝者年齡/身份別 (選取後自動對應中款選項)",
                        [
                            "49歲以下 (年輕、早逝)",
                            "50至69歲 (壯年至中老年)",
                            "70至79歲 (古稀)",
                            "80歲以上 (高壽、期頤)",
                            "自訂中款",
                        ],
                    )

            # 對應中款選項清單
            if funeral_gender == "女":
                if "49歲以下" in age_category:
                    mid_options = [
                        "遽促芳齡",
                        "玉殞香消",
                        "芳華早謝",
                        "蘭摧蕙折",
                        "妝台月冷",
                    ]
                elif "50至79" in age_category:
                    mid_options = [
                        "淑德永昭",
                        "懿範長存",
                        "慈容永念",
                        "德業長昭",
                        "巾幗模範",
                    ]
                elif "80歲以上" in age_category:
                    mid_options = [
                        "萱範長存",
                        "母儀千古",
                        "駕返瑤池",
                        "萱蔭長留",
                        "壺範垂型",
                    ]
                else:
                    mid_options = ["自訂"]
            else:
                if "49歲以下" in age_category:
                    mid_options = [
                        "星隕少微",
                        "玉樹長埋",
                        "壯志未酬",
                        "天不假年",
                        "長才未盡",
                        "玉折蘭摧",
                    ]
                elif "50至69" in age_category:
                    mid_options = [
                        "棟折梁摧",
                        "典則空留",
                        "英氣頓杳",
                        "德望昭然",
                        "風範長存",
                    ]
                elif "70至79" in age_category:
                    mid_options = [
                        "哲人其萎",
                        "斗柄西移",
                        "德業長昭",
                        "典范長存",
                    ]
                elif "80歲以上" in age_category:
                    mid_options = [
                        "德高望重",
                        "魯般圮毀",
                        "仁者壽",
                        "德望永昭",
                    ]
                else:
                    mid_options = ["自訂"]

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                default_upper = (
                    "敬悼 X公X先生 千古"
                    if funeral_gender == "男"
                    else "敬悼 X媽X夫人 仙逝"
                )
                upper_text = st.text_input(
                    "【右側上款】 (例如: 敬悼 X公X先生 千古 / 敬悼 X媽X夫人 仙逝)", value=default_upper
                )
            with col_u2:
                if "自訂" in mid_options or mid_options == ["自訂"]:
                    middle_text = st.text_input(
                        "【中間中款】輓辭 (可自行打字)", value=""
                    )
                else:
                    sel_mid = st.selectbox("選擇預設中款輓辭", mid_options)
                    middle_text = st.text_input(
                        "【中間中款】輓辭 (可選擇或直接修改)", value=sel_mid
                    )

            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                lower_company = st.text_input("【下款】公司/單位名稱 (選填)", value="")
            with col_l2:
                lower_name = st.text_input("【下款】名字位置", value="某某某")
            with col_l3:
                lower_suffix = st.selectbox("【左下角】署名結尾", ["敬輓", "泣輓", "泐輓"])

            if lower_company:
                lower_text = f"{lower_company} {lower_name} {lower_suffix}"
            else:
                lower_text = f"{lower_name} {lower_suffix}"

        else:
            st.subheader("🎉 慶祝 / 開幕賀卡細節設定")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                upper_text = st.text_input(
                    "【上款】祝賀對象", value="恭祝 鴻海科技集團 新廠落成"
                )
                opening_mids = [
                    "鴻圖大展",
                    "駿業宏開",
                    "生意興隆",
                    "財源廣進",
                    "大業千秋",
                ]
                sel_op_mid = st.selectbox("選擇預設開幕賀詞", opening_mids)
                middle_text = st.text_input(
                    "【中款】賀詞內容 (可直接修改)", value=sel_op_mid
                )
            with col_c2:
                lower_company = st.text_input("【下款】公司/單位名稱", value="大吉花店")
                lower_suffix = st.selectbox("【下款】敬獻方式", ["敬賀", "敬獻"])
                lower_text = f"{lower_company} {lower_suffix}"

        generate_btn = st.button("🖨️ 產生 A4 列印預覽")

        if generate_btn:
            st.markdown("---")
            st.subheader("🖨️ A4 排版預覽效果")

            if "直式" in layout_style:
                # 直式排版 (傳統直書，右至左排列)
                card_html = f"""
                <div style="border: 2px dashed #bbb; padding: 40px; width: 100%; max-width: 650px; height: 550px; margin: 0 auto; background-color: #fff; color: #000; font-family: 'DFKai-SB', 'BiauKai', 'Microsoft JhengHei', serif; display: flex; justify-content: space-around; align-items: center; writing-mode: vertical-rl; text-orientation: upright; letter-spacing: 5px;">
                    <div style="font-size: 20px; font-weight: bold; margin-top: 20px;">{lower_text}</div>
                    <div style="font-size: 32px; font-weight: bold; margin: 0 25px;">{middle_text}</div>
                    <div style="font-size: 20px; font-weight: bold; margin-bottom: 20px;">{upper_text}</div>
                </div>
                """
            else:
                # 橫式排版
                card_html = f"""
                <div style="border: 2px dashed #bbb; padding: 40px; width: 100%; max-width: 700px; margin: 0 auto; background-color: #fff; color: #000; font-family: 'DFKai-SB', 'BiauKai', 'Microsoft JhengHei', sans-serif; text-align: center;">
                    <h3 style="letter-spacing: 5px; margin-bottom: 20px;">{upper_text}</h3>
                    <hr style="width: 50%; margin: 20px auto;">
                    <h1 style="font-size: 34px; letter-spacing: 8px; margin: 40px 0; line-height: 1.5;">{middle_text}</h1>
                    <hr style="width: 50%; margin: 20px auto;">
                    <h3 style="letter-spacing: 5px; margin-top: 30px; text-align: right; padding-right: 50px;">{lower_text}</h3>
                </div>
                """

            st.markdown(card_html, unsafe_allow_html=True)
            st.info("💡 提示：您可以直接按下瀏覽器的列印快速鍵（Ctrl + P 或 Cmd + P），即可將此畫面輸出為 A4 實體輓聯或賀卡。")
