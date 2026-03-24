#!/usr/bin/env python3
"""
Backfill book.total_sold from delivered/completed orders.
Run: python3 sync_total_sold.py
"""

import requests

ORDER_URL = "http://localhost:8007"
BOOK_URL = "http://localhost:8005"


def main():
    print("Syncing total_sold from order-service -> book-service ...")

    try:
        resp = requests.get(f"{ORDER_URL}/orders/", timeout=15)
        resp.raise_for_status()
        orders = resp.json() if isinstance(resp.json(), list) else []
    except Exception as exc:
        print(f"Failed to fetch orders: {exc}")
        return

    sold_map = {}
    for order in orders:
        status = str(order.get("status", "")).lower()
        if status in {"cancelled", "refunded"}:
            continue

        for item in order.get("items") or []:
            book_id = str(item.get("book_id") or "").strip()
            qty = int(item.get("quantity") or 0)
            if not book_id or qty <= 0:
                continue
            sold_map[book_id] = sold_map.get(book_id, 0) + qty

    if not sold_map:
        print("No sale-qualified order items found.")
        return

    ok = 0
    fail = 0
    for book_id, qty in sold_map.items():
        try:
            r = requests.post(
                f"{BOOK_URL}/books/{book_id}/sales/",
                json={"quantity": qty, "mode": "set"},
                timeout=8,
            )
            if r.status_code == 200:
                ok += 1
            else:
                fail += 1
                print(f"Failed {book_id}: {r.status_code} {r.text[:120]}")
        except Exception as exc:
            fail += 1
            print(f"Failed {book_id}: {exc}")

    print(f"Done. Updated={ok}, Failed={fail}")


if __name__ == "__main__":
    main()
