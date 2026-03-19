"""
Coleta notas fiscais da API dfe.yooga.com.br
NFC-e (modelo=65), NF-e (modelo=55), Entrada de Nota, Notas de Compra
"""
import json, requests
from pathlib import Path

PASTA        = Path("C:/Users/WILLIAM/village-gourmet/dados")
DATA_INI     = "2026-03-01"
DATA_FIM     = "2026-03-31"
BASE_DFE     = "https://dfe.yooga.com.br"
BASE_REPORT  = "https://report.yooga.com.br"

# Carrega token fiscal salvo
with open(PASTA / "emissor_init_raw.json", encoding="utf-8") as f:
    init = json.load(f)
TOKEN_FISCAL = init["https://report.yooga.com.br/configs/tokens/fiscal"]["token"]

def sessao():
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {TOKEN_FISCAL}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
        "Origin":        "https://emissor.yooga.com.br",
        "Referer":       "https://emissor.yooga.com.br/",
    })
    return s

def get(s, url, desc):
    r = s.get(url, timeout=30)
    if r.status_code == 200:
        try:
            d = r.json()
            n = len(d) if isinstance(d, list) else len(str(d))
            print(f"  [OK {r.status_code}] {desc} — {n} {'registros' if isinstance(d,list) else 'chars'}")
            return d
        except:
            print(f"  [NAO-JSON] {desc}")
            return None
    print(f"  [HTTP {r.status_code}] {desc}")
    return None

def main():
    print("=" * 60)
    print("  COLETA NOTAS FISCAIS — dfe.yooga.com.br")
    print(f"  Periodo: {DATA_INI} a {DATA_FIM}")
    print("=" * 60)

    s = sessao()
    notas = {}

    # ── NFC-e (modelo 65 — cupom fiscal eletronico) ──────────
    print("\n[1] NFC-e (modelo 65)")
    d = get(s, f"{BASE_DFE}/nota/resumo?dataIni={DATA_INI}&dataFim={DATA_FIM}&modelo=65", "resumo NFC-e")
    if d: notas["nfce_resumo"] = d

    d = get(s, f"{BASE_DFE}/nota?dataIni={DATA_INI}&dataFim={DATA_FIM}&cStat=&modelo=65", "lista NFC-e")
    if d: notas["nfce_lista"] = d

    # ── NF-e saida (modelo 55) ────────────────────────────────
    print("\n[2] NF-e saida (modelo 55)")
    d = get(s, f"{BASE_DFE}/nota/resumo?dataIni={DATA_INI}&dataFim={DATA_FIM}&modelo=55", "resumo NF-e")
    if d: notas["nfe_resumo"] = d

    d = get(s, f"{BASE_DFE}/nota?dataIni={DATA_INI}&dataFim={DATA_FIM}&cStat=&modelo=55", "lista NF-e")
    if d: notas["nfe_lista"] = d

    # ── Entrada de Nota (compras recebidas) ───────────────────
    print("\n[3] Entrada de Nota")
    endpoints_entrada = [
        (f"{BASE_DFE}/entrada?dataIni={DATA_INI}&dataFim={DATA_FIM}", "entrada lista"),
        (f"{BASE_DFE}/nota/entrada?dataIni={DATA_INI}&dataFim={DATA_FIM}", "nota entrada"),
        (f"{BASE_DFE}/nfe/entrada?dataIni={DATA_INI}&dataFim={DATA_FIM}", "nfe entrada"),
        (f"{BASE_DFE}/manifesto?dataIni={DATA_INI}&dataFim={DATA_FIM}", "manifesto"),
        (f"{BASE_DFE}/cte?dataIni={DATA_INI}&dataFim={DATA_FIM}", "cte"),
        (f"{BASE_DFE}/nota?dataIni={DATA_INI}&dataFim={DATA_FIM}&tipo=entrada", "nota tipo entrada"),
        (f"{BASE_DFE}/nota?dataIni={DATA_INI}&dataFim={DATA_FIM}&tpNF=0", "nota tpNF=0"),
        (f"{BASE_DFE}/nota?dataIni={DATA_INI}&dataFim={DATA_FIM}&tpNF=0&modelo=55", "nota entrada modelo55"),
    ]
    for url, desc in endpoints_entrada:
        d = get(s, url, desc)
        if d and len(str(d)) > 10:
            notas["entrada_lista"] = d
            print(f"  => Entrada encontrada via: {url.split('?')[0]}")
            break

    # ── Notas de Compra ───────────────────────────────────────
    print("\n[4] Notas de Compra")
    endpoints_compra = [
        (f"{BASE_DFE}/compra?dataIni={DATA_INI}&dataFim={DATA_FIM}", "compra"),
        (f"{BASE_DFE}/nota/compra?dataIni={DATA_INI}&dataFim={DATA_FIM}", "nota compra"),
        (f"{BASE_REPORT}/compras?start=2026-03-01&end={DATA_FIM}", "report compras"),
        (f"{BASE_REPORT}/notas-entrada?start=2026-03-01&end={DATA_FIM}", "notas entrada"),
        (f"{BASE_REPORT}/fiscal/notas?start=2026-03-01&end={DATA_FIM}", "fiscal notas"),
    ]
    for url, desc in endpoints_compra:
        d = get(s, url, desc)
        if d and len(str(d)) > 10:
            notas["compras_lista"] = d
            print(f"  => Compras encontrada via: {url.split('?')[0]}")
            break

    # ── Salvar ────────────────────────────────────────────────
    out = PASTA / "notas_fiscais.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=2)
    print(f"\nSalvo: {out}")
    for k, v in notas.items():
        n = len(v) if isinstance(v, list) else len(str(v))
        print(f"  {k:30s} {n:>6} {'registros' if isinstance(v,list) else 'chars'}")

if __name__ == "__main__":
    main()
