import os
import re

# Count URLs
print("=" * 50)
print("URL FILES")
print("=" * 50)

url_total = 0
url_files = [
    'ares_project/urls.py',
    'analytics/urls.py',
    'orders/urls.py',
    'products/urls.py',
    'support/urls.py',
    'users/urls.py',
    'verification/urls.py',
]

for filepath in url_files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            paths = len(re.findall(r'\bpath\s*\(', content))
            re_paths = len(re.findall(r'\bre_path\s*\(', content))
            count = paths + re_paths
            url_total += count
            print(f"{filepath}: {count} URLs")

print(f"\nTOTAL URL PATTERNS: {url_total}")

# Count Views
print("\n" + "=" * 50)
print("VIEW FILES")
print("=" * 50)

view_total = 0
view_files = [
    'analytics/views.py',
    'orders/views.py',
    'products/views.py',
    'support/views.py',
    'users/views.py',
    'verification/views.py',
]

for filepath in view_files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count function definitions
            funcs = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
            count = len(funcs)
            view_total += count
            print(f"{filepath}: {count} view functions")

print(f"\nTOTAL VIEW FUNCTIONS: {view_total}")

print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
print(f"Total URL patterns: {url_total}")
print(f"Total view functions: {view_total}")
