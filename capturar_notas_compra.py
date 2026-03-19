"""
Captura o body do POST dfe.yooga.com.br/fiscal/robo/notas e testa com datas corretas
"""
import json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

PASTA    = Path("C:/Users/WILLIAM/village-gourmet/dados")

post_bodies = {}

def main():
    print("=" * 60)
    print("  CAPTURA BODY DO POST fiscal/robo/notas")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        ctx  = browser.contexts[0]
        page = ctx.new_page()

        def on_request(req):
            if "fiscal/robo/notas" in req.url:
                try:
                    body = req.post_data
                    print(f"\n  [POST BODY] {req.url}")
                    print(f"  Body: {body}")
                    post_bodies[req.url] = body
                except Exception as e:
                    print(f"  Erro ao ler body: {e}")

        def on_response(resp):
            if "fiscal/robo/notas" in resp.url:
                try:
                    data = resp.json()
                    print(f"\n  [RESP] {resp.url}")
                    print(f"  Response: {json.dumps(data, ensure_ascii=False)[:300]}")
                except:
                    pass

        page.on("request",  on_request)
        page.on("response", on_response)

        page.goto("https://emissor.yooga.com.br", wait_until="networkidle", timeout=30000)
        time.sleep(1)

        page.get_by_text("Notas de Compra", exact=True).first.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(3)

        print(f"\nBodies capturados: {len(post_bodies)}")
        page.close()

    # Agora testa direto com requests usando o body correto
    if post_bodies:
        import requests as req_lib

        with open(PASTA / "emissor_init_raw.json", encoding="utf-8") as f:
            init = json.load(f)
        TOKEN = init["https://report.yooga.com.br/configs/tokens/fiscal"]["token"]

        hdrs = {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://emissor.yooga.com.br",
            "Referer": "https://emissor.yooga.com.br/",
        }

        # Testa com o body original
        for url, body_str in post_bodies.items():
            try:
                body_orig = json.loads(body_str) if body_str else {}
                print(f"\nBody original: {json.dumps(body_orig, ensure_ascii=False)}")
            except:
                body_orig = {}
                print(f"\nBody original (raw): {body_str}")

            # Testa com periodo completo de marco
            bodies_to_test = [
                body_orig,
                {"dataIni": "2026-03-01", "dataFim": "2026-03-31"},
                {"dataIni": "2026-01-01", "dataFim": "2026-03-31"},
                {"dataInicio": "2026-03-01", "dataFim": "2026-03-31"},
                {"start": "2026-03-01", "end": "2026-03-31"},
                {"page": 0, "size": 50, "dataIni": "2026-03-01", "dataFim": "2026-03-31"},
            ]

            print("\nTestando variações de body:")
            for body in bodies_to_test:
                r = req_lib.post(url, headers=hdrs, json=body, timeout=20)
                try:
                    d = r.json()
                    total = d.get("total", len(d) if isinstance(d, list) else "?")
                    print(f"  [{r.status_code}] body={json.dumps(body)} -> total={total}")
                except:
                    print(f"  [{r.status_code}] body={json.dumps(body)} -> {r.text[:80]}")

if __name__ == "__main__":
    main()
