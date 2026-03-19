"""
Coleta dados usando endpoints exatos descobertos via navegacao
"""
import json, requests
from pathlib import Path
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

PASTA       = Path("C:/Users/WILLIAM/village-gourmet/dados")
DATA_INICIO = "2026-03-01"
DATA_FIM    = "2026-03-19"
BASE        = "https://report.yooga.com.br"

def extrair_token():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page    = browser.contexts[0].pages[0]
        page.goto("https://painel.yooga.com.br/dashboard", wait_until="networkidle", timeout=20000)
        token = page.evaluate("localStorage.getItem('app_v3_token')")
        idi   = page.evaluate("localStorage.getItem('app_current_idi')")
    return token, str(idi or "")

def sessao(token, idi):
    s = requests.Session()
    s.headers.update({
        "Authorization":  f"Bearer {token}",
        "Accept":         "application/json",
        "Content-Type":   "application/json",
        "Origin":         "https://painel.yooga.com.br",
        "Referer":        "https://painel.yooga.com.br/",
        "x-franchise-id": idi,
    })
    return s

def get(s, url, desc):
    r = s.get(url, timeout=30)
    if r.status_code == 200:
        d = r.json()
        print(f"  [OK {r.status_code}] {desc}")
        return d
    print(f"  [HTTP {r.status_code}] {desc} — {url[:80]}")
    return None

def salvar(nome, dados):
    arq = PASTA / f"{nome}.json"
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    n = len(dados) if isinstance(dados, list) else len(str(dados))
    print(f"  => {arq.name}  ({n} {'registros' if isinstance(dados,list) else 'chars'})")

def main():
    print("=" * 60)
    print(f"  COLETA ENDPOINTS CONFIRMADOS — {DATA_INICIO} a {DATA_FIM}")
    print("=" * 60)

    token, idi = extrair_token()
    s = sessao(token, idi)

    # ── ESTOQUE MINIMO ──────────────────────────────────────
    print("\n[1] ESTOQUE MINIMO")
    d = get(s, f"{BASE}/produtos/estoque/minimo", "estoque minimo")
    if d: salvar("estoque_minimo", d)

    # ── PRODUTOS V3 (com estoque atual) ────────────────────
    print("\n[2] PRODUTOS COM ESTOQUE (v3)")
    d = get(s, f"{BASE}/v3/produtos", "produtos v3 completo")
    if d: salvar("produtos_estoque_v3", d)

    # ── CARDAPIO COMPLETO (com paginacao) ──────────────────
    print("\n[3] CARDAPIO COMPLETO (todos os produtos)")
    todos_produtos = []
    page_num = 1
    while True:
        d = get(s, f"{BASE}/v2/produtos/dashboard?page={page_num}&query=&order=ranking&type_order=DESC&lote=false",
                f"produtos pagina {page_num}")
        if not d: break
        items = d if isinstance(d, list) else d.get("data", d.get("produtos", d.get("items", [])))
        if not items or (isinstance(items, list) and len(items) == 0): break
        if isinstance(items, list):
            todos_produtos.extend(items)
            if len(items) < 20: break  # ultima pagina
            page_num += 1
        else:
            todos_produtos.append(items)
            break
    if todos_produtos:
        salvar("cardapio_completo", todos_produtos)
    else:
        # Salva o que veio diretamente
        d = get(s, f"{BASE}/v2/produtos/dashboard?page=1&query=&order=ranking&type_order=DESC&lote=false", "cardapio p1")
        if d: salvar("cardapio_completo", d)

    # ── CATEGORIAS ─────────────────────────────────────────
    print("\n[4] CATEGORIAS")
    d = get(s, f"{BASE}/categorias", "categorias")
    if d: salvar("categorias", d)

    # ── CONTAS (financeiro) ────────────────────────────────
    print("\n[5] CONTAS / LANCAMENTOS")
    d = get(s, f"{BASE}/accounts", "accounts geral")
    if d: salvar("contas_geral", d)
    d = get(s, f"{BASE}/accounts?order=true", "accounts ordenado")
    if d: salvar("contas_ordenado", d)

    # ── EXTRATO MENSAL (pedidos/lancamentos) ───────────────
    print("\n[6] EXTRATO MENSAL (01/03 a 31/03)")
    d = get(s, f"{BASE}/orders?type=o&state=caixa&start={DATA_INICIO}&end=2026-03-31&month=true",
            "extrato mensal")
    if d: salvar("extrato_mensal", d)

    d = get(s, f"{BASE}/orders/options?type=o&state=caixa&start={DATA_INICIO}&end=2026-03-31",
            "extrato opcoes")
    if d: salvar("extrato_opcoes", d)

    # ── FLUXO DE CAIXA (dia a dia) ─────────────────────────
    print("\n[7] FLUXO DE CAIXA (dia a dia)")
    fluxo = []
    dt = datetime.strptime(DATA_INICIO, "%Y-%m-%d")
    fim = datetime.strptime(DATA_FIM, "%Y-%m-%d")
    while dt <= fim:
        ds = dt.strftime("%Y-%m-%d")
        d = get(s, f"{BASE}/v2/orders/flow?type=caixa&date={ds}", f"fluxo {ds}")
        if d: fluxo.append({"data": ds, "dados": d})
        dt += timedelta(days=1)
    if fluxo: salvar("fluxo_caixa_diario", fluxo)

    # ── DRE (periodo completo) ─────────────────────────────
    print("\n[8] DRE")
    d = get(s, f"{BASE}/dre?data_inicio={DATA_INICIO}&data_fim={DATA_FIM}", "dre periodo")
    if d: salvar("dre", d)

    # ── CAIXAS ─────────────────────────────────────────────
    print("\n[9] CAIXAS")
    d = get(s, f"{BASE}/v2/caixas?inverse=true&data_inicio={DATA_INICIO}&data_fim={DATA_FIM}&page=1&notLoadSales=true",
            "caixas periodo")
    if d: salvar("caixas", d)

    # ── FORMAS DE PAGAMENTO ────────────────────────────────
    print("\n[10] FORMAS DE PAGAMENTO")
    d = get(s, f"{BASE}/formas-pagamento", "formas pagamento")
    if d: salvar("formas_pagamento", d)
    d = get(s, f"{BASE}/payment-methods", "payment methods")
    if d: salvar("payment_methods", d)

    # ── FORNECEDORES ───────────────────────────────────────
    print("\n[11] FORNECEDORES")
    d = get(s, f"{BASE}/fornecedores?order=true", "fornecedores completo")
    if d: salvar("fornecedores_completo", d)

    # ── CLIENTES ───────────────────────────────────────────
    print("\n[12] CLIENTES")
    d = get(s, f"{BASE}/clientes?no_paginate=true", "clientes")
    if d: salvar("clientes", d)

    # ── VENDAS DIARIAS (cabecalho por dia) ─────────────────
    print("\n[13] VENDAS DIARIAS (cabecalho por dia)")
    vendas_dias = []
    dt = datetime.strptime(DATA_INICIO, "%Y-%m-%d")
    fim = datetime.strptime(DATA_FIM, "%Y-%m-%d")
    while dt <= fim:
        ds = dt.strftime("%Y-%m-%d")
        d = get(s, f"{BASE}/long/cabecalho?start={ds}", f"cabecalho {ds}")
        if d:
            vendas_dias.append({
                "data":         ds,
                "faturamento":  round(d.get("vendas_dia", 0), 2),
                "pedidos":      d.get("vendas_count", 0),
                "ticket_medio": round(d.get("ticket_medio", 0), 2),
                "pagamentos":   dict(zip(
                    d.get("chart_pagamento_labels", []),
                    d.get("chart_pagamento_data", [])
                )),
            })
        dt += timedelta(days=1)
    if vendas_dias: salvar("vendas_por_dia", vendas_dias)

    # ── RELATORIO FINAL ────────────────────────────────────
    print("\n" + "=" * 60)
    arquivos = sorted(PASTA.glob("*.json"))
    print(f"  {len(arquivos)} arquivos salvos em {PASTA}")
    for a in arquivos:
        if not a.name.startswith("_"):
            print(f"  {a.name:45s} {a.stat().st_size:>8} bytes")

if __name__ == "__main__":
    main()
