import urllib.request

def fetch(url, filename):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

fetch("https://emprego.sapo.pt/offers?q=trainee%20OR%20estagio", "sapo_raw.html")
fetch("https://expressoemprego.pt/ofertas?q=est%C3%A1gio+OR+trainee", "expresso_raw.html")
