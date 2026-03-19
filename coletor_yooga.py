"""
Coletor de dados Yooga - Village Gourmet
Conecta ao Chrome já autenticado via CDP (porta 9222)
"""
import json
import re
from datetime import date
from pathlib import Path
from playwright.sync_api import sync_playwright

PASTA_DADOS = Path.home() / "village-gourmet" / "dados"
PASTA_DADOS.mkdir(parents=True, exist_ok=True)
HOJE = date.today().strftime("%Y-%m-%d")
ARQUIVO_SAIDA = PASTA_DADOS / f"{HOJE}.json"

resultado = {
    "data": date.today().strftime("%d/%m/%Y"),
    "faturamento_bruto": 0,
    "total_pedidos": 0,
    "ticket_medio": 0,
    "top_produtos": [],
    "total_despesas": 0,
    "saldo_caixa": 0,
    "estoque_critico": []
}

def limpar_valor(texto):
    """Converte 'R$ 1.234,56' para float 1234.56"""
    if not texto:
        return 0.0
    texto = re.sub(r"[R$\s]", "", texto)
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except:
        return 0.0

def coletar_dashboard(page):
    print("\n[1/3] Coletando dashboard...")
    page.goto("https://painel.yooga.com.br", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    # Tenta capturar os cards do dashboard por texto
    cards = page.query_selector_all("[class*='card'], [class*='resumo'], [class*='stat'], [class*='metric']")
    print(f"    {len(cards)} cards encontrados na tela")

    # Captura screenshot para referência
    screenshot = PASTA_DADOS / f"{HOJE}_dashboard.png"
    page.screenshot(path=str(screenshot))
    print(f"    Screenshot salvo: {screenshot}")

    # Tenta extrair texto de todos os elementos visíveis com valor monetário
    body_text = page.inner_text("body")

    # Busca padrões de valores monetários no texto da página
    valores = re.findall(r"R\$\s*[\d.,]+", body_text)
    numeros = re.findall(r"\b\d+\b", body_text)

    print(f"    Valores monetários encontrados: {valores[:10]}")

    return body_text

def coletar_estoque(page):
    print("\n[2/3] Coletando estoque crítico...")

    # Tenta navegar para seção de estoque
    urls_estoque = [
        "https://painel.yooga.com.br/estoque",
        "https://painel.yooga.com.br/#/estoque",
        "https://painel.yooga.com.br/insumos",
    ]

    for url in urls_estoque:
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(2000)
            titulo = page.title()
            print(f"    Tentativa {url} → título: {titulo}")
            break
        except:
            continue

    screenshot = PASTA_DADOS / f"{HOJE}_estoque.png"
    page.screenshot(path=str(screenshot))
    print(f"    Screenshot salvo: {screenshot}")

    return page.inner_text("body")

def coletar_via_rede(page):
    """Intercepta chamadas de API para capturar dados estruturados"""
    print("\n[3/3] Monitorando chamadas de API...")
    dados_api = []

    def capturar_resposta(response):
        if "api" in response.url.lower() or "yooga" in response.url.lower():
            try:
                if response.status == 200:
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        dados = response.json()
                        dados_api.append({"url": response.url, "dados": dados})
                        print(f"    API: {response.url[:80]}")
            except:
                pass

    page.on("response", capturar_resposta)
    page.goto("https://painel.yooga.com.br", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(3000)

    return dados_api

def main():
    print("=" * 60)
    print("  COLETOR YOOGA - Village Gourmet")
    print(f"  Data: {resultado['data']}")
    print("=" * 60)
    print("\nConectando ao Chrome na porta 9222...")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Conectado ao Chrome com sucesso!")
        except Exception as e:
            print(f"\nERRO: Não foi possível conectar ao Chrome.")
            print(f"Detalhe: {e}")
            print("\nCertifique-se de que o Chrome foi aberto com:")
            print('  chrome --remote-debugging-port=9222')
            return

        # Usa a primeira aba existente ou abre nova
        contexts = browser.contexts
        if contexts and contexts[0].pages:
            page = contexts[0].pages[0]
            print(f"Usando aba existente: {page.url}")
        else:
            context = browser.new_context()
            page = context.new_page()

        # Verifica se está logado
        page.goto("https://painel.yooga.com.br", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        url_atual = page.url
        print(f"URL atual: {url_atual}")

        if "login" in url_atual.lower() or "auth" in url_atual.lower():
            print("\nAINDA NÃO LOGADO. Faça login no Chrome e execute novamente.")
            page.screenshot(path=str(PASTA_DADOS / f"{HOJE}_login_necessario.png"))
            return

        print("Sessão autenticada detectada!")

        # Coleta dados via API interceptada
        dados_api = coletar_via_rede(page)

        # Salva dados de API brutos se encontrou algo
        if dados_api:
            arquivo_api = PASTA_DADOS / f"{HOJE}_api_raw.json"
            with open(arquivo_api, "w", encoding="utf-8") as f:
                json.dump(dados_api, f, ensure_ascii=False, indent=2)
            print(f"\n{len(dados_api)} chamadas de API capturadas -> {arquivo_api}")

        # Coleta texto do dashboard
        texto_dashboard = coletar_dashboard(page)

        # Coleta estoque
        texto_estoque = coletar_estoque(page)

        # Salva resultado consolidado
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print(f"  COLETA CONCLUÍDA")
        print(f"  Arquivo: {ARQUIVO_SAIDA}")
        print("=" * 60)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
