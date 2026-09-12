#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool đồng bộ & kiểm tra dữ liệu Helpdesk Ticket từ hệ thống phụ qua JSON-RPC.
Kết hợp:
- Bước 2 (search_read): Lấy các trường thông tin ticket bao gồm 'description' (mô tả/ghi chú ticket)
- Bước 2c (gerp_get_messages): Lấy toàn bộ lịch sử chat Zalo, trao đổi & internal notes (messages_detail)
"""

import os
import sys
import json
import urllib.request
import urllib.error

# Ensure stdout handles UTF-8 on Windows terminal
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if not os.path.exists(config_path):
        print(f"[ERROR] Không tìm thấy file cấu hình tại {config_path}")
        sys.exit(1)
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def jsonrpc_call(url, service, method, *args):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": service,
            "method": method,
            "args": list(args),
        }
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            if 'error' in res:
                print(f"[ERROR JSON-RPC] {res['error'].get('message', res['error'])}")
                return None
            return res.get('result')
    except urllib.error.HTTPError as e:
        print(f"[HTTP ERROR {e.code}] {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"[URL ERROR] Không thể kết nối tới {url}: {e.reason}")
        return None


def main():
    print("=" * 80)
    print(" HELPDESK TICKET FETCH TOOL - SEARCH_READ (W/ DESCRIPTION) + GERP_GET_MESSAGES")
    print("=" * 80)

    cfg = load_config()
    base_url = cfg.get("base_url", "http://localhost:8069").rstrip("/")
    db = cfg.get("db", "gerp-eoffice-v17")
    login = cfg.get("login", "admin")
    password = cfg.get("password", "admin")
    limit = int(cfg.get("limit", 5))

    jsonrpc_url = f"{base_url}/jsonrpc"

    print(f"\n[1] Đăng nhập hệ thống (Request 1)...")
    print(f"    URL      : {jsonrpc_url}")
    print(f"    Database : {db}")
    print(f"    User     : {login}")

    uid = jsonrpc_call(jsonrpc_url, "common", "login", db, login, password)
    if not uid:
        print("\n[FAIL] Đăng nhập thất bại hoặc máy chủ chưa sẵn sàng. Vui lòng kiểm tra lại config.json!")
        return

    print(f"    ==> Đăng nhập thành công! User UID = {uid}")

    # 2. Search tickets bao gồm description (Request 2)
    ticket_fields = [
        "id", "ticket_ref", "name", "description", "team_id", "stage_id",
        "partner_id", "user_id", "priority", "create_date", "close_date"
    ]

    target_model = cfg.get("model", "gerp.helpdesk.ticket")
    print(f"\n[2] Tải danh sách Ticket kèm 'description' (Request 2 - Model: {target_model})...")

    tickets = jsonrpc_call(
        jsonrpc_url, "object", "execute_kw",
        db, uid, password,
        target_model, "search_read",
        [[]],
        {
            "fields": ticket_fields,
            "order": "create_date desc",
            "limit": limit
        }
    )

    if tickets is None and target_model == "gerp.helpdesk.ticket":
        print("    [Info] Thử lại với model 'helpdesk.ticket'...")
        target_model = "helpdesk.ticket"
        tickets = jsonrpc_call(
            jsonrpc_url, "object", "execute_kw",
            db, uid, password,
            target_model, "search_read",
            [[]],
            {
                "fields": ticket_fields,
                "order": "create_date desc",
                "limit": limit
            }
        )

    if not tickets:
        print("\n[INFO] Không tìm thấy bản ghi Ticket nào.")
        return

    print(f"    ==> Tìm thấy {len(tickets)} Ticket.")

    # 2c. Fetch messages/notes for all tickets (Request 2c)
    ticket_ids = [t["id"] for t in tickets]
    messages_by_ticket = {}

    print(f"\n[2c] Tải chi tiết chat Zalo & messages (gerp_get_messages - Request 2c)...")
    msgs_raw = jsonrpc_call(
        jsonrpc_url, "object", "execute_kw",
        db, uid, password,
        target_model, "gerp_get_messages",
        [ticket_ids]
    )

    if msgs_raw and isinstance(msgs_raw, list):
        for msg in msgs_raw:
            tid = msg.get("ticket_id")
            if tid:
                messages_by_ticket.setdefault(tid, []).append(msg)
        print(f"    ==> Tải thành công {len(msgs_raw)} tin nhắn/ghi chú (bao gồm cả chat Zalo & Internal Notes).")
    else:
        print("    [Warning] Không lấy được tin nhắn qua gerp_get_messages hoặc không có tin nhắn.")

    # In kết quả kết hợp đầy đủ thông tin Ticket + Description + messages_detail
    print("\n" + "=" * 80)
    print(f" KẾT QUẢ KẾT HỢP DỮ LIỆU TICKET (DESCRIPTION + MESSAGES_DETAIL CHAT ZALO)")
    print("=" * 80)

    for idx, t in enumerate(tickets, start=1):
        tid = t.get("id")
        t["messages_detail"] = messages_by_ticket.get(tid, [])
        t["message_count"] = len(t["messages_detail"])

        print(f"\n--- BẢN GHI #{idx} (ID: {tid} | Ref: {t.get('ticket_ref') or 'N/A'}) ---")
        print(json.dumps(t, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print(" HOÀN THÀNH KẾT HỢP DỮ LIỆU TICKET!")
    print("=" * 80)


if __name__ == "__main__":
    main()
