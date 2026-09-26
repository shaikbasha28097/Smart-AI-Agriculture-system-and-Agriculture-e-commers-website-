import urllib.request
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_endpoints():
    print("=== 1. TEST CATEGORIES API ===")
    req = urllib.request.Request(f"{BASE_URL}/api/categories")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Status: {resp.status}, Total Categories: {len(data['categories'])}")
        for c in data['categories']:
            print(f"  - [{c['id']}] {c['name']} ({c['slug']})")
        assert any(c['name'] == 'Groceries' and c['id'] == 9 for c in data['categories']), "Groceries category missing!"
        print("PASS: Groceries category is present in API.")

    print("\n=== 2. TEST GROCERIES PRODUCTS (Category 9) ===")
    req = urllib.request.Request(f"{BASE_URL}/api/products?category_id=9")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Status: {resp.status}, Products in Groceries: {len(data['products'])}")
        for p in data['products']:
            print(f"  - [{p['id']}] {p['name']} | Price: INR {p['price']} /{p['unit']}")
        assert len(data['products']) >= 4, "Expected seeded grocery products!"
        print("PASS: Groceries products returned correctly.")

    print("\n=== 3. TEST FARMING TOOLS PRODUCTS (Category 8) ===")
    req = urllib.request.Request(f"{BASE_URL}/api/products?category_id=8")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Status: {resp.status}, Products in Farming Tools: {len(data['products'])}")
        for p in data['products']:
            print(f"  - [{p['id']}] {p['name']} | Price: INR {p['price']}")
        assert len(data['products']) >= 1, "Expected farming tools products!"
        print("PASS: Farming tools products returned correctly.")

    print("\n=== 4. TEST SELLER CREATE FARMING TOOL (No unit of measure needed) ===")
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body_lines = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="seller_id"',
        '',
        '2',
        f"--{boundary}",
        'Content-Disposition: form-data; name="name"',
        '',
        'Heavy-Duty Ergonomic Garden Hoe & Tiller',
        f"--{boundary}",
        'Content-Disposition: form-data; name="category_id"',
        '',
        '8',
        f"--{boundary}",
        'Content-Disposition: form-data; name="price"',
        '',
        '750',
        f"--{boundary}",
        'Content-Disposition: form-data; name="stock_quantity"',
        '',
        '40',
        f"--{boundary}",
        'Content-Disposition: form-data; name="unit"',
        '',
        '',
        f"--{boundary}",
        'Content-Disposition: form-data; name="is_organic"',
        '',
        '0',
        f"--{boundary}",
        'Content-Disposition: form-data; name="short_description"',
        '',
        'Carbon steel garden hoe for weeding and soil aeration.',
        f"--{boundary}--",
        ''
    ]
    body = "\r\n".join(body_lines).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/seller/create-product",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode())
        print("Create Tool Response:", res)
        assert res['success'] is True, "Failed to create tool!"
        tool_id = res['product_id']
        print(f"PASS: Created Farming Tool ID: {tool_id}")

    print("\n=== 5. VERIFY CREATED TOOL IN PRODUCTS API ===")
    req = urllib.request.Request(f"{BASE_URL}/api/products/{tool_id}")
    with urllib.request.urlopen(req) as resp:
        p_data = json.loads(resp.read().decode())
        print(f"Fetched Tool: {p_data['product']['name']} | Category: {p_data['product']['category_id']}")
        assert p_data['product']['category_id'] == 8
        print("PASS: Verified tool exists in category 8.")

    print("\n=== 6. CLEANUP TEST TOOL ===")
    del_req = urllib.request.Request(f"{BASE_URL}/api/products/{tool_id}")
    del_req.get_method = lambda: 'DELETE'
    with urllib.request.urlopen(del_req) as resp:
        del_data = json.loads(resp.read().decode())
        print(f"Cleanup Status: {del_data}")
        assert del_data['success'] is True

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_endpoints()
