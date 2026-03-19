"""
Coletor completo Yooga - Village Gourmet
Periodo: 01/03/2026 a 19/03/2026
"""
import json
import time
from datetime import date
from pathlib import Path
from playwright.sync_api import sync_playwright

PASTA = Path("C:/Users/WILLIAM/village-gourmet/dados")
PASTA.mkdir(parents=True, exist_ok=True)
DATA_INICIO = "2026-03-01"
DATA_FIM    = "2026-03-19"
BASE_API    = "https://report.yooga.com.br"

dados_coletados = {}
erros = []

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def salvar(nome, conteudo):
    arquivo = PASTA / f"{nome}.json"
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)
    print(f"  [SALVO] {arquivo.name}  ({len(str(conteudo))} chars)")

def get_json(page, url, descricao=""):
    """Faz fetch autenticado usando o contexto do browser logado."""
    try:
        result = page.evaluate(f"""
            async () => {{
                const r = await fetch('{url}', {{
                    credentials: 'include',
                    headers: {{ 'Accept': 'application/json' }}
                }});
                if (!r.ok) return {{ _erro: r.status, _url: '{url}' }};
                return await r.json();
            }}
        """)
        if result and '_erro' not in result:
            print(f"  [OK] {descricao or url}")
            return result
        else:
            print(f"  [ERRO {result.get('_erro','?')}] {descricao or url}")
            erros.append({"url": url, "status": result.get('_erro')})
            return None
    except Exception as e:
        print(f"  [EXCECAO] {url}: {e}")
        erros.append({"url": url, "erro": str(e)})
        return None

def navegar_e_capturar(page, url_painel, descricao, espera=4000):
    """Navega para uma seção e captura todas as APIs chamadas."""
    capturadas = []

    def on_response(response):
        if ("report.yooga" in response.url or "api.yooga" in response.url):
            try:
                if response.status == 200:
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        d = response.json()
                        capturadas.append({"url": response.url, "dados": d})
            except:
                pass

    page.on("response", on_response)
    try:
        page.goto(url_painel, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(espera)
    except:
        page.wait_for_timeout(espera)
    page.remove_listener("response", on_response)
    print(f"  Navegacao '{descricao}': {len(capturadas)} APIs capturadas")
    return capturadas

# ──────────────────────────────────────────────
# Secoes de coleta
# ──────────────────────────────────────────────

def coletar_dashboard(page):
    print("\n[1/8] DASHBOARD")
    d = get_json(page,
        f"{BASE_API}/long/cabecalho?start={DATA_INICIO}&end={DATA_FIM}",
        "cabecalho geral")
    if d:
        dados_coletados["dashboard"] = d
        salvar("dashboard", d)

def coletar_vendas_diarias(page):
    print("\n[2/8] VENDAS DIARIAS")
    # Relatório por dia
    d = get_json(page,
        f"{BASE_API}/long/vendas-dia?start={DATA_INICIO}&end={DATA_FIM}",
        "vendas por dia")
    if not d:
        d = get_json(page,
            f"{BASE_API}/relatorio/vendas?start={DATA_INICIO}&end={DATA_FIM}&group=day",
            "vendas por dia (v2)")
    if not d:
        # Tenta capturar via navegação
        caps = navegar_e_capturar(page,
            f"https://painel.yooga.com.br/relatorio/vendas?start={DATA_INICIO}&end={DATA_FIM}",
            "relatorio vendas")
        for c in caps:
            if "venda" in c["url"].lower() or "relatorio" in c["url"].lower():
                d = c["dados"]
                break
    if d:
        dados_coletados["vendas_diarias"] = d
        salvar("vendas_diarias", d)

def coletar_vendas_produtos(page):
    print("\n[3/8] VENDAS POR PRODUTO")
    d = get_json(page,
        f"{BASE_API}/long/produtos?start={DATA_INICIO}&end={DATA_FIM}",
        "produtos vendidos")
    if not d:
        d = get_json(page,
            f"{BASE_API}/relatorio/produtos?start={DATA_INICIO}&end={DATA_FIM}",
            "produtos (v2)")
    if not d:
        # Usa dados do cabecalho já coletado
        if "dashboard" in dados_coletados:
            cab = dados_coletados["dashboard"]
            labels = cab.get("chart_produto_labels", [])
            qtds   = cab.get("chart_produto_data", [])
            d = [{"produto": l, "quantidade": q} for l, q in zip(labels, qtds)]
            d.sort(key=lambda x: x["quantidade"], reverse=True)
            print("  [OK] produtos extraidos do dashboard")
    if d:
        dados_coletados["vendas_produtos"] = d
        salvar("vendas_produtos", d)

def coletar_cardapio(page):
    print("\n[4/8] CARDAPIO / FICHAS TECNICAS")
    # Tenta endpoints conhecidos
    endpoints = [
        (f"{BASE_API}/cardapio", "cardapio"),
        (f"{BASE_API}/produtos", "produtos"),
        (f"{BASE_API}/menu", "menu"),
        (f"{BASE_API}/items", "items"),
        (f"{BASE_API}/produto/lista", "produto lista"),
        (f"{BASE_API}/v2/produtos", "produtos v2"),
    ]
    for url, desc in endpoints:
        d = get_json(page, url, desc)
        if d:
            dados_coletados["cardapio"] = d
            salvar("cardapio", d)
            break

    # Ficha tecnica
    ft_endpoints = [
        (f"{BASE_API}/ficha-tecnica", "ficha tecnica"),
        (f"{BASE_API}/fichas", "fichas"),
        (f"{BASE_API}/insumos/fichas", "insumos fichas"),
        (f"{BASE_API}/cmv", "cmv"),
    ]
    for url, desc in ft_endpoints:
        d = get_json(page, url, desc)
        if d:
            dados_coletados["fichas_tecnicas"] = d
            salvar("fichas_tecnicas", d)
            break

    # Navega para cardapio e captura
    caps = navegar_e_capturar(page,
        "https://painel.yooga.com.br/cardapio",
        "pagina cardapio", espera=5000)
    if caps:
        dados_coletados["cardapio_navegacao"] = caps
        salvar("cardapio_navegacao", caps)

def coletar_estoque(page):
    print("\n[5/8] ESTOQUE")
    endpoints = [
        (f"{BASE_API}/estoque", "estoque"),
        (f"{BASE_API}/insumos", "insumos"),
        (f"{BASE_API}/insumos/estoque", "insumos estoque"),
        (f"{BASE_API}/estoque/insumos", "estoque insumos"),
        (f"{BASE_API}/v2/estoque", "estoque v2"),
        (f"{BASE_API}/insumos/lista", "insumos lista"),
        (f"{BASE_API}/estoque/lista", "estoque lista"),
    ]
    for url, desc in endpoints:
        d = get_json(page, url, desc)
        if d and isinstance(d, (list, dict)) and len(d) > 0:
            dados_coletados["estoque"] = d
            salvar("estoque", d)
            break

    # Navega para estoque
    caps = navegar_e_capturar(page,
        "https://painel.yooga.com.br/estoque",
        "pagina estoque", espera=5000)
    estoque_caps = [c for c in caps if any(k in c["url"].lower()
        for k in ["estoque", "insumo", "stock"])]
    if estoque_caps:
        dados_coletados["estoque_navegacao"] = estoque_caps
        salvar("estoque_navegacao", estoque_caps)
        print(f"  {len(estoque_caps)} APIs de estoque capturadas na navegacao")

def coletar_financeiro(page):
    print("\n[6/8] FINANCEIRO")
    secoes = {
        "contas_pagar": [
            f"{BASE_API}/financeiro/contas-pagar?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/contas-pagar?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/financeiro/despesas?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/despesas?start={DATA_INICIO}&end={DATA_FIM}",
        ],
        "contas_receber": [
            f"{BASE_API}/financeiro/contas-receber?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/contas-receber?start={DATA_INICIO}&end={DATA_FIM}",
        ],
        "fluxo_caixa": [
            f"{BASE_API}/financeiro/fluxo-caixa?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/fluxo-caixa?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/caixa?start={DATA_INICIO}&end={DATA_FIM}",
            f"{BASE_API}/financeiro/caixa?start={DATA_INICIO}&end={DATA_FIM}",
        ],
    }
    for secao, urls in secoes.items():
        for url in urls:
            d = get_json(page, url, secao)
            if d and len(str(d)) > 10:
                dados_coletados[secao] = d
                salvar(secao, d)
                break

    # Navega para financeiro e captura tudo
    caps = navegar_e_capturar(page,
        "https://painel.yooga.com.br/financeiro",
        "pagina financeiro", espera=5000)
    fin_caps = [c for c in caps if any(k in c["url"].lower()
        for k in ["financeiro", "caixa", "despesa", "pagar", "receber"])]
    if fin_caps:
        dados_coletados["financeiro_navegacao"] = fin_caps
        salvar("financeiro_navegacao", fin_caps)
        print(f"  {len(fin_caps)} APIs financeiras capturadas na navegacao")

def coletar_compras_fornecedores(page):
    print("\n[7/8] COMPRAS E FORNECEDORES")
    endpoints_fornecedores = [
        (f"{BASE_API}/fornecedores", "fornecedores"),
        (f"{BASE_API}/suppliers", "suppliers"),
        (f"{BASE_API}/compras/fornecedores", "compras fornecedores"),
    ]
    for url, desc in endpoints_fornecedores:
        d = get_json(page, url, desc)
        if d and len(str(d)) > 10:
            dados_coletados["fornecedores"] = d
            salvar("fornecedores", d)
            break

    endpoints_compras = [
        (f"{BASE_API}/compras?start={DATA_INICIO}&end={DATA_FIM}", "compras"),
        (f"{BASE_API}/pedidos-compra?start={DATA_INICIO}&end={DATA_FIM}", "pedidos compra"),
        (f"{BASE_API}/financeiro/compras?start={DATA_INICIO}&end={DATA_FIM}", "compras financeiro"),
    ]
    for url, desc in endpoints_compras:
        d = get_json(page, url, desc)
        if d and len(str(d)) > 10:
            dados_coletados["compras"] = d
            salvar("compras", d)
            break

    caps = navegar_e_capturar(page,
        "https://painel.yooga.com.br/compras",
        "pagina compras", espera=5000)
    comp_caps = [c for c in caps if any(k in c["url"].lower()
        for k in ["compra", "fornecedor", "supplier"])]
    if comp_caps:
        dados_coletados["compras_navegacao"] = comp_caps
        salvar("compras_navegacao", comp_caps)

def coletar_configuracoes(page):
    print("\n[8/8] CONFIGURACOES")
    endpoints = [
        (f"{BASE_API}/configs", "configs"),
        (f"{BASE_API}/configuracoes", "configuracoes"),
        (f"{BASE_API}/delivery/store/details", "delivery store"),
        (f"{BASE_API}/franchises", "franchises"),
    ]
    resultados = {}
    for url, desc in endpoints:
        d = get_json(page, url, desc)
        if d:
            resultados[desc] = d
    if resultados:
        dados_coletados["configuracoes"] = resultados
        salvar("configuracoes", resultados)

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  COLETOR COMPLETO YOOGA - Village Gourmet")
    print(f"  Periodo: {DATA_INICIO} a {DATA_FIM}")
    print("=" * 60)

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("\nConectado ao Chrome!\n")
        except Exception as e:
            print(f"ERRO ao conectar: {e}")
            return

        contexts = browser.contexts
        page = contexts[0].pages[0] if contexts and contexts[0].pages else browser.new_context().new_page()

        # Garante que está no painel
        page.goto("https://painel.yooga.com.br/dashboard", wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)

        coletar_dashboard(page)
        coletar_vendas_diarias(page)
        coletar_vendas_produtos(page)
        coletar_cardapio(page)
        coletar_estoque(page)
        coletar_financeiro(page)
        coletar_compras_fornecedores(page)
        coletar_configuracoes(page)

    # Relatorio final
    print("\n" + "=" * 60)
    print("  RELATORIO FINAL")
    print("=" * 60)
    print(f"\nSecoes coletadas com sucesso ({len(dados_coletados)}):")
    for k in dados_coletados:
        tamanho = len(json.dumps(dados_coletados[k], ensure_ascii=False))
        print(f"  [OK] {k:35s} {tamanho:>8} bytes")

    if erros:
        print(f"\nSecoes com problema ({len(erros)}):")
        vistos = set()
        for e in erros:
            u = e['url']
            if u not in vistos:
                vistos.add(u)
                print(f"  [ERRO] {u}")

    salvar("_relatorio_coleta", {
        "periodo": {"inicio": DATA_INICIO, "fim": DATA_FIM},
        "secoes_coletadas": list(dados_coletados.keys()),
        "total_erros": len(erros),
        "erros": erros[:20]
    })
    print(f"\nTodos os arquivos salvos em: {PASTA}")

if __name__ == "__main__":
    main()
