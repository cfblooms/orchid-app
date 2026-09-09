import datetime
import os
import streamlit as st
from utils import (
    WEB_APP_URL,
    get_data,
    append_data,
    update_data,
    delete_data,
    get_next_id,
)

st.set_page_config(
    page_title="蘭花庫存與訂單管理系統", page_icon="🌸", layout="wide"
)

st.title("🌸 蘭花庫存、客戶、進退貨與訂單管理系統")

if not WEB_APP_URL or "你的網址" in WEB_APP_URL:
    st.warning(
        "⚠️ 提醒：請先至 `utils.py` 設定您的 Google Apps Script 雲端網址。"
    )
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🌸 1. 蘭花品種資料庫",
            "👥 2. 客戶資料庫",
            "📦 3. 進貨與庫存管理",
            "🔄 4. 退貨管理區",
            "💰 5. 訂單與帳務管理",
        ]
    )

    # -----------------------------------------
    # TAB 1: 蘭花品種資料庫
    # -----------------------------------------
    with tab1:
        st.header("🌸 蘭花品種寫入與資料庫管理")
        st.markdown(
            "在此建立標準蘭花品種檔案與照片，後續進貨與開單時可直接選取。"
        )

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
        else:
            st.info("目前資料庫尚無品種資料。")

    # -----------------------------------------
    # TAB 2: 客戶資料庫
    # -----------------------------------------
    with tab2:
        st.header("👥 客戶資料庫管理 (批發商與花店)")
        st.markdown(
            "在此建立批發商、花店與常客資料，方便後續訂單直接點選帶入聯絡資訊。"
        )

        with st.form("cust_form"):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                cust_id = st.text_input("客戶編號", value=get_next_id("CUST", "客戶資料庫"))
                cust_name = st.text_input("客戶 / 店鋪名稱 (例如: 大吉花店、宏達批發)")
            with c_col2:
                cust_type = st.selectbox("客戶類別", ["批發商", "花店", "個人"])
                cust_phone = st.text_input("聯絡電話", value="0912-345678")
                cust_line = st.text_input("Line 名稱 / 備註", value="")

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

                types_list = ["批發商", "花店", "個人"]
                default_type_idx = (
                    types_list.index(c_type) if c_type in types_list else 0
                )

                with st.form("update_cust_form"):
                    upd_c_name = st.text_input("修改客戶 / 店鋪名稱", value=c_name)
                    upd_c_type = st.selectbox(
                        "修改客戶類別", types_list, index=default_type_idx
                    )
                    upd_c_phone = st.text_input("修改聯絡電話", value=c_phone)
                    upd_c_line = st.text_input("修改 Line 名稱 / 備註", value=c_line)

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
                    input_mode = st.radio(
                        "品種選擇方式", ["從資料庫選取", "自行輸入"], horizontal=True
                    )
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
                    supplier = st.text_input("供應商 / 花農名稱", value="某某花農")
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
                        supplier,
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
                    supplier = st.text_input("盆器供應商", value="陶瓷器行")
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
                        supplier,
                    ]
                    if append_data("進貨表", row):
                        st.success("成功新增盆器進貨紀錄！")
                        st.rerun()

        st.markdown("---")
        st.subheader("📦 現有進貨清單管理")
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
                    party_name = st.text_input(
                        "自行輸入對象名稱 (花農/批發商)", value="某某花農"
                    )

            with col_r2:
                target_item = st.selectbox(
                    "關聯進貨品項",
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
                f"💡 系統計算總金額：**{total_return_amount} 元** ({bad_qty}棵 × {unit_price}元)"
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

        st.subheader("📋 現有退貨紀錄總覽與刪除")
        df_ret = get_data("退貨表")
        if not df_ret.empty:
            st.dataframe(df_ret, use_container_width=True)
            ret_ids = df_ret[df_ret.columns[0]].astype(str).tolist()
            selected_ret_id = st.selectbox(
                "選擇要刪除的退貨編號", ret_ids, key="del_ret"
            )
            if st.button("🗑️ 刪除此退貨紀錄"):
                if delete_data("退貨表", selected_ret_id):
                    st.success(f"已刪除退貨編號：{selected_ret_id}")
                    st.rerun()
        else:
            st.info("目前尚無退貨紀錄。")

    # -----------------------------------------
    # TAB 5: 訂單與帳務管理
    # -----------------------------------------
    with tab5:
        st.header("💰 訂單登錄與帳務管理")

        df_inv_check = get_data("進貨表")
        flower_list = []
        if not df_inv_check.empty and "類別" in df_inv_check.columns:
            flower_df = df_inv_check[df_inv_check["類別"] == "蘭花"]
            if not flower_df.empty:
                flower_list = (
                    flower_df["品項名稱/品種"] + " (" + flower_df["規格細節"] + ")"
                ).tolist()

        df_cust_check = get_data("客戶資料庫")
        cust_name_list = (
            df_cust_check["客戶名稱"].tolist()
            if not df_cust_check.empty and "客戶名稱" in df_cust_check.columns
            else []
        )

        with st.form("order_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                order_id = st.text_input(
                    "訂單編號", value=get_next_id("OR", "訂單表")
                )
                cust_type = st.selectbox("客戶類型", ["批發", "花店", "個人"])

                c_input_mode = st.radio(
                    "訂購人選擇方式", ["從客戶資料庫選取", "自行輸入"], horizontal=True
                )
                if c_input_mode == "從客戶資料庫選取" and cust_name_list:
                    customer = st.selectbox("選擇客戶", cust_name_list)
                else:
                    customer = st.text_input("訂購人 / 批發商名稱")

                customer_phone = st.text_input("聯絡電話", value="0912-345678")
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
                    customer_phone,
                    item_spec_str,
                    pot_used,
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
                    o_phone = r_vals[3] if len(r_vals) > 3 else ""
                    o_spec = r_vals[4] if len(r_vals) > 4 else ""
                    o_pot = r_vals[5] if len(r_vals) > 5 else "無盆"
                    o_cost = (
                        float(r_vals[6])
                        if len(r_vals) > 6
                        and str(r_vals[6]).replace(".", "", 1).isdigit()
                        else 0.0
                    )
                    o_price = (
                        float(r_vals[7])
                        if len(r_vals) > 7
                        and str(r_vals[7]).replace(".", "", 1).isdigit()
                        else 0.0
                    )
                    o_date_str = (
                        r_vals[8] if len(r_vals) > 8 else str(datetime.date.today())
                    )
                    o_exp_str = (
                        r_vals[9] if len(r_vals) > 9 else str(datetime.date.today())
                    )
                    o_shipped = r_vals[10] if len(r_vals) > 10 else "未出貨"
                    o_payment = r_vals[11] if len(r_vals) > 11 else "未結"

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
                        upd_customer = st.text_input(
                            "修改訂購人/批發商名稱", value=o_customer
                        )
                        upd_phone = st.text_input("修改聯絡電話", value=o_phone)
                        upd_spec = st.text_input("修改品項與規格細節", value=o_spec)
                        upd_pot = st.text_input("修改使用盆器", value=o_pot)
                        upd_cost = st.number_input(
                            "修改預估總成本 (元)", min_value=0.0, value=o_cost
                        )
                        upd_price = st.number_input(
                            "修改總售價/金額 (元)", min_value=0.0, value=o_price
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
                                upd_phone,
                                upd_spec,
                                upd_pot,
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