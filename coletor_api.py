"""
Coletor API Yooga - Village Gourmet
Usa token JWT extraido do browser para chamadas diretas
"""
import json
import requests
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

PASTA       = Path("C:/Users/WILLIAM/village-gourmet/dados")
PASTA.mkdir(parents=True, exist_ok=True)
DATA_INICIO = "2026-03-01"
DATA_FIM    = "2026-03-19"
BASE        = "https://report.yooga.com.br"

resultados = {}
erros      = []

# ──────────────────────────────────────────────
# 1. Extrai token do browser
# ──────────────────────────────────────────────

def extrair_token():
    print("Extraindo token do Chrome...")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page    = browser.contexts[0].pages[0]
        page.goto("https://painel.yooga.com.br/dashboard",
                  wait_until="networkidle", timeout=20000)
        token = page.evaluate("localStorage.getItem('app_v3_token')")
        idi   = page.evaluate("localStorage.getItem('app_current_idi')")
        user  = json.loads(page.evaluate("localStorage.getItem('app_user')") or "{}")
    if not token:
        print("ERRO: token nao encontrado")
        sys.exit(1)
    print(f"  Token OK  |  IDI: {idi}  |  Usuario: {user.get('email','?')}")
    return token, idi

# ──────────────────────────────────────────────
# 2. Helpers de requisicao
# ──────────────────────────────────────────────

def get(session, url, desc=""):
    try:
        r = session.get(url, timeout=20)
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"  [OK {r.status_code}] {desc or url[:80]}")
                return data
            except:
                print(f"  [NAO-JSON {r.status_code}] {desc or url[:80]}")
                return None
        else:
            print(f"  [HTTP {r.status_code}] {desc or url[:80]}")
            erros.append({"url": url, "status": r.status_code})
            return None
    except Exception as e:
        print(f"  [EXCECAO] {desc}: {e}")
        erros.append({"url": url, "erro": str(e)})
        return None

def salvar(nome, dados):
    arq = PASTA / f"{nome}.json"
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    n = len(dados) if isinstance(dados, list) else len(str(dados))
    print(f"  => Salvo: {arq.name}  ({n} {'registros' if isinstance(dados,list) else 'chars'})")

# ──────────────────────────────────────────────
# 3. Coletas
# ──────────────────────────────────────────────

def coletar_dashboard(s):
    print("\n[1/8] DASHBOARD")
    d = get(s, f"{BASE}/long/cabecalho?start={DATA_INICIO}", "cabecalho")
    if d:
        resultados["dashboard"] = d
        salvar("dashboard", d)

def coletar_vendas_diarias(s):
    print("\n[2/8] VENDAS DIARIAS (por dia do periodo)")
    # Tenta endpoint de vendas por dia
    endpoints = [
        f"{BASE}/long/vendas?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/relatorio/vendas-dia?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/vendas/diario?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/dashboard/vendas?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/long/timeflow?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/relatorio/diario?start={DATA_INICIO}&end={DATA_FIM}",
    ]
    for url in endpoints:
        d = get(s, url, url.split("/")[-1].split("?")[0])
        if d and len(str(d)) > 20:
            resultados["vendas_diarias"] = d
            salvar("vendas_diarias", d)
            break

    # Coleta dia a dia se nenhum endpoint funcionou
    if "vendas_diarias" not in resultados:
        print("  Tentando coleta dia a dia...")
        dias = []
        dt = datetime.strptime(DATA_INICIO, "%Y-%m-%d")
        fim = datetime.strptime(DATA_FIM, "%Y-%m-%d")
        while dt <= fim:
            ds = dt.strftime("%Y-%m-%d")
            d = get(s, f"{BASE}/long/cabecalho?start={ds}", f"dia {ds}")
            if d:
                dias.append({"data": ds, **{k: v for k, v in d.items()
                    if k in ["vendas_dia","vendas_count","ticket_medio"]}})
            dt += timedelta(days=1)
        if dias:
            resultados["vendas_diarias"] = dias
            salvar("vendas_diarias", dias)

def coletar_vendas_produtos(s):
    print("\n[3/8] VENDAS POR PRODUTO")
    endpoints = [
        f"{BASE}/long/produtos?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/relatorio/produtos?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/produtos/vendas?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/relatorio/ranking-produtos?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/vendas/produtos?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/long/ranking?start={DATA_INICIO}&end={DATA_FIM}",
    ]
    for url in endpoints:
        d = get(s, url, url.split("/")[-1].split("?")[0])
        if d and len(str(d)) > 20:
            resultados["vendas_produtos"] = d
            salvar("vendas_produtos", d)
            break

    # Fallback: usa dados do dashboard ja coletado
    if "vendas_produtos" not in resultados and "dashboard" in resultados:
        cab = resultados["dashboard"]
        labels = cab.get("chart_produto_labels", [])
        qtds   = cab.get("chart_produto_data", [])
        desc   = cab.get("chart_produto_desc", [])
        prods  = [{"produto": l, "descricao": d, "quantidade_mes": q}
                  for l, d, q in zip(labels, desc or labels, qtds)]
        prods.sort(key=lambda x: x["quantidade_mes"], reverse=True)
        resultados["vendas_produtos"] = prods
        salvar("vendas_produtos", prods)
        print(f"  Extraido do dashboard: {len(prods)} produtos")

def coletar_cardapio(s):
    print("\n[4/8] CARDAPIO E PRODUTOS")
    endpoints = [
        (f"{BASE}/cardapio",           "cardapio"),
        (f"{BASE}/produto",            "produto"),
        (f"{BASE}/produtos",           "produtos"),
        (f"{BASE}/menu/items",         "menu items"),
        (f"{BASE}/v2/cardapio",        "cardapio v2"),
        (f"{BASE}/items/cardapio",     "items cardapio"),
        (f"{BASE}/produto/lista",      "produto lista"),
        (f"{BASE}/categorias",         "categorias"),
        (f"{BASE}/categoria",          "categoria"),
    ]
    for url, desc in endpoints:
        d = get(s, url, desc)
        if d and len(str(d)) > 50:
            resultados["cardapio"] = d
            salvar("cardapio", d)
            break

    # Ficha tecnica / CMV
    ft_endpoints = [
        (f"{BASE}/ficha-tecnica",          "ficha-tecnica"),
        (f"{BASE}/fichatecnica",           "fichatecnica"),
        (f"{BASE}/insumos/fichas",         "insumos fichas"),
        (f"{BASE}/cmv/produtos",           "cmv produtos"),
        (f"{BASE}/cmv",                    "cmv"),
        (f"{BASE}/receitas",               "receitas"),
        (f"{BASE}/produto/ficha",          "produto ficha"),
        (f"{BASE}/relatorio/cmv?start={DATA_INICIO}&end={DATA_FIM}", "relatorio cmv"),
    ]
    for url, desc in ft_endpoints:
        d = get(s, url, desc)
        if d and len(str(d)) > 50:
            resultados["fichas_tecnicas"] = d
            salvar("fichas_tecnicas", d)
            break

def coletar_estoque(s):
    print("\n[5/8] ESTOQUE")
    endpoints = [
        (f"{BASE}/estoque",                "estoque"),
        (f"{BASE}/insumos",                "insumos"),
        (f"{BASE}/estoque/insumos",        "estoque insumos"),
        (f"{BASE}/insumos/estoque",        "insumos estoque"),
        (f"{BASE}/insumos/lista",          "insumos lista"),
        (f"{BASE}/v2/estoque",             "estoque v2"),
        (f"{BASE}/estoque/lista",          "estoque lista"),
        (f"{BASE}/almoxarifado",           "almoxarifado"),
        (f"{BASE}/insumo",                 "insumo"),
    ]
    for url, desc in endpoints:
        d = get(s, url, desc)
        if d and len(str(d)) > 50:
            resultados["estoque"] = d
            salvar("estoque", d)
            break

    # Estoque minimo / critico
    critico_endpoints = [
        f"{BASE}/estoque/critico",
        f"{BASE}/insumos/abaixo-minimo",
        f"{BASE}/estoque/alerta",
    ]
    for url in critico_endpoints:
        d = get(s, url, "estoque critico")
        if d:
            resultados["estoque_critico"] = d
            salvar("estoque_critico", d)
            break

def coletar_financeiro(s):
    print("\n[6/8] FINANCEIRO")

    # Contas a pagar
    for url in [
        f"{BASE}/contas-pagar?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/contas-pagar?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/despesas?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/lancamentos?tipo=pagar&start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/despesas?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/contas?tipo=pagar&start={DATA_INICIO}&end={DATA_FIM}",
    ]:
        d = get(s, url, "contas a pagar")
        if d and len(str(d)) > 20:
            resultados["contas_pagar"] = d
            salvar("contas_pagar", d)
            break

    # Contas a receber
    for url in [
        f"{BASE}/contas-receber?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/contas-receber?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/receitas-financeiro?start={DATA_INICIO}&end={DATA_FIM}",
    ]:
        d = get(s, url, "contas a receber")
        if d and len(str(d)) > 20:
            resultados["contas_receber"] = d
            salvar("contas_receber", d)
            break

    # Fluxo de caixa
    for url in [
        f"{BASE}/fluxo-caixa?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/fluxo-caixa?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/caixa?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/caixa?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/resumo?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/long/financeiro?start={DATA_INICIO}&end={DATA_FIM}",
    ]:
        d = get(s, url, "fluxo de caixa")
        if d and len(str(d)) > 20:
            resultados["fluxo_caixa"] = d
            salvar("fluxo_caixa", d)
            break

    # Despesas por categoria
    for url in [
        f"{BASE}/despesas/categoria?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/categorias?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/categorias-despesa?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/relatorio/despesas?start={DATA_INICIO}&end={DATA_FIM}",
    ]:
        d = get(s, url, "despesas categoria")
        if d and len(str(d)) > 20:
            resultados["despesas_categoria"] = d
            salvar("despesas_categoria", d)
            break

def coletar_compras_fornecedores(s):
    print("\n[7/8] COMPRAS E FORNECEDORES")
    for url in [
        f"{BASE}/fornecedores",
        f"{BASE}/suppliers",
        f"{BASE}/fornecedor",
        f"{BASE}/compras/fornecedores",
    ]:
        d = get(s, url, "fornecedores")
        if d and len(str(d)) > 20:
            resultados["fornecedores"] = d
            salvar("fornecedores", d)
            break

    for url in [
        f"{BASE}/compras?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/pedidos-compra?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/financeiro/compras?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/ordem-compra?start={DATA_INICIO}&end={DATA_FIM}",
        f"{BASE}/compra?start={DATA_INICIO}&end={DATA_FIM}",
    ]:
        d = get(s, url, "historico compras")
        if d and len(str(d)) > 20:
            resultados["compras"] = d
            salvar("compras", d)
            break

def coletar_configuracoes(s):
    print("\n[8/8] CONFIGURACOES")
    cfgs = {}
    for url, desc in [
        (f"{BASE}/configs",              "configs"),
        (f"{BASE}/delivery/store/details","store details"),
        (f"{BASE}/franchises",           "franchises"),
        (f"{BASE}/usuarios/authenticated","usuario autenticado"),
        (f"{BASE}/v2/billing/status",    "billing status"),
        (f"{BASE}/configs/tokens/fiscal","token fiscal"),
    ]:
        d = get(s, url, desc)
        if d:
            cfgs[desc] = d
    if cfgs:
        resultados["configuracoes"] = cfgs
        salvar("configuracoes", cfgs)

# ──────────────────────────────────────────────
# 4. Main
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  COLETOR API YOOGA - Village Gourmet")
    print(f"  Periodo: {DATA_INICIO} a {DATA_FIM}")
    print("=" * 60)

    token, idi = extrair_token()

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
        "Origin":        "https://painel.yooga.com.br",
        "Referer":       "https://painel.yooga.com.br/",
        "x-franchise-id": str(idi or ""),
    })

    coletar_dashboard(session)
    coletar_vendas_diarias(session)
    coletar_vendas_produtos(session)
    coletar_cardapio(session)
    coletar_estoque(session)
    coletar_financeiro(session)
    coletar_compras_fornecedores(session)
    coletar_configuracoes(session)

    print("\n" + "=" * 60)
    print("  RELATORIO FINAL")
    print("=" * 60)
    print(f"\nSecoes coletadas: {len(resultados)}")
    for k, v in resultados.items():
        n = len(v) if isinstance(v, list) else len(str(v))
        print(f"  [OK] {k:35s} {n:>8} {'registros' if isinstance(v,list) else 'chars'}")

    unicos = list({e["url"] for e in erros})
    print(f"\nEndpoints sem resposta: {len(unicos)}")

    salvar("_relatorio_coleta", {
        "periodo": {"inicio": DATA_INICIO, "fim": DATA_FIM},
        "secoes_coletadas": list(resultados.keys()),
        "endpoints_sem_resposta": unicos,
    })
    print(f"\nArquivos em: {PASTA}")

if __name__ == "__main__":
    main()
