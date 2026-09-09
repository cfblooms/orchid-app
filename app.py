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
                            st.success(f"已成功刪除訂單：{selected_del_id}")
                            st.rerun()

            st.markdown("---")
            st.subheader("📄 未結訂單對帳單與列印")
            cols = df_order.columns.tolist()
            pay_col = "付款狀態" if "付款狀態" in cols else cols[-1]
            cust_col = (
                "訂購人 / 批發商名稱"
                if "訂購人 / 批發商名稱" in cols
                else (cols[2] if len(cols) > 2 else cols[1])
            )
            amt_col = None
            for c in cols:
                if "金額" in c or "售價" in c:
                    amt_col = c
                    break

            df_unpaid = df_order[df_order[pay_col] == "未結"]
            if not df_unpaid.empty:
                unpaid_customers = df_unpaid[cust_col].unique().tolist()
                selected_statement_cust = st.selectbox(
                    "🔍 選擇要列印未結對帳單的訂購人 / 批發商名稱", unpaid_customers
                )

                cust_unpaid_df = df_unpaid[df_unpaid[cust_col] == selected_statement_cust]

                st.markdown(f"#### 📋 【{selected_statement_cust}】未結訂單明細")
                st.dataframe(cust_unpaid_df, use_container_width=True)

                total_unpaid_amount = 0
                if amt_col:
                    total_unpaid_amount = pd.to_numeric(
                        cust_unpaid_df[amt_col], errors="coerce"
                    ).sum()
                    st.info(
                        f"💰 **{selected_statement_cust}** 目前累積未結總金額：**{total_unpaid_amount:,.0f} 元**"
                    )

                print_html = f"""
                    <style>
                    .statement-box {{
                        width: 210mm;
                        padding: 20mm;
                        margin: 20px auto;
                        background: white;
                        border: 2px dashed #999;
                        font-family: "DFKai-SB", "BiauKai", "標楷體", serif;
                        color: #000;
                        box-sizing: border-box;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .statement-title {{ text-align: center; font-size: 26px; font-weight: bold; margin-bottom: 25px; letter-spacing: 2px; }}
                    .statement-info {{ display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 16px; }}
                    .statement-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                    .statement-table th, .statement-table td {{ border: 1.5px solid #000; padding: 10px 12px; font-size: 15px; text-align: left; }}
                    .statement-table th {{ background-color: #f0f0f0; }}
                    .statement-footer {{ text-align: right; font-size: 18px; font-weight: bold; margin-top: 20px; letter-spacing: 1px; }}
                    @media print {{
                        @page {{ size: A4 portrait; margin: 10mm; }}
                        body * {{ visibility: hidden; }}
                        .statement-box, .statement-box * {{ visibility: visible; }}
                        .statement-box {{ position: absolute; left: 0; top: 0; border: none; width: 100%; margin: 0; padding: 10mm; box-shadow: none; }}
                    }}
                    </style>
                    <div class="statement-box">
                        <div class="statement-title">🌸 蘭花業務未結款項對帳單 🌸</div>
                        <div class="statement-info">
                            <div><strong>客戶 / 批發商名稱：</strong> {selected_statement_cust}</div>
                            <div><strong>製表日期：</strong> {datetime.date.today().strftime('%Y-%m-%d')}</div>
                        </div>
                        <table class="statement-table">
                            <thead>
                                <tr>
                                    <th>訂單編號</th>
                                    <th>品項與規格</th>
                                    <th>下單日期</th>
                                    <th>預計出貨</th>
                                    <th>金額 (元)</th>
                                </tr>
                            </thead>
                            <tbody>
                """
                for _, r in cust_unpaid_df.iterrows():
                    o_id = r.get("訂單編號", r.get(cols[0], "---"))
                    o_spec = r.get("品項規格", r.get(cols[3] if len(cols) > 3 else cols[1], "---"))
                    o_date = r.get("下單日期", r.get(cols[9] if len(cols) > 9 else "", "---"))
                    exp_date = r.get("預計出貨日期", r.get(cols[10] if len(cols) > 10 else "", "---"))
                    amt = r.get(amt_col, 0) if amt_col else 0

                    print_html += f"""
                                <tr>
                                    <td>{o_id}</td>
                                    <td>{o_spec}</td>
                                    <td>{o_date}</td>
                                    <td>{exp_date}</td>
                                    <td>{amt}</td>
                                </tr>
                            """

                print_html += f"""
                            </tbody>
                        </table>
                        <div class="statement-footer">
                            未結總計金額： NT$ {total_unpaid_amount:,.0f} 元
                        </div>
                    </div>
                """
                st.markdown(print_html, unsafe_allow_html=True)
                st.info("💡 列印提示：請按下 **Ctrl + P**，即可將上方預覽的「未結對帳單」列印輸出！")
            else:
                st.success("🎉 目前所有訂單皆已結清，沒有未結訂單！")
        else:
            st.info("目前尚無訂單資料。")

    # -----------------------------------------
    # TAB 6: A4 輓聯與卡片產生器 (已修復並補齊)
    # -----------------------------------------
    with tab6:
        st.header("🖨️ A4 輓聯與喜慶賀卡產生器")

        card_mode = st.selectbox(
            "選擇卡片類型",
            [
                "喪禮傳統輓聯 (直式 / 橫式)",
                "喜慶 / 開幕賀卡 (橫式花牌風格)",
            ],
        )

        if card_mode == "喪禮傳統輓聯 (直式 / 橫式)":
            orientation = st.radio(
                "選擇輓聯列印方向", ["A4 直式排版", "A4 橫式排版"], horizontal=True
            )

            with st.expander("✍️ 1. 輸入輓聯各區塊文字內容", expanded=True):
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.markdown("**【上款 / 受者設定】**")
                    upper_text = st.text_input(
                        "右側/上方受者文字", value="敬悼 佛弟子林文姬居士蓮前"
                    )
                with col_t2:
                    st.markdown("**【中款 / 輓辭設定】**")
                    mid_text = st.text_input("中間輓辭文字", value="往生極樂")
                with col_t3:
                    st.markdown("**【下款 / 署名與敬挽設定】**")
                    sender_company = st.text_input("機關 / 單位名稱", value="桃園市議員")
                    sender_name = st.text_input("落款大名", value="李宗豪")
                    kwan_text = st.text_input("敬輓字樣", value="敬輓")

            with st.expander("⚙️ 2. 自由調整字體大小與位置微調", expanded=False):
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                with f_col1:
                    sz_upper = st.slider("上款字體大小", 20, 80, 42)
                with f_col2:
                    sz_mid = st.slider("中款字體大小", 50, 180, 105)
                with f_col3:
                    sz_lower = st.slider("下款/姓名字體大小", 20, 80, 42)
                with f_col4:
                    sz_kwan = st.slider("敬輓字體大小", 20, 80, 38)

                st.markdown("---")
                p_col1, p_col2, p_col3 = st.columns(3)
                with p_col1:
                    pos_right_offset = st.slider(
                        "右側欄位上下平移", -100, 100, 0, key="p_r"
                    )
                    pos_right_x = st.slider(
                        "右側欄位左右平移", -100, 100, 0, key="px_r"
                    )
                with p_col2:
                    pos_mid_offset = st.slider(
                        "中間欄位上下平移", -100, 100, 0, key="p_m"
                    )
                    pos_mid_x = st.slider(
                        "中間欄位左右平移", -100, 100, 0, key="px_m"
                    )
                with p_col3:
                    pos_left_offset = st.slider(
                        "左側欄位上下平移", -100, 100, 0, key="p_l"
                    )
                    pos_left_x = st.slider(
                        "左側欄位左右平移", -100, 100, 0, key="px_l"
                    )

            st.markdown("---")

            if orientation == "A4 直式排版":
                a4_html = f"""
                    <style>
                    .a4-portrait {{
                        width: 210mm;
                        height: 297mm;
                        padding: 20mm 15mm;
                        margin: auto;
                        border: 2px dashed #bbb;
                        background: white;
                        font-family: "DFKai-SB", "BiauKai", "標楷體", "KaiTi", serif;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-start;
                        box-sizing: border-box;
                        box-shadow: 0 0 15px rgba(0,0,0,0.1);
                        color: #000;
                    }}
                    .col-right {{
                        writing-mode: vertical-rl;
                        font-size: {sz_upper}px;
                        letter-spacing: 4px;
                        height: 90%;
                        display: flex;
                        align-items: flex-start;
                        position: relative;
                        top: {pos_right_offset}px;
                        right: {pos_right_x}px;
                    }}
                    .col-center {{
                        writing-mode: vertical-rl;
                        font-size: {sz_mid}px;
                        letter-spacing: 12px;
                        height: 90%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-weight: bold;
                        position: relative;
                        top: {pos_mid_offset}px;
                        left: {pos_mid_x}px;
                    }}
                    .col-left-group {{
                        height: 90%;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                        align-items: flex-end;
                        position: relative;
                        top: {pos_left_offset}px;
                        left: {pos_left_x}px;
                    }}
                    .col-bottom-left-stack {{
                        writing-mode: horizontal-tb;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                    }}
                    .col-lower {{
                        writing-mode: vertical-rl;
                        font-size: {sz_lower}px;
                        letter-spacing: 4px;
                    }}
                    .col-kwan {{
                        writing-mode: vertical-rl;
                        font-size: {sz_kwan}px;
                        letter-spacing: 4px;
                    }}
                    @media print {{
                        @page {{ size: A4 portrait; margin: 0; }}
                        body * {{ visibility: hidden; }}
                        .a4-portrait, .a4-portrait * {{ visibility: visible; }}
                        .a4-portrait {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; margin: 0; }}
                    }}
                    </style>
                    <div class="a4-portrait">
                        <div class="col-left-group">
                            <div></div>
                            <div class="col-bottom-left-stack">
                                <div class="col-lower">{sender_company} {sender_name}</div>
                                <div class="col-kwan" style="margin-top: 10px;">{kwan_text}</div>
                            </div>
                        </div>
                        <div class="col-center">{mid_text}</div>
                        <div class="col-right">{upper_text}</div>
                    </div>
                """
                st.markdown(a4_html, unsafe_allow_html=True)
                st.info("💡 列印提示：請按下 **Ctrl + P**，並將列印設定選取「直式 (Portrait)」、取消頁首頁尾，即可印出精準排版的傳統直式輓聯！")

            else:
                a4_landscape_html = f"""
                    <style>
                    .a4-landscape {{
                        width: 297mm;
                        height: 210mm;
                        padding: 15mm 20mm;
                        margin: auto;
                        border: 2px dashed #bbb;
                        background: white;
                        font-family: "DFKai-SB", "BiauKai", "標楷體", "KaiTi", serif;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                        box-sizing: border-box;
                        box-shadow: 0 0 15px rgba(0,0,0,0.1);
                        color: #000;
                    }}
                    .land-top {{
                        font-size: {sz_upper}px;
                        text-align: center;
                        letter-spacing: 2px;
                    }}
                    .land-center {{
                        font-size: {sz_mid}px;
                        text-align: center;
                        font-weight: bold;
                        letter-spacing: 6px;
                    }}
                    .land-bottom {{
                        font-size: {sz_lower}px;
                        text-align: right;
                        letter-spacing: 2px;
                    }}
                    @media print {{
                        @page {{ size: A4 landscape; margin: 0; }}
                        body * {{ visibility: hidden; }}
                        .a4-landscape, .a4-landscape * {{ visibility: visible; }}
                        .a4-landscape {{ position: absolute; left: 0; top: 0; border: none; box-shadow: none; margin: 0; }}
                    }}
                    </style>
                    <div class="a4-landscape">
                        <div class="land-top">{upper_text}</div>
                        <div class="land-center">{mid_text}</div>
                        <div class="land-bottom">{sender_company} {sender_name} {kwan_text}</div>
                    </div>
                """
                st.markdown(a4_landscape_html, unsafe_allow_html=True)
                st.info("💡 列印提示：請按下 **Ctrl + P**，並將列印設定選取「橫式 (Landscape)」、取消頁首頁尾，即可印出橫式輓聯！")

        else:
            # 喜慶 / 開幕賀卡模式
            st.markdown("### 🌸 喜慶 / 開幕賀卡設定")
            c_top = st.text_input("賀詞標題 (例如: 祝 鴻圖大展)", value="祝 鴻圖大展")
            c_mid = st.text_input("主要賀詞內容 (例如: 業務蒸蒸日上 生意興隆)", value="業務蒸蒸日上 生意興隆")
            c_bot = st.text_input("署名 / 送花人 (例如: 好友 張小明 敬賀)", value="好友 張小明 敬賀")

            card_html = f"""
                <style>
                .card-box {{
                    width: 297mm;
                    height: 210mm;
                    padding: 25mm;
                    margin: auto;
                    border: 3px solid #d4af37;
                    background: #fffdfa;
                    font-family: "DFKai-SB", "BiauKai", "標楷體", serif;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-around;
                    align-items: center;
                    box-sizing: border-box;
                    box-shadow: 0 0 15px rgba(0,0,0,0.15);
                    color: #8b0000;
                    text-align: center;
                }}
                .card-title {{ font-size: 50px; font-weight: bold; letter-spacing: 4px; }}
                .card-content {{ font-size: 65px; font-weight: bold; letter-spacing: 6px; color: #000; }}
                .card-footer {{ font-size: 40px; font-weight: bold; letter-spacing: 2px; align-self: flex-end; }}
                @media print {{
                    @page {{ size: A4 landscape; margin: 0; }}
                    body * {{ visibility: hidden; }}
                    .card-box, .card-box * {{ visibility: visible; }}
                    .card-box {{ position: absolute; left: 0; top: 0; border: none; width: 100%; height: 100%; margin: 0; padding: 20mm; box-shadow: none; }}
                }}
                </style>
                <div class="card-box">
                    <div class="card-title">{c_top}</div>
                    <div class="card-content">{c_mid}</div>
                    <div class="card-footer">{c_bot}</div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            st.info("💡 提示：按下 **Ctrl + P**（橫式 Landscape）即可將此喜慶花牌賀卡列印出來！")
