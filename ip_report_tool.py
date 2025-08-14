import ipaddress
import csv
import requests

# Загружаем IP из файла
def load_ips(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip()]

# Загружаем blacklist (IP или подсети)
def load_blacklist(filename):
    with open(filename) as f:
        return [ipaddress.ip_network(line.strip()) for line in f if line.strip()]

# Проверка: входит ли IP в blacklist
def is_blacklisted(ip, blacklist):
    ip_obj = ipaddress.ip_address(ip)
    for net in blacklist:
        if ip_obj in net:
            return True
    return False

# Получаем страну и организацию через API
def enrich_ip(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if r.status_code == 200:
            data = r.json()
            country = data.get("country", "N/A")
            org = data.get("org", "N/A")
            return country, org
        else:
            return "N/A", "N/A"
    except:
        return "N/A", "N/A"

# Сохраняем в CSV
def save_to_csv(rows, filename="report.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IP", "Статус", "Страна", "Организация"])
        writer.writerows(rows)

# ---- Основной код ----

ips = load_ips("ips_to_check2.txt")
blacklist = load_blacklist("blacklist.txt")
report_rows = []

for ip in ips:
    status = "BLACKLISTED" if is_blacklisted(ip, blacklist) else "OK"
    country, org = enrich_ip(ip)
    print(f"🔍 {ip} — {status} | {country} | {org}")
    report_rows.append([ip, status, country, org])

save_to_csv(report_rows)
print("✅ Отчёт сохранён в report.csv")
