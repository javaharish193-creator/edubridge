import urllib.request
import json

req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/login',
    data=json.dumps({"phone_number": "9876543210", "password": "Admin@123"}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())["access_token"]

sub_req = urllib.request.Request(
    'http://localhost:8000/api/v1/admin/subjects',
    headers={"Authorization": f"Bearer {token}"}
)
with urllib.request.urlopen(sub_req) as resp:
    subjects = json.loads(resp.read().decode())
    print(f"Total Subjects: {len(subjects)}")
    for s in subjects:
        mat_req = urllib.request.Request(
            f"http://localhost:8000/api/v1/content/subjects/{s['id']}/materials",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(mat_req) as mresp:
            tree = json.loads(mresp.read().decode())
            print(f"  OK: {s['name']} ({s['code']}) has {len(tree['chapters'])} chapters and {sum(len(c['materials']) for c in tree['chapters'])} materials")

print("All subjects verified in Content Hub!")
