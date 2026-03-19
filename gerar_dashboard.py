"""
Gera o dashboard HTML completo com dados embarcados
"""
import json
from pathlib import Path

DADOS = Path("C:/Users/WILLIAM/village-gourmet/dados")
OUT   = Path("C:/Users/WILLIAM/village-gourmet/dashboard/index.html")

def ler(arq, default=None):
    try:
        with open(DADOS / arq, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

dash     = ler("dashboard.json")
vpd      = ler("vendas_por_dia.json", [])
prods_v3 = ler("produtos_estoque_v3.json", [])
estoque  = ler("estoque_minimo.json", {"categorias": []})
extrato  = ler("extrato_mensal.json", [])
ext_opt  = ler("extrato_opcoes.json", {})
fluxo    = ler("fluxo_caixa_diario.json", [])
dre_raw  = ler("dre.json", {"dre": []})
cats     = ler("categorias.json", [])
fornec   = ler("fornecedores_completo.json", [])
caixas   = ler("caixas.json", {})
cardapio = ler("cardapio_completo.json", [])
notas_f   = ler("notas_fiscais.json", {})
notas_cmp = ler("notas_compra.json", [])

prods_card = []
if cardapio and isinstance(cardapio, list) and cardapio[0].get("data"):
    prods_card = cardapio[0]["data"]
else:
    prods_card = prods_v3

def js(obj):
    return json.dumps(obj, ensure_ascii=False)

# Bloco de dados — usa f-string apenas aqui
DATA_JS = f"""
const DASH   = {js(dash)};
const VPD    = {js(vpd)};
const PRODS  = {js(prods_card)};
const ESTMIN = {js(estoque)};
const EXTRATO= {js(extrato)};
const EXTOPT = {js(ext_opt)};
const FLUXO  = {js(fluxo)};
const DRE    = {js(dre_raw)};
const CATS   = {js(cats)};
const FORNEC = {js(fornec)};
const CAIXAS = {js(caixas)};
const NOTAS  = {js(notas_f)};
const NOTAS_COMPRA = {js(notas_cmp)};
"""

# HTML/CSS/JS — string normal, sem f-string
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Village Gourmet — Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--bg2:#1a1d27;--bg3:#252836;--border:#2e3347;
  --text:#e2e8f0;--text2:#94a3b8;--accent:#6366f1;--accent2:#818cf8;
  --green:#22c55e;--red:#ef4444;--yellow:#f59e0b;--blue:#3b82f6;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh}
.topbar{background:var(--bg2);border-bottom:1px solid var(--border);padding:0 20px;display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:100;flex-wrap:wrap}
.logo{font-size:1.05rem;font-weight:700;color:var(--accent2);padding:14px 0;white-space:nowrap}
.logo span{color:var(--text2);font-weight:400}
.nav-tabs{display:flex;gap:2px;overflow-x:auto;flex:1}
.nav-tab{padding:14px 16px;color:var(--text2);cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;font-size:.85rem;transition:.2s;user-select:none}
.nav-tab:hover{color:var(--text)}
.nav-tab.active{color:var(--accent2);border-bottom-color:var(--accent)}
.refresh-btn{background:var(--accent);color:#fff;border:none;padding:7px 14px;border-radius:8px;cursor:pointer;font-size:.78rem;white-space:nowrap}
.refresh-btn:hover{background:var(--accent2)}
.page{display:none;padding:20px;max-width:1400px;margin:0 auto}
.page.active{display:block}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:20px}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:18px}
.card-label{font-size:.72rem;color:var(--text2);text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}
.card-value{font-size:1.5rem;font-weight:700}
.card-sub{font-size:.75rem;color:var(--text2);margin-top:3px}
.card-icon{font-size:1.4rem;float:right;opacity:.5}
.card.green .card-value{color:var(--green)}
.card.red .card-value{color:var(--red)}
.card.yellow .card-value{color:var(--yellow)}
.card.blue .card-value{color:var(--blue)}
.section{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:18px}
.section-title{font-size:.8rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.05em;margin-bottom:14px;display:flex;align-items:center;gap:7px}
.section-title::before{content:'';width:3px;height:13px;background:var(--accent);border-radius:2px;display:inline-block}
.chart-wrap{width:100%;overflow-x:auto}
canvas{display:block;max-width:100%}
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{text-align:left;padding:9px 11px;color:var(--text2);font-weight:500;border-bottom:1px solid var(--border);font-size:.72rem;text-transform:uppercase;letter-spacing:.04em}
td{padding:9px 11px;border-bottom:1px solid var(--border);color:var(--text)}
tr:hover td{background:var(--bg3)}
tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:2px 7px;border-radius:20px;font-size:.68rem;font-weight:600}
.badge-ok{background:#16a34a22;color:var(--green)}
.badge-warn{background:#d9770622;color:var(--yellow)}
.badge-crit{background:#dc262622;color:var(--red)}
.badge-info{background:#1d4ed822;color:var(--blue)}
.alert{background:#7c2d1222;border:1px solid #f97316;border-radius:8px;padding:11px 14px;margin-bottom:18px;color:#fb923c;font-size:.85rem}
.alert strong{color:#f97316}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:768px){.grid2{grid-template-columns:1fr}}
.prog-wrap{background:var(--bg3);border-radius:4px;height:7px;margin-top:4px;overflow:hidden}
.prog-bar{height:100%;border-radius:4px}
.chat-wrap{display:flex;flex-direction:column;height:calc(100vh - 155px);min-height:480px}
.chat-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:82%;padding:11px 15px;border-radius:12px;font-size:.85rem;line-height:1.6}
.msg.user{background:var(--accent);color:#fff;align-self:flex-end;border-radius:12px 12px 2px 12px}
.msg.agent{background:var(--bg3);color:var(--text);align-self:flex-start;border-radius:12px 12px 12px 2px}
.msg.agent strong{color:var(--accent2)}
.chat-input-row{display:flex;gap:9px;padding:14px;border-top:1px solid var(--border)}
.chat-input{flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:11px 14px;color:var(--text);font-size:.85rem;outline:none;resize:none;height:46px}
.chat-input:focus{border-color:var(--accent)}
.chat-send{background:var(--accent);color:#fff;border:none;padding:11px 18px;border-radius:10px;cursor:pointer;font-size:.85rem}
.chat-send:hover{background:var(--accent2)}
.suggestions{display:flex;flex-wrap:wrap;gap:7px;padding:0 14px 10px}
.sug-btn{background:var(--bg3);border:1px solid var(--border);color:var(--text2);padding:5px 11px;border-radius:20px;cursor:pointer;font-size:.72rem;transition:.2s}
.sug-btn:hover{border-color:var(--accent);color:var(--text)}
.dre-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border)}
.dre-row:last-child{border-bottom:none}
.dre-row.result{background:var(--bg3);padding:7px 11px;border-radius:6px;margin:3px -11px;border-bottom:none;margin-top:4px}
.dre-row.result-final{background:linear-gradient(90deg,var(--accent)18,transparent);border:1px solid var(--accent);padding:9px 11px;border-radius:8px;margin:6px -11px;border-bottom:none}
.dre-row.section-sep{border-bottom:2px solid var(--border);margin-bottom:4px}
.dre-label{flex:1;font-size:.83rem}
.dre-pct{font-size:.72rem;color:var(--text2);width:48px;text-align:right;margin-right:10px}
.dre-value{font-weight:600;min-width:110px;text-align:right}
.dre-value.pos{color:var(--green)}
.dre-value.neg{color:var(--red)}
.dre-indent{padding-left:14px;opacity:.85}
.rank-item{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--border)}
.rank-item:last-child{border-bottom:none}
.rank-num{width:26px;height:26px;background:var(--bg3);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;color:var(--text2);flex-shrink:0}
.rank-num.top{background:var(--accent);color:#fff}
.rank-name{flex:1;font-size:.85rem}
.rank-val{font-size:.85rem;font-weight:600;color:var(--accent2)}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
/* PRECIFICAÇÃO */
.config-panel{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:16px 20px;margin-bottom:18px;display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end}
.config-panel label{font-size:.75rem;color:var(--text2);display:block;margin-bottom:5px;text-transform:uppercase;letter-spacing:.04em}
.config-panel input[type=number],.config-panel select{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--text);font-size:.9rem;width:160px;outline:none}
.config-panel input[type=number]:focus,.config-panel select:focus{border-color:var(--accent)}
.config-panel .cfg-group{display:flex;flex-direction:column}
.config-apply{background:var(--accent);color:#fff;border:none;padding:8px 18px;border-radius:8px;cursor:pointer;font-size:.82rem;align-self:flex-end;height:38px}
.config-apply:hover{background:var(--accent2)}
.tax-breakdown{font-size:.7rem;color:var(--text2);margin-top:3px}
.price-tag{display:inline-block;padding:3px 9px;border-radius:6px;font-weight:700;font-size:.82rem}
.price-up{background:#16a34a22;color:var(--green)}
.price-down{background:#dc262622;color:var(--red)}
.price-ok{background:#1d4ed822;color:var(--blue)}
.imposto-badge{background:#7c3aed22;color:#a78bfa;display:inline-block;padding:2px 7px;border-radius:20px;font-size:.68rem;font-weight:600}
/* DESPESAS FIXAS */
.desp-form{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin-bottom:18px}
.desp-form .form-row{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}
.form-group{display:flex;flex-direction:column;gap:4px}
.form-group label{font-size:.72rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em}
.form-group input,.form-group select{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--text);font-size:.88rem;outline:none}
.form-group input:focus,.form-group select:focus{border-color:var(--accent)}
.form-group input{width:180px}
.form-group select{width:180px}
.btn-add{background:var(--green);color:#fff;border:none;padding:8px 18px;border-radius:8px;cursor:pointer;font-size:.82rem;height:38px}
.btn-add:hover{background:#16a34a}
.btn-del{background:none;border:none;color:var(--red);cursor:pointer;font-size:.9rem;padding:4px 8px;border-radius:6px}
.btn-del:hover{background:#dc262622}
.btn-edit{background:none;border:none;color:var(--blue);cursor:pointer;font-size:.85rem;padding:4px 8px;border-radius:6px}
.btn-edit:hover{background:#1d4ed822}
.cat-icon{font-size:1.1rem;margin-right:5px}
/* IMPOSTOS */
.tax-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:14px}
.tax-card-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.tax-name{font-size:.9rem;font-weight:600}
.tax-aliq{font-size:.75rem;color:var(--text2);background:var(--bg3);padding:3px 10px;border-radius:20px}
.tax-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);font-size:.83rem}
.tax-row:last-child{border-bottom:none}
.tax-total-row{display:flex;justify-content:space-between;padding:10px 0 2px;font-weight:700;font-size:.92rem;border-top:2px solid var(--border);margin-top:6px}
.venc-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:600}
.venc-ok{background:#16a34a22;color:var(--green)}
.venc-warn{background:#d9770622;color:var(--yellow)}
.venc-venc{background:#dc262622;color:var(--red)}
.tax-timeline{display:flex;flex-wrap:wrap;gap:10px;margin-top:4px}
.tl-item{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:12px 14px;min-width:160px;flex:1}
.tl-item.vencido{border-color:var(--red)}
.tl-item.proximo{border-color:var(--yellow)}
.tl-item.ok{border-color:var(--green)}
.tl-label{font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.tl-value{font-size:1.1rem;font-weight:700}
.tl-date{font-size:.72rem;color:var(--text2);margin-top:2px}
/* NOTAS FISCAIS */
.nf-resumo-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:20px}
.nf-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px}
.nf-card-label{font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
.nf-card-value{font-size:1.6rem;font-weight:700}
.nf-card-sub{font-size:.75rem;color:var(--text2);margin-top:4px}
.nf-card.saida .nf-card-value{color:var(--blue)}
.nf-card.entrada .nf-card-value{color:var(--green)}
.nf-card.total .nf-card-value{color:var(--accent2)}
.nf-detail-toggle{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px 16px;cursor:pointer;font-size:.82rem;color:var(--text2);transition:.2s;display:inline-flex;align-items:center;gap:6px}
.nf-detail-toggle:hover{border-color:var(--accent);color:var(--text)}
.nf-detail-toggle.active{border-color:var(--accent);color:var(--accent2);background:var(--bg2)}
.nf-detail-block{display:none;margin-top:12px}
.nf-detail-block.visible{display:block}
.nf-type-label{display:inline-block;padding:2px 8px;border-radius:12px;font-size:.7rem;font-weight:600;margin-right:4px}
.nf-type-nfce{background:#1d4ed822;color:var(--blue)}
.nf-type-nfe{background:#7c3aed22;color:#a78bfa}
.nf-type-entrada{background:#16a34a22;color:var(--green)}
</style>
</head>
<body>

<div class="topbar">
  <div class="logo">&#127869; Village <span>Gourmet</span></div>
  <nav class="nav-tabs">
    <div class="nav-tab active" onclick="showTab('visao',this)">&#128200; Visão Geral</div>
    <div class="nav-tab" onclick="showTab('financeiro',this)">&#128178; Financeiro</div>
    <div class="nav-tab" onclick="showTab('produtos',this)">&#127829; Produtos</div>
    <div class="nav-tab" onclick="showTab('estoque',this)">&#128230; Estoque</div>
    <div class="nav-tab" onclick="showTab('compras',this)">&#128666; Compras</div>
    <div class="nav-tab" onclick="showTab('precificacao',this)">&#127881; Precificação</div>
    <div class="nav-tab" onclick="showTab('despesas',this)">&#128200; Despesas Fixas</div>
    <div class="nav-tab" onclick="showTab('impostos',this)">&#127981; Impostos</div>
    <div class="nav-tab" onclick="showTab('notas',this)">&#128196; Notas Fiscais</div>
    <div class="nav-tab" onclick="showTab('chat',this)">&#128172; Chat IA</div>
  </nav>
  <button class="refresh-btn" onclick="showRefreshInfo()">&#8635; Atualizar</button>
</div>

<!-- VISÃO GERAL -->
<div id="tab-visao" class="page active">
  <div id="alert-estoque"></div>
  <div class="cards" id="cards-visao"></div>
  <div class="grid2">
    <div class="section">
      <div class="section-title">Faturamento Diário — Março 2026</div>
      <div class="chart-wrap"><canvas id="chart-fat" height="180"></canvas></div>
    </div>
    <div class="section">
      <div class="section-title">Formas de Pagamento (mês)</div>
      <div class="chart-wrap"><canvas id="chart-pag" height="180"></canvas></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">Top 10 Produtos Mais Vendidos — Março</div>
    <div id="top-produtos"></div>
  </div>
</div>

<!-- FINANCEIRO -->
<div id="tab-financeiro" class="page">
  <div class="cards" id="cards-fin"></div>
  <div class="grid2">
    <div class="section">
      <div class="section-title">DRE — Demonstrativo de Resultado — Março 2026</div>
      <div id="dre-content"></div>
    </div>
    <div class="section">
      <div class="section-title">Composição dos Custos</div>
      <div class="chart-wrap" style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
        <canvas id="chart-composicao" height="220" style="max-width:220px"></canvas>
        <div id="composicao-legenda" style="font-size:.8rem;flex:1;min-width:160px"></div>
      </div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">Fluxo de Caixa — Saldo Acumulado Diário</div>
    <div class="chart-wrap"><canvas id="chart-fluxo" height="200"></canvas></div>
  </div>
  <div class="section">
    <div class="section-title">Lançamentos do Período</div>
    <div class="tbl-wrap"><table id="tbl-lancamentos">
      <thead><tr><th>Data</th><th>Descrição</th><th>Tipo</th><th>Valor</th><th>Status</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
</div>

<!-- PRODUTOS -->
<div id="tab-produtos" class="page">
  <div class="section">
    <div class="section-title">Cardápio Completo — Preço, Custo e Margem</div>
    <div style="display:flex;gap:9px;margin-bottom:11px;flex-wrap:wrap">
      <input id="busca-prod" type="text" placeholder="Buscar produto..." oninput="filtrarProdutos()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem;width:240px">
      <select id="sort-prod" onchange="filtrarProdutos()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
        <option value="ranking">Mais Vendidos</option>
        <option value="margem_asc">Menor Margem</option>
        <option value="margem_desc">Maior Margem</option>
        <option value="preco_desc">Maior Preço</option>
        <option value="nome">Nome A-Z</option>
      </select>
    </div>
    <div class="tbl-wrap"><table id="tbl-produtos">
      <thead><tr><th>Produto</th><th>Categoria</th><th>Preço Venda</th><th>Custo (CMV)</th><th>CMV %</th><th>CMV c/ Imposto</th><th>Margem Líquida</th><th>Ranking</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
  <div class="grid2">
    <div class="section">
      <div class="section-title">&#127942; Top 10 Mais Vendidos no Mês</div>
      <div id="rank-vendidos"></div>
    </div>
    <div class="section">
      <div class="section-title">&#9888; Margem Abaixo de 60%</div>
      <div id="margem-baixa"></div>
    </div>
  </div>
</div>

<!-- ESTOQUE -->
<div id="tab-estoque" class="page">
  <div class="cards" id="cards-est"></div>
  <div class="section">
    <div class="section-title">Status do Estoque</div>
    <div style="display:flex;gap:7px;margin-bottom:11px;flex-wrap:wrap">
      <button onclick="filtroEst='todos';renderEstoque()" class="sug-btn">Todos</button>
      <button onclick="filtroEst='critico';renderEstoque()" class="sug-btn" style="color:var(--red)">&#128680; Crítico</button>
      <button onclick="filtroEst='atencao';renderEstoque()" class="sug-btn" style="color:var(--yellow)">&#9888; Atenção</button>
      <button onclick="filtroEst='ok';renderEstoque()" class="sug-btn" style="color:var(--green)">&#9989; OK</button>
    </div>
    <div class="tbl-wrap"><table id="tbl-estoque">
      <thead><tr><th>Produto</th><th>Categoria</th><th>Estoque Atual</th><th>Mínimo</th><th>Status</th><th>Ação</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
</div>

<!-- COMPRAS -->
<div id="tab-compras" class="page">
  <div class="cards" id="cards-comp"></div>
  <div class="grid2">
    <div class="section">
      <div class="section-title">&#128666; Compras por Fornecedor — Notas Fiscais</div>
      <div id="comp-por-fornec"></div>
    </div>
    <div class="section">
      <div class="section-title">&#128197; Compras por Dia — Março 2026</div>
      <div class="chart-wrap"><canvas id="chart-compras-dia" height="200"></canvas></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">&#127981; Notas de Compra Recebidas — Março 2026</div>
    <div style="display:flex;gap:9px;margin-bottom:11px;flex-wrap:wrap">
      <input id="busca-comp" type="text" placeholder="Buscar fornecedor, N&#186; NF..."
        oninput="filtrarCompras()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem;width:240px">
      <select id="flt-comp-forn" onchange="filtrarCompras()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
        <option value="">Todos os fornecedores</option>
      </select>
    </div>
    <div class="tbl-wrap"><table id="tbl-notas-comp">
      <thead><tr><th>Data</th><th>N&#186; NF</th><th>Fornecedor</th><th>CNPJ</th><th>Nat. Operação</th><th>Valor Produtos</th><th>Valor Total NF</th><th>Status</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
  <div class="section">
    <div class="section-title">Histórico de Caixas — Março 2026</div>
    <div class="tbl-wrap"><table id="tbl-caixas">
      <thead><tr><th>Abertura</th><th>Fechamento</th><th>Receita</th><th>Despesa</th><th>Saldo</th><th>Status</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
</div>

<!-- PRECIFICAÇÃO -->
<div id="tab-precificacao" class="page">
  <div class="config-panel">
    <div class="cfg-group">
      <label>Regime Tributário</label>
      <select id="cfg-regime" onchange="onRegimeChange()">
        <option value="simples_1">Simples Nacional — Anexo I (até R$180k) ~4,0%</option>
        <option value="simples_2" selected>Simples Nacional — Anexo I (até R$360k) ~7,3%</option>
        <option value="simples_3">Simples Nacional — Anexo I (até R$720k) ~9,5%</option>
        <option value="presumido">Lucro Presumido (PIS+COFINS+ISS+IR+CS) ~16,3%</option>
        <option value="real">Lucro Real (PIS+COFINS+ISS+IR+CS) ~22,0%</option>
        <option value="custom">Personalizado</option>
      </select>
      <div class="tax-breakdown" id="tax-desc">PIS 0,65% · COFINS 3% · ISS 5% · IRPJ 2% · CSLL 1,08% → aprox. 7,3% efetivo</div>
    </div>
    <div class="cfg-group">
      <label>Alíquota Total (%)</label>
      <input type="number" id="cfg-imposto" value="7.3" min="0" max="50" step="0.1">
    </div>
    <div class="cfg-group">
      <label>Margem de Lucro Desejada (%)</label>
      <input type="number" id="cfg-margem" value="25" min="1" max="90" step="0.5">
    </div>
    <div class="cfg-group">
      <label>Outros Custos Fixos por Item (%)</label>
      <input type="number" id="cfg-fixos" value="10" min="0" max="50" step="0.5">
      <div class="tax-breakdown">Rateio de aluguel, salários, energia, etc.</div>
    </div>
    <button class="config-apply" onclick="calcPrecificacao()">&#9654; Recalcular</button>
  </div>

  <div class="cards" id="cards-prec"></div>

  <div class="section">
    <div class="section-title">Precificação Ideal — Todos os Produtos</div>
    <div style="display:flex;gap:9px;margin-bottom:11px;flex-wrap:wrap">
      <input id="busca-prec" type="text" placeholder="Buscar produto..."
        oninput="calcPrecificacao()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem;width:240px">
      <select id="sort-prec" onchange="calcPrecificacao()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
        <option value="diff_desc">Maior ajuste necessário</option>
        <option value="diff_asc">Menor ajuste</option>
        <option value="cmv_desc">Maior CMV%</option>
        <option value="preco_desc">Maior preço atual</option>
        <option value="nome">Nome A-Z</option>
      </select>
      <select id="flt-prec" onchange="calcPrecificacao()"
        style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
        <option value="todos">Todos os produtos</option>
        <option value="acima">Preço acima do ideal</option>
        <option value="abaixo">Preço abaixo do ideal &#9888;</option>
        <option value="sem_custo">Sem custo cadastrado</option>
      </select>
    </div>
    <div class="tbl-wrap"><table id="tbl-prec">
      <thead><tr>
        <th>Produto</th>
        <th>Custo</th>
        <th>Imposto</th>
        <th>Custo Fixo</th>
        <th>CMV Efetivo %</th>
        <th>Preço Atual</th>
        <th>Preço Ideal</th>
        <th>Diferença</th>
        <th>Status</th>
      </tr></thead>
      <tbody></tbody>
    </table></div>
  </div>

  <div class="grid2">
    <div class="section">
      <div class="section-title">&#128200; Detalhamento do CMV por Componente</div>
      <div class="chart-wrap"><canvas id="chart-cmv-stack" height="260"></canvas></div>
    </div>
    <div class="section">
      <div class="section-title">&#128181; Simulador de Preço</div>
      <div style="padding:4px 0">
        <label style="font-size:.75rem;color:var(--text2);display:block;margin-bottom:5px">Produto</label>
        <select id="sim-produto" onchange="simularPreco()"
          style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--text);font-size:.82rem;margin-bottom:12px">
        </select>
        <div class="grid2" style="gap:10px;margin-bottom:10px">
          <div>
            <label style="font-size:.75rem;color:var(--text2);display:block;margin-bottom:4px">Custo do produto (R$)</label>
            <input type="number" id="sim-custo" oninput="simularPreco()" step="0.01" min="0"
              style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px;color:var(--text);font-size:.9rem">
          </div>
          <div>
            <label style="font-size:.75rem;color:var(--text2);display:block;margin-bottom:4px">Preço de venda (R$)</label>
            <input type="number" id="sim-venda" oninput="simularPreco()" step="0.01" min="0"
              style="width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:8px;color:var(--text);font-size:.9rem">
          </div>
        </div>
        <div id="sim-resultado" style="background:var(--bg3);border-radius:10px;padding:14px;font-size:.85rem;line-height:2"></div>
      </div>
    </div>
  </div>
</div>

<!-- DESPESAS FIXAS -->
<div id="tab-despesas" class="page">
  <div class="desp-form">
    <div class="section-title" style="margin-bottom:14px">&#10133; Cadastrar Nova Despesa Fixa</div>
    <div class="form-row">
      <div class="form-group">
        <label>Descrição</label>
        <input type="text" id="df-nome" placeholder="Ex: Conta de Luz" style="width:220px">
      </div>
      <div class="form-group">
        <label>Categoria</label>
        <select id="df-cat">
          <option value="energia">&#9889; Energia Elétrica</option>
          <option value="funcionarios">&#128104; Funcionários / Folha</option>
          <option value="aluguel">&#127968; Aluguel</option>
          <option value="agua">&#128167; Água / Saneamento</option>
          <option value="gas">&#128293; Gás</option>
          <option value="internet">&#128246; Internet / Telefone</option>
          <option value="manutencao">&#128295; Manutenção</option>
          <option value="contabilidade">&#128203; Contabilidade</option>
          <option value="seguro">&#128737; Seguro</option>
          <option value="marketing">&#128227; Marketing</option>
          <option value="outros">&#128188; Outros</option>
        </select>
      </div>
      <div class="form-group">
        <label>Valor Mensal (R$)</label>
        <input type="number" id="df-valor" placeholder="0,00" min="0" step="0.01">
      </div>
      <div class="form-group">
        <label>Recorrência</label>
        <select id="df-recorr">
          <option value="mensal">Mensal</option>
          <option value="quinzenal">Quinzenal</option>
          <option value="semanal">Semanal</option>
          <option value="anual">Anual</option>
          <option value="variavel">Variável</option>
        </select>
      </div>
      <div class="form-group">
        <label>Dia Vencimento</label>
        <input type="number" id="df-dia" placeholder="Ex: 10" min="1" max="31" style="width:120px">
      </div>
      <div class="form-group">
        <label>Obs (opcional)</label>
        <input type="text" id="df-obs" placeholder="Nota..." style="width:180px">
      </div>
      <button class="btn-add" onclick="adicionarDespesa()">&#10133; Adicionar</button>
    </div>
  </div>

  <div class="cards" id="cards-desp"></div>

  <div class="grid2">
    <div class="section">
      <div class="section-title">&#128202; Despesas por Categoria</div>
      <canvas id="chart-desp-cat" height="220"></canvas>
    </div>
    <div class="section">
      <div class="section-title">&#128197; Calendário de Vencimentos</div>
      <div id="calendario-desp"></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#128203; Lista de Despesas Fixas Cadastradas</div>
    <div class="tbl-wrap"><table id="tbl-desp-fixas">
      <thead><tr><th>Categoria</th><th>Descrição</th><th>Valor Mensal</th><th>Recorrência</th><th>Vencimento</th><th>Obs</th><th>Ações</th></tr></thead>
      <tbody></tbody>
    </table></div>
    <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
      <span style="color:var(--text2);font-size:.82rem">Total mensal estimado:</span>
      <span id="total-desp-fixas" style="font-size:1.1rem;font-weight:700;color:var(--red)">R$ 0,00</span>
    </div>
  </div>
</div>

<!-- IMPOSTOS -->
<div id="tab-impostos" class="page">
  <div class="config-panel" style="margin-bottom:18px">
    <div class="cfg-group">
      <label>Regime Tributário</label>
      <select id="imp-regime" onchange="calcImpostos()">
        <option value="simples_1">Simples Nacional — até R$180k/ano ~4,0%</option>
        <option value="simples_2" selected>Simples Nacional — até R$360k/ano ~7,3%</option>
        <option value="simples_3">Simples Nacional — até R$720k/ano ~9,5%</option>
        <option value="presumido">Lucro Presumido ~16,3%</option>
        <option value="real">Lucro Real ~22,0%</option>
      </select>
    </div>
    <div class="cfg-group">
      <label>Mês de Referência</label>
      <select id="imp-mes" onchange="calcImpostos()">
        <option value="2026-03" selected>Março 2026</option>
      </select>
    </div>
    <div class="cfg-group">
      <label>Faturamento do Mês (R$)</label>
      <input type="number" id="imp-fat" step="0.01" oninput="calcImpostos()"
        style="background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--text);font-size:.9rem;width:180px;outline:none">
    </div>
    <button class="config-apply" onclick="calcImpostos()">&#9654; Recalcular</button>
  </div>

  <div class="cards" id="cards-imp"></div>

  <div class="section">
    <div class="section-title">&#128197; Calendário de Recolhimento — Março / Abril 2026</div>
    <div class="tax-timeline" id="tax-timeline"></div>
  </div>

  <div class="grid2">
    <div id="impostos-detalhes"></div>
    <div>
      <div class="section">
        <div class="section-title">&#128200; Distribuição dos Impostos</div>
        <canvas id="chart-impostos-pizza" height="220"></canvas>
      </div>
      <div class="section" style="margin-top:0">
        <div class="section-title">&#128203; Guia de Recolhimento</div>
        <div id="guia-recolhimento" style="font-size:.83rem;line-height:2;color:var(--text2)"></div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#128181; Simulação Anual de Impostos</div>
    <div class="tbl-wrap"><table id="tbl-imp-anual">
      <thead><tr><th>Mês</th><th>Fat. Estimado</th><th>DAS / Total</th><th>PIS</th><th>COFINS</th><th>ISS</th><th>IRPJ+CSLL</th><th>Total Impostos</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </div>
</div>

<!-- NOTAS FISCAIS -->
<div id="tab-notas" class="page">
  <div class="nf-resumo-cards" id="nf-cards"></div>
  <div class="section">
    <div class="section-title">&#128196; Notas Emitidas — Saída (NFC-e + NF-e)</div>
    <div style="display:flex;gap:9px;margin-bottom:12px;flex-wrap:wrap;align-items:center">
      <button class="nf-detail-toggle" id="btn-det-saida" onclick="toggleNFDetail('saida')">&#128269; Detalhar Saída</button>
      <span style="font-size:.78rem;color:var(--text2)" id="nf-saida-count"></span>
    </div>
    <div id="nf-resumo-saida"></div>
    <div class="nf-detail-block" id="nf-detail-saida">
      <div style="display:flex;gap:9px;margin-bottom:9px;flex-wrap:wrap">
        <input id="busca-nf-saida" type="text" placeholder="Buscar nota, destinatário..."
          oninput="renderNFTable('saida')"
          style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem;width:260px">
        <select id="flt-nf-saida" onchange="renderNFTable('saida')"
          style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
          <option value="todas">Todos os modelos</option>
          <option value="65">NFC-e (modelo 65)</option>
          <option value="55">NF-e (modelo 55)</option>
        </select>
      </div>
      <div class="tbl-wrap"><table id="tbl-nf-saida">
        <thead><tr><th>Data</th><th>N&#186; NF</th><th>Modelo</th><th>Destinatário</th><th>Nat. Operação</th><th>Valor (R$)</th><th>Status</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">&#128229; Notas de Compra (Entrada)</div>
    <div style="display:flex;gap:9px;margin-bottom:12px;flex-wrap:wrap;align-items:center">
      <button class="nf-detail-toggle" id="btn-det-entrada" onclick="toggleNFDetail('entrada')">&#128269; Detalhar Compras</button>
      <span style="font-size:.78rem;color:var(--text2)" id="nf-entrada-count"></span>
    </div>
    <div id="nf-resumo-entrada"></div>
    <div class="nf-detail-block" id="nf-detail-entrada">
      <div style="display:flex;gap:9px;margin-bottom:9px;flex-wrap:wrap">
        <input id="busca-nf-entrada" type="text" placeholder="Buscar fornecedor, N&#186; NF..."
          oninput="renderNFTable('entrada')"
          style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem;width:260px">
        <select id="flt-nf-forn" onchange="renderNFTable('entrada')"
          style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:7px 11px;color:var(--text);font-size:.82rem">
          <option value="">Todos os fornecedores</option>
        </select>
      </div>
      <div class="tbl-wrap"><table id="tbl-nf-entrada">
        <thead><tr><th>Data</th><th>N&#186; NF</th><th>Fornecedor</th><th>CNPJ</th><th>Nat. Operação</th><th>Valor Produtos</th><th>Valor NF</th><th>Status</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </div>
  </div>
</div>

<!-- CHAT -->
<div id="tab-chat" class="page" style="padding:0">
  <div class="chat-wrap">
    <div class="suggestions">
      <button class="sug-btn" onclick="sendChat('Qual foi meu melhor dia do mês?')">Melhor dia</button>
      <button class="sug-btn" onclick="sendChat('Qual prato devo tirar do cardápio?')">Prato para remover</button>
      <button class="sug-btn" onclick="sendChat('Tenho dinheiro para pagar fornecedores?')">Caixa vs fornecedores</button>
      <button class="sug-btn" onclick="sendChat('Quais produtos têm margem ruim?')">Margem ruim</button>
      <button class="sug-btn" onclick="sendChat('Quais itens estão em falta no estoque?')">Estoque crítico</button>
      <button class="sug-btn" onclick="sendChat('Qual é meu produto mais rentável?')">Mais rentável</button>
      <button class="sug-btn" onclick="sendChat('Como foram as vendas esta semana?')">Vendas da semana</button>
      <button class="sug-btn" onclick="sendChat('Qual o total de despesas do mês?')">Total despesas</button>
      <button class="sug-btn" onclick="sendChat('Resumo geral do mês')">Resumo do mês</button>
    </div>
    <div class="chat-msgs" id="chat-msgs">
      <div class="msg agent">
        &#128075; Olá! Sou o agente do <strong>Village Gourmet</strong>.<br>
        Posso responder sobre vendas, produtos, estoque e financeiro com os dados do Yooga.<br>
        Período: <strong>01/03/2026 a 19/03/2026</strong>. O que você quer saber?
      </div>
    </div>
    <div class="chat-input-row">
      <textarea class="chat-input" id="chat-input"
        placeholder="Digite sua pergunta em português..."
        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendChatInput()}"></textarea>
      <button class="chat-send" onclick="sendChatInput()">Enviar</button>
    </div>
  </div>
</div>

<script>
// ═══ DADOS EMBARCADOS ═══
__DATA_PLACEHOLDER__

// ═══ MAPA CATEGORIAS ═══
const CAT_MAP = {};
CATS.forEach(c => CAT_MAP[c.idi] = c.nome);

// ═══ UTILS ═══
const fmt = v => (v||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const fmtN = v => (v||0).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1});
const fmtPct = v => (v||0).toFixed(1)+'%';
const fmtDate = d => {
  if (!d) return '-';
  try { return new Date(d).toLocaleDateString('pt-BR'); } catch(e){ return d.toString().slice(0,10); }
};

function showTab(id, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  if (el) el.classList.add('active');
  if (id==='visao') redrawVisao();
  if (id==='financeiro') initFinanceiro();
  if (id==='precificacao') setTimeout(()=>calcPrecificacao(),50);
  if (id==='despesas')    renderDespesas();
  if (id==='impostos')    calcImpostos();
  if (id==='notas')       initNotas();
}

function showRefreshInfo() {
  alert('Para atualizar os dados:\\n\\n1. Execute: python coletar_endpoints.py\\n2. Execute: python gerar_dashboard.py\\n3. Recarregue esta página (F5)');
}

// ═══ UTILITÁRIO FINANCEIRO CENTRAL ═══
function calcDRE() {
  const receita    = EXTOPT.order_revenue_total || 0;
  const nPed       = EXTOPT.order_count || 0;
  const cmv        = (NOTAS_COMPRA||[]).reduce((s,n) => s + (n.vNF||0), 0);
  const despYooga  = EXTOPT.order_expense_total || 0;
  const despFixas  = loadDespesas().reduce((s,d) => {
    const v = d.recorr==='anual'?d.valor/12 : d.recorr==='semanal'?d.valor*4.33 : d.recorr==='quinzenal'?d.valor*2 : d.valor;
    return s + v;
  }, 0);
  // Usa regime da aba impostos se disponível, senão precificação, senão padrão
  const regimeEl = document.getElementById('imp-regime') || document.getElementById('cfg-regime');
  const regime   = regimeEl?.value || 'simples_2';
  const aliqPct  = (REGIMES_IMP[regime]?.aliq_total || 7.3);
  const impostos = receita * aliqPct / 100;

  const lucroBruto  = receita - cmv;
  const ebitda      = lucroBruto - despYooga - despFixas;
  const resultLiq   = ebitda - impostos;
  const pct = v => receita > 0 ? (v/receita*100) : 0;

  return {receita, nPed, cmv, despYooga, despFixas, impostos, aliqPct,
          lucroBruto, ebitda, resultLiq, pct};
}

// ═══ VISÃO GERAL ═══
function initVisao() {
  const D       = calcDRE();
  const nPed    = D.nPed;
  const ticketMed = nPed > 0 ? D.receita/nPed : 0;

  const cmvPct  = D.pct(D.cmv);
  const mbPct   = D.pct(D.lucroBruto);
  const rlPct   = D.pct(D.resultLiq);

  document.getElementById('cards-visao').innerHTML = [
    {label:'Faturamento do Mês', value:fmt(D.receita),    sub:'01 a 19/03/2026 · '+nPed+' pedidos',  cls:'green',                              icon:'&#128200;'},
    {label:'Ticket Médio',       value:fmt(ticketMed),    sub:'Receita ÷ total de pedidos',           cls:'blue',                               icon:'&#127915;'},
    {label:'CMV (Custo Compras)',value:fmt(D.cmv),        sub:fmtPct(cmvPct)+' da receita bruta · '+((NOTAS_COMPRA||[]).length)+' NFs',        cls:'red',                                icon:'&#128666;'},
    {label:'Resultado Líquido',  value:fmt(D.resultLiq),  sub:'Após CMV, fixas e impostos · '+fmtPct(rlPct), cls:D.resultLiq>=0?'green':'red', icon:'&#9878;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // Alerta estoque
  const criticos = [];
  (ESTMIN.categorias||[]).forEach(cat => {
    (cat.produtos||[]).forEach(p => { if (p.estoque_atual < 0) criticos.push(p.produto); });
  });
  if (criticos.length > 0) {
    document.getElementById('alert-estoque').innerHTML =
      `<div class="alert">&#9888; <strong>${criticos.length} produto(s) com estoque crítico:</strong> ${criticos.slice(0,5).join(', ')}${criticos.length>5?' e mais '+(criticos.length-5)+'...':''}</div>`;
  }

  // Top produtos
  const labels = DASH.chart_produto_labels || [];
  const qtds   = DASH.chart_produto_data   || [];
  const top10  = labels.map((l,i)=>({n:l,q:qtds[i]})).sort((a,b)=>b.q-a.q).slice(0,10);
  const maxQ   = top10[0]?.q || 1;
  document.getElementById('top-produtos').innerHTML = top10.map((p,i)=>`
    <div class="rank-item">
      <div class="rank-num ${i<3?'top':''}">${i+1}</div>
      <div class="rank-name">${p.n}</div>
      <div style="flex:1;margin:0 10px"><div class="prog-wrap"><div class="prog-bar" style="width:${(p.q/maxQ*100).toFixed(0)}%;background:var(--accent)"></div></div></div>
      <div class="rank-val">${p.q.toLocaleString('pt-BR')}</div>
    </div>`).join('');

  redrawVisao();
}

function redrawVisao() {
  setTimeout(()=>{
    drawBarChart('chart-fat',
      VPD.map(d=>d.data.slice(5)),
      VPD.map(d=>d.faturamento), '#6366f1');
    const pl = DASH.chart_pagamento_labels || ['Débito','Crédito','Pix','Dinheiro'];
    const pd = DASH.chart_pagamento_data   || [0,0,0,0];
    drawDonut('chart-pag', pl, pd, ['#6366f1','#22c55e','#f59e0b','#3b82f6']);
  },50);
}

// ═══ FINANCEIRO ═══
function initFinanceiro() {
  const D = calcDRE();

  // ─ Cards ──────────────────────────────────────────────────
  document.getElementById('cards-fin').innerHTML = [
    {label:'Receita Bruta',    value:fmt(D.receita),      sub:D.nPed+' pedidos · 01–19/03/2026',             cls:'green',                              icon:'&#128200;'},
    {label:'CMV — Compras NF', value:fmt(D.cmv),          sub:fmtPct(D.pct(D.cmv))+' da receita · '+(NOTAS_COMPRA||[]).length+' notas',          cls:'red',                                icon:'&#128666;'},
    {label:'Margem Bruta',     value:fmt(D.lucroBruto),   sub:fmtPct(D.pct(D.lucroBruto))+' — após deduzir CMV',                                  cls:D.lucroBruto>=0?'green':'red',        icon:'&#128202;'},
    {label:'Resultado Líquido',value:fmt(D.resultLiq),    sub:fmtPct(D.pct(D.resultLiq))+' — após tudo (CMV+fixas+impostos)',                     cls:D.resultLiq>=0?'green':'red',         icon:'&#9878;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // ─ DRE completo ───────────────────────────────────────────
  const row = (label, val, indent, cls, pct, bold) => {
    const v = val < 0 ? `<span class="dre-value neg">${fmt(val)}</span>` :
              val > 0 ? `<span class="dre-value ${cls||'pos'}">${fmt(val)}</span>` :
                        `<span class="dre-value" style="color:var(--text2)">${fmt(0)}</span>`;
    return `<div class="dre-row${bold?' result':''}">
      <span class="dre-label${indent?' dre-indent':''}" ${bold?'style="font-weight:700"':''}>${label}</span>
      <span class="dre-pct">${pct!==undefined?fmtPct(pct):''}</span>
      ${v}
    </div>`;
  };

  const despTotaisOp = D.despYooga + D.despFixas;
  const alertaCMV = D.pct(D.cmv) > 40
    ? `<div style="background:#7c2d1222;border:1px solid var(--yellow);border-radius:7px;padding:8px 12px;margin-bottom:10px;font-size:.78rem;color:var(--yellow)">
        &#9888; CMV acima de 40% da receita — revise preços ou renegocie fornecedores</div>` : '';

  document.getElementById('dre-content').innerHTML = alertaCMV + `
    ${row('(+) Receita Operacional Bruta', D.receita, false, 'pos', 100, false)}
    ${row('(-) CMV — Notas de Compra', -D.cmv, true, '', D.pct(D.cmv), false)}
    ${row('(=) Lucro Bruto', D.lucroBruto, false, D.lucroBruto>=0?'pos':'neg', D.pct(D.lucroBruto), true)}
    ${row('(-) Desp. Operacionais Yooga', -D.despYooga, true, '', D.pct(D.despYooga), false)}
    ${row('(-) Despesas Fixas Cadastradas', -D.despFixas, true, '', D.pct(D.despFixas), false)}
    ${row('(=) EBITDA', D.ebitda, false, D.ebitda>=0?'pos':'neg', D.pct(D.ebitda), true)}
    ${row('(-) Impostos (~'+D.aliqPct.toFixed(1)+'%)', -D.impostos, true, '', D.aliqPct, false)}
    <div class="dre-row result-final">
      <span class="dre-label" style="font-weight:700">&#9783; Resultado Líquido</span>
      <span class="dre-pct">${fmtPct(D.pct(D.resultLiq))}</span>
      <span class="dre-value ${D.resultLiq>=0?'pos':'neg'}" style="font-size:1.05rem">${fmt(D.resultLiq)}</span>
    </div>
    <div style="margin-top:14px;padding-top:10px;border-top:1px solid var(--border)">
      ${row('Pendente a receber', D.receita>0?(EXTOPT.pending_revenue_total||0):0, false, 'pos', undefined, false)}
      ${row('Pendente a pagar', -(EXTOPT.pending_expense_total||0), false, '', undefined, false)}
    </div>`;

  // ─ Gráfico composição de custos ──────────────────────────
  const lucroPos = Math.max(D.resultLiq, 0);
  const prejuizo = D.resultLiq < 0 ? Math.abs(D.resultLiq) : 0;
  const compLabels = ['CMV (Compras)', 'Desp. Operac.', 'Desp. Fixas', 'Impostos',
                      D.resultLiq>=0 ? 'Lucro Líquido' : 'Resultado Negativo'];
  const compValues = [D.cmv, D.despYooga, D.despFixas, D.impostos,
                      D.resultLiq>=0 ? lucroPos : prejuizo];
  const compColors = ['#ef4444','#f97316','#f59e0b','#8b5cf6',
                      D.resultLiq>=0 ? '#22c55e' : '#dc2626'];
  setTimeout(() => {
    drawDonut('chart-composicao', compLabels, compValues, compColors);
    const total = compValues.reduce((s,v)=>s+v,0)||1;
    document.getElementById('composicao-legenda').innerHTML =
      compLabels.map((l,i)=>`
        <div style="display:flex;align-items:center;gap:7px;margin-bottom:7px">
          <span style="width:11px;height:11px;border-radius:50%;background:${compColors[i]};flex-shrink:0"></span>
          <span style="flex:1;font-size:.78rem">${l}</span>
          <span style="font-size:.78rem;font-weight:600;color:${compColors[i]}">${fmtPct(compValues[i]/D.receita*100)}</span>
        </div>`).join('');
  }, 80);

  // Tabela lançamentos
  const tbody = document.querySelector('#tbl-lancamentos tbody');
  const sorted = [...EXTRATO].sort((a,b)=>new Date(b.due_date)-new Date(a.due_date));
  const hoje = new Date();
  tbody.innerHTML = sorted.map(e=>{
    const venc = e.due_date ? new Date(e.due_date) : null;
    const pago = !!e.pay_date;
    const vencido = venc && venc < hoje && !pago && e.type==='e';
    return `<tr>
      <td>${fmtDate(e.due_date)}</td>
      <td>${e.name||'-'}</td>
      <td><span class="badge ${e.type==='r'?'badge-ok':'badge-warn'}">${e.type==='r'?'RECEITA':'DESPESA'}</span></td>
      <td style="color:${e.type==='r'?'var(--green)':'var(--red)'}">${fmt(e.value)}</td>
      <td><span class="badge ${pago?'badge-ok':vencido?'badge-crit':'badge-info'}">${pago?'PAGO':vencido?'VENCIDO':'PENDENTE'}</span></td>
    </tr>`;
  }).join('');

  redrawFluxo();
}

function redrawFluxo() {
  setTimeout(()=>{
    const datas = FLUXO.map(f=>f.data.slice(5));
    let acum = 0;
    const saldos = FLUXO.map(f=>{
      const flow = f.dados?.flow || [];
      const mes  = flow.find(x=>x.current_month) || flow[flow.length-1] || {};
      acum += (mes.total_revenue||0) - (mes.total_expense||0);
      return parseFloat(acum.toFixed(2));
    });
    drawLineChart('chart-fluxo', datas, saldos, '#22c55e');
  },50);
}

// ═══ PRODUTOS ═══
let prodsTodos = [];
function initProdutos() {
  prodsTodos = PRODS.map(p=>{
    const custo  = p.valor_custo || 0;
    const venda  = p.valor_venda || 0;
    const margem = venda>0 ? ((venda-custo)/venda*100) : (custo===0?100:0);
    return {...p, margem, cat_nome: CAT_MAP[p.categoria_id]||'Outros'};
  }).filter(p=>p.valor_venda>0);
  filtrarProdutos();

  // Top 10 mais vendidos
  const labels = DASH.chart_produto_labels || [];
  const qtds   = DASH.chart_produto_data   || [];
  const top = labels.map((l,i)=>({n:l,q:qtds[i]})).sort((a,b)=>b.q-a.q).slice(0,10);
  document.getElementById('rank-vendidos').innerHTML = top.map((p,i)=>`
    <div class="rank-item">
      <div class="rank-num ${i<3?'top':''}">${i+1}</div>
      <div class="rank-name" style="font-size:.8rem">${p.n}</div>
      <div class="rank-val">${p.q.toLocaleString('pt-BR')} un</div>
    </div>`).join('');

  // Margem baixa
  const baixa = prodsTodos.filter(p=>p.valor_custo>0&&p.margem<60).sort((a,b)=>a.margem-b.margem).slice(0,15);
  document.getElementById('margem-baixa').innerHTML = baixa.length===0
    ? '<p style="color:var(--text2);font-size:.82rem;padding:8px 0">Sem produtos com custo cadastrado abaixo de 60%.</p>'
    : baixa.map(p=>`<div class="rank-item">
        <div class="rank-num" style="background:var(--red);color:#fff">!</div>
        <div class="rank-name" style="font-size:.8rem">${p.descricao}</div>
        <div class="rank-val" style="color:var(--red)">${fmtPct(p.margem)}</div>
      </div>`).join('');
}

function filtrarProdutos() {
  const busca = (document.getElementById('busca-prod')?.value||'').toLowerCase();
  const sort  = document.getElementById('sort-prod')?.value||'ranking';
  let lista   = prodsTodos.filter(p=>p.descricao.toLowerCase().includes(busca));
  if (sort==='margem_asc')       lista.sort((a,b)=>a.margem-b.margem);
  else if(sort==='margem_desc')  lista.sort((a,b)=>b.margem-a.margem);
  else if(sort==='preco_desc')   lista.sort((a,b)=>b.valor_venda-a.valor_venda);
  else if(sort==='nome')         lista.sort((a,b)=>a.descricao.localeCompare(b.descricao));
  else lista.sort((a,b)=>(b.ranking||0)-(a.ranking||0));

  // Pega alíquota atual do painel de precificação (se disponível)
  const aliq = parseFloat(document.getElementById('cfg-imposto')?.value||7.3)/100;

  const tbody = document.querySelector('#tbl-produtos tbody');
  tbody.innerHTML = lista.slice(0,300).map(p=>{
    const venda  = p.valor_venda||0;
    const custo  = p.valor_custo||0;
    // CMV bruto = custo / venda
    const cmvBruto  = venda>0&&custo>0 ? (custo/venda*100) : null;
    // Receita líquida = venda × (1 - aliq)
    const recLiq    = venda*(1-aliq);
    // CMV c/ imposto = custo / receita líquida
    const cmvImposto = recLiq>0&&custo>0 ? (custo/recLiq*100) : null;
    // Margem líquida = (venda - custo - imposto) / venda
    const margemLiq  = venda>0&&custo>0 ? ((venda-custo-venda*aliq)/venda*100) : null;

    const mc  = c => c===null?'var(--text2)':c>70?'var(--red)':c>50?'var(--yellow)':'var(--green)';
    const mlc = m => m===null?'var(--text2)':m<20?'var(--red)':m<30?'var(--yellow)':'var(--green)';
    const nd  = '<span style="color:var(--text2)">—</span>';

    return `<tr>
      <td>${p.descricao}</td>
      <td style="color:var(--text2);font-size:.78rem">${p.cat_nome}</td>
      <td style="color:var(--green)">${fmt(venda)}</td>
      <td>${custo>0?fmt(custo):nd}</td>
      <td>${cmvBruto!==null?`<span style="color:${mc(cmvBruto)}">${fmtPct(cmvBruto)}</span>`:nd}</td>
      <td>${cmvImposto!==null?`<span style="color:${mc(cmvImposto)}">${fmtPct(cmvImposto)}</span><span class="imposto-badge" style="margin-left:5px">+imp</span>`:nd}</td>
      <td>${margemLiq!==null?`<span style="color:${mlc(margemLiq)}">${fmtPct(margemLiq)}</span>`:nd}</td>
      <td style="color:var(--text2)">${(p.ranking||0).toLocaleString('pt-BR')}</td>
    </tr>`;
  }).join('');
}

// ═══ PRECIFICAÇÃO ═══
const REGIMES = {
  simples_1:  {aliq:4.0,  desc:'Simples Nacional Anexo I faixa 1 — DAS ~4,0%'},
  simples_2:  {aliq:7.3,  desc:'PIS 0,65% · COFINS 3% · ISS 5% · IRPJ 2% · CSLL 1,08% → ~7,3% efetivo'},
  simples_3:  {aliq:9.5,  desc:'Simples Nacional Anexo I faixa 3 — DAS ~9,5%'},
  presumido:  {aliq:16.33,desc:'PIS 0,65% · COFINS 3% · ISS 5% · IRPJ 4,8% · CSLL 2,88% → ~16,3%'},
  real:       {aliq:22.0, desc:'PIS 1,65% · COFINS 7,6% · ISS 5% · IRPJ ~5% · CSLL ~3% → ~22%'},
  custom:     {aliq:null, desc:'Alíquota personalizada — edite o campo ao lado'},
};

function onRegimeChange() {
  const regime = document.getElementById('cfg-regime').value;
  const r = REGIMES[regime];
  document.getElementById('tax-desc').textContent = r.desc;
  if (r.aliq !== null) document.getElementById('cfg-imposto').value = r.aliq;
}

function initPrecificacao() {
  onRegimeChange();
  // Popula simulador
  const sel = document.getElementById('sim-produto');
  const opts = PRODS.filter(p=>p.valor_venda>0)
    .sort((a,b)=>a.descricao.localeCompare(b.descricao));
  sel.innerHTML = opts.map(p=>`<option value="${p.idi||p.codigo}">${p.descricao}</option>`).join('');
  sel.addEventListener('change', ()=>{
    const found = opts.find(p=>(p.idi||p.codigo)==sel.value);
    if (found) {
      document.getElementById('sim-custo').value = found.valor_custo||0;
      document.getElementById('sim-venda').value = found.valor_venda||0;
      simularPreco();
    }
  });
  if (opts[0]) {
    document.getElementById('sim-custo').value = opts[0].valor_custo||0;
    document.getElementById('sim-venda').value = opts[0].valor_venda||0;
  }
  calcPrecificacao();
  simularPreco();
}

function calcPrecificacao() {
  const aliq    = parseFloat(document.getElementById('cfg-imposto').value||7.3)/100;
  const margDes = parseFloat(document.getElementById('cfg-margem').value||25)/100;
  const fixos   = parseFloat(document.getElementById('cfg-fixos').value||10)/100;
  const busca   = (document.getElementById('busca-prec')?.value||'').toLowerCase();
  const sort    = document.getElementById('sort-prec')?.value||'diff_desc';
  const flt     = document.getElementById('flt-prec')?.value||'todos';

  // Preço ideal = Custo / (1 - margem_desejada - impostos - fixos)
  const divisor = 1 - margDes - aliq - fixos;

  let lista = PRODS.filter(p=>p.valor_venda>0)
    .map(p=>{
      const venda = p.valor_venda||0;
      const custo = p.valor_custo||0;
      const imposto_rs   = venda * aliq;
      const fixos_rs     = custo * fixos;
      const rec_liq      = venda*(1-aliq);
      const cmv_efetivo  = rec_liq>0&&custo>0 ? (custo/rec_liq*100) : null;
      const preco_ideal  = divisor>0&&custo>0 ? (custo/divisor) : null;
      const diff         = preco_ideal!==null ? (venda - preco_ideal) : null;
      const diff_pct     = preco_ideal>0 ? ((venda/preco_ideal-1)*100) : null;
      return {...p, imposto_rs, fixos_rs, cmv_efetivo, preco_ideal, diff, diff_pct};
    });

  // Atualiza também a tabela de produtos (refaz com novo aliq)
  filtrarProdutos();

  // Cards resumo
  const comCusto  = lista.filter(p=>p.valor_custo>0);
  const abaixo    = comCusto.filter(p=>p.diff!==null&&p.diff<-0.5);
  const acima     = comCusto.filter(p=>p.diff!==null&&p.diff>=0.5);
  const ok_prec   = comCusto.filter(p=>p.diff!==null&&Math.abs(p.diff)<0.5);
  const cmv_medio = comCusto.length>0 ? comCusto.reduce((s,p)=>s+(p.cmv_efetivo||0),0)/comCusto.length : 0;

  document.getElementById('cards-prec').innerHTML = [
    {label:'CMV Médio c/ Imposto', value:fmtPct(cmv_medio),     sub:'Custo sobre receita líquida', cls:cmv_medio>60?'red':cmv_medio>45?'yellow':'green', icon:'&#128200;'},
    {label:'Preço Abaixo do Ideal',value:abaixo.length,         sub:'Precisam de reajuste',        cls:'red',   icon:'&#128201;'},
    {label:'Preço OK',             value:ok_prec.length,        sub:'Dentro da faixa ideal',       cls:'green', icon:'&#9989;'},
    {label:'Preço Acima do Ideal', value:acima.length,          sub:'Margem acima de '+fmtPct(margDes*100),cls:'blue',  icon:'&#128176;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // Filtros
  if (busca) lista = lista.filter(p=>p.descricao.toLowerCase().includes(busca));
  if (flt==='abaixo')    lista = lista.filter(p=>p.diff!==null&&p.diff<-0.5);
  else if(flt==='acima') lista = lista.filter(p=>p.diff!==null&&p.diff>=0.5);
  else if(flt==='sem_custo') lista = lista.filter(p=>!p.valor_custo||p.valor_custo===0);

  // Ordenação
  if(sort==='diff_desc')    lista.sort((a,b)=>(a.diff??Infinity)-(b.diff??Infinity));
  else if(sort==='diff_asc')lista.sort((a,b)=>(b.diff??-Infinity)-(a.diff??-Infinity));
  else if(sort==='cmv_desc')lista.sort((a,b)=>(b.cmv_efetivo||0)-(a.cmv_efetivo||0));
  else if(sort==='preco_desc')lista.sort((a,b)=>b.valor_venda-a.valor_venda);
  else lista.sort((a,b)=>a.descricao.localeCompare(b.descricao));

  const tbody = document.querySelector('#tbl-prec tbody');
  tbody.innerHTML = lista.slice(0,300).map(p=>{
    const nd = '<span style="color:var(--text2)">—</span>';
    const hasCusto = p.valor_custo>0;

    // CMV semáforo: verde <40%, amarelo 40-60%, vermelho >60%
    const cmvCor = !p.cmv_efetivo?'var(--text2)':p.cmv_efetivo>60?'var(--red)':p.cmv_efetivo>40?'var(--yellow)':'var(--green)';

    let statusHtml = nd;
    let diffHtml   = nd;
    let idealHtml  = nd;
    if (hasCusto && p.preco_ideal!==null) {
      idealHtml = `<strong>${fmt(p.preco_ideal)}</strong>`;
      if (p.diff < -0.5) {
        diffHtml   = `<span class="price-tag price-down">&#9650; ${fmt(-p.diff)}</span>`;
        statusHtml = `<span class="badge badge-crit">ABAIXO</span>`;
      } else if (p.diff > 0.5) {
        diffHtml   = `<span class="price-tag price-up">&#9660; ${fmt(p.diff)}</span>`;
        statusHtml = `<span class="badge badge-ok">OK+</span>`;
      } else {
        diffHtml   = `<span class="price-tag price-ok">~OK</span>`;
        statusHtml = `<span class="badge badge-info">IDEAL</span>`;
      }
    } else if (!hasCusto) {
      statusHtml = `<span class="badge" style="background:#2e334755;color:var(--text2)">SEM CUSTO</span>`;
    }

    return `<tr>
      <td>${p.descricao}</td>
      <td>${hasCusto?fmt(p.valor_custo):nd}</td>
      <td>${hasCusto?`<span class="imposto-badge">${fmt(p.imposto_rs)}</span>`:nd}</td>
      <td style="color:var(--text2);font-size:.78rem">${hasCusto?fmt(p.fixos_rs):nd}</td>
      <td>${p.cmv_efetivo!==null?`<span style="color:${cmvCor};font-weight:600">${fmtPct(p.cmv_efetivo)}</span>`:nd}</td>
      <td style="color:var(--green);font-weight:600">${fmt(p.valor_venda)}</td>
      <td>${idealHtml}</td>
      <td>${diffHtml}</td>
      <td>${statusHtml}</td>
    </tr>`;
  }).join('');

  // Gráfico CMV stack (top 15 produtos com custo)
  const top15 = lista.filter(p=>p.valor_custo>0).slice(0,15);
  drawCmvStack('chart-cmv-stack', top15, aliq);
}

function drawCmvStack(id, prods, aliq) {
  const canvas = document.getElementById(id);
  if (!canvas||!prods.length) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth||600;
  canvas.width=W; canvas.height=+canvas.getAttribute('height')||260;
  const H=canvas.height;
  const pad={t:20,r:120,b:100,l:10};
  const cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;
  ctx.clearRect(0,0,W,H);

  const bh = Math.min(22, (ch/prods.length)-3);
  const colors = {custo:'#6366f1', imposto:'#a855f7', fixo:'#3b82f6', lucro:'#22c55e'};

  prods.forEach((p,i)=>{
    const venda   = p.valor_venda||1;
    const pCusto  = (p.valor_custo/venda)*100;
    const pImp    = aliq*100;
    const pFixo   = parseFloat(document.getElementById('cfg-fixos').value||10);
    const pLucro  = Math.max(0, 100-pCusto-pImp-pFixo);
    const y       = pad.t + i*(ch/prods.length) + (ch/prods.length-bh)/2;

    const segments = [
      {v:pCusto, c:colors.custo},
      {v:pImp,   c:colors.imposto},
      {v:pFixo,  c:colors.fixo},
      {v:pLucro, c:colors.lucro},
    ];
    let x = pad.l;
    segments.forEach(seg=>{
      const sw = (seg.v/100)*cw;
      ctx.fillStyle=seg.c;
      ctx.fillRect(x, y, Math.max(0,sw), bh);
      x+=Math.max(0,sw);
    });
    // Label produto
    ctx.fillStyle='#94a3b8'; ctx.font='10px sans-serif'; ctx.textAlign='left';
    ctx.fillText(p.descricao.slice(0,22)+(p.descricao.length>22?'…':''), pad.l+cw+6, y+bh/2+4);
  });

  // Legenda
  const leg=[['Custo',colors.custo],['Imposto',colors.imposto],['Fixos',colors.fixo],['Lucro',colors.lucro]];
  leg.forEach(([l,c],i)=>{
    const lx=pad.l+i*(cw/4), ly=H-pad.b+14;
    ctx.fillStyle=c; ctx.fillRect(lx,ly,10,10);
    ctx.fillStyle='#94a3b8'; ctx.font='9px sans-serif'; ctx.textAlign='left';
    ctx.fillText(l, lx+13, ly+9);
  });
}

function simularPreco() {
  const custo  = parseFloat(document.getElementById('sim-custo')?.value||0);
  const venda  = parseFloat(document.getElementById('sim-venda')?.value||0);
  const aliq   = parseFloat(document.getElementById('cfg-imposto')?.value||7.3)/100;
  const margDes= parseFloat(document.getElementById('cfg-margem')?.value||25)/100;
  const fixos  = parseFloat(document.getElementById('cfg-fixos')?.value||10)/100;

  if (!venda||!custo) {
    document.getElementById('sim-resultado').innerHTML='<span style="color:var(--text2)">Preencha custo e preço de venda.</span>';
    return;
  }
  const rec_liq     = venda*(1-aliq);
  const imposto_rs  = venda*aliq;
  const fixos_rs    = custo*fixos;
  const cmv_bruto   = (custo/venda)*100;
  const cmv_efetivo = rec_liq>0?(custo/rec_liq*100):0;
  const margem_liq  = ((venda-custo-imposto_rs-fixos_rs)/venda)*100;
  const divisor     = 1-margDes-aliq-fixos;
  const preco_ideal = divisor>0?custo/divisor:0;
  const diff        = venda-preco_ideal;

  const cor = margem_liq >= margDes*100*0.9 ? '#22c55e' : margem_liq>=0?'#f59e0b':'#ef4444';
  document.getElementById('sim-resultado').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
      <span style="color:var(--text2)">Custo bruto:</span>         <span>${fmt(custo)} (${fmtPct(cmv_bruto)})</span>
      <span style="color:var(--text2)">Imposto (${fmtPct(aliq*100)}):</span>   <span class="imposto-badge">${fmt(imposto_rs)}</span>
      <span style="color:var(--text2)">Custo fixo (${fmtPct(fixos*100)}):</span><span>${fmt(fixos_rs)}</span>
      <span style="color:var(--text2)">CMV c/ imposto:</span>       <span style="color:${cmv_efetivo>60?'var(--red)':cmv_efetivo>40?'var(--yellow)':'var(--green)'};font-weight:700">${fmtPct(cmv_efetivo)}</span>
      <span style="color:var(--text2)">Margem líquida:</span>       <span style="color:${cor};font-weight:700">${fmtPct(margem_liq)}</span>
      <span style="color:var(--text2)">Preço ideal (${fmtPct(margDes*100)}):</span><span style="font-weight:700">${fmt(preco_ideal)}</span>
      <span style="color:var(--text2)">Ajuste necessário:</span>    <span style="color:${diff<-0.5?'var(--red)':diff>0.5?'var(--green)':'var(--blue)'};font-weight:700">${diff<-0.5?'▲ reajustar +'+fmt(-diff):diff>0.5?'▼ margem extra '+fmt(diff):'✓ preço ideal'}</span>
    </div>`;
}

// ═══ ESTOQUE ═══
let filtroEst = 'todos';
function initEstoque() {
  let todos = [];
  (ESTMIN.categorias||[]).forEach(cat=>{
    (cat.produtos||[]).forEach(p=>{
      const status = p.estoque_atual < 0 ? 'critico'
        : (p.estoque_minimo>0 && p.estoque_atual<=p.estoque_minimo) ? 'atencao' : 'ok';
      todos.push({...p, cat_nome:cat.categoria_nome, status});
    });
  });
  const crit  = todos.filter(p=>p.status==='critico').length;
  const atenc = todos.filter(p=>p.status==='atencao').length;
  const ok    = todos.filter(p=>p.status==='ok').length;
  document.getElementById('cards-est').innerHTML = [
    {label:'Total Produtos',  value:todos.length, sub:'Cadastrados', cls:'',       icon:'&#128230;'},
    {label:'Crítico',         value:crit,         sub:'Estoque negativo', cls:'red',    icon:'&#128680;'},
    {label:'Atenção',         value:atenc,        sub:'Abaixo do mínimo', cls:'yellow', icon:'&#9888;'},
    {label:'OK',              value:ok,           sub:'Nível adequado',   cls:'green',  icon:'&#9989;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');
  window._estoqTodos = todos;
  renderEstoque();
}

function renderEstoque() {
  const todos = window._estoqTodos||[];
  let lista = filtroEst==='todos' ? todos : todos.filter(p=>p.status===filtroEst);
  lista.sort((a,b)=>{
    const ord = {critico:0,atencao:1,ok:2};
    return ord[a.status]-ord[b.status]||a.cat_nome.localeCompare(b.cat_nome);
  });
  const tbody = document.querySelector('#tbl-estoque tbody');
  tbody.innerHTML = lista.map(p=>{
    const cls = p.status==='critico'?'badge-crit':p.status==='atencao'?'badge-warn':'badge-ok';
    const lbl = p.status==='critico'?'CRÍTICO':p.status==='atencao'?'ATENÇÃO':'OK';
    const acao = p.estoque_atual<0 ? '<span style="color:var(--red)">Repor urgente</span>'
      : p.status==='atencao' ? '<span style="color:var(--yellow)">Solicitar pedido</span>'
      : '<span style="color:var(--text2)">—</span>';
    return `<tr>
      <td>${p.produto}</td>
      <td style="color:var(--text2);font-size:.78rem">${p.cat_nome}</td>
      <td style="color:${p.estoque_atual<0?'var(--red)':'var(--text)'}">${fmtN(p.estoque_atual)}</td>
      <td style="color:var(--text2)">${fmtN(p.estoque_minimo)}</td>
      <td><span class="badge ${cls}">${lbl}</span></td>
      <td style="font-size:.78rem">${acao}</td>
    </tr>`;
  }).join('');
}

// ═══ COMPRAS ═══
function initCompras() {
  const compras   = NOTAS_COMPRA || [];
  const totComp   = compras.reduce((s,n) => s+( n.vNF||0), 0);
  const totProd   = compras.reduce((s,n) => s+(n.vProd||0), 0);

  // Agrupa por fornecedor
  const porFornec = {};
  compras.forEach(n => {
    const nome = n.xNome || 'Desconhecido';
    if (!porFornec[nome]) porFornec[nome] = {qt:0, val:0, cnpj:n.CNPJ||''};
    porFornec[nome].qt++;
    porFornec[nome].val += n.vNF||0;
  });
  const fornArr = Object.entries(porFornec).sort((a,b) => b[1].val - a[1].val);
  const maiorForn = fornArr[0];

  // ─ Cards ──────────────────────────────────────────────────
  document.getElementById('cards-comp').innerHTML = [
    {label:'Total em Compras (NF)',    value:fmt(totComp),          sub:`${compras.length} notas fiscais recebidas`, cls:'red',    icon:'&#128666;'},
    {label:'Fornecedores com NF',      value:fornArr.length,         sub:'No período 01–19/03/2026',                  cls:'blue',   icon:'&#127981;'},
    {label:'Maior Fornecedor',         value:maiorForn?fmt(maiorForn[1].val):'—',
                                       sub:maiorForn?maiorForn[0].slice(0,28):'—',                                   cls:'yellow', icon:'&#127942;'},
    {label:'Ticket Médio por NF',      value:fmt(compras.length?totComp/compras.length:0), sub:'Valor médio por nota recebida', cls:'',  icon:'&#128200;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // ─ Ranking de fornecedores ─────────────────────────────────
  const maxFV = fornArr[0]?.[1].val || 1;
  document.getElementById('comp-por-fornec').innerHTML = fornArr.length === 0
    ? '<p style="color:var(--text2);font-size:.82rem">Nenhuma nota de compra encontrada.</p>'
    : fornArr.map(([nome, v], i) => `
      <div style="margin-bottom:11px">
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:.83rem;margin-bottom:4px">
          <span style="display:flex;align-items:center;gap:7px">
            <span style="background:var(--bg3);border-radius:50%;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;color:${i===0?'var(--accent2)':'var(--text2)'}">${i+1}</span>
            <span style="font-weight:500">${nome}</span>
          </span>
          <span style="display:flex;flex-direction:column;align-items:flex-end">
            <span style="color:var(--red);font-weight:700">${fmt(v.val)}</span>
            <span style="font-size:.7rem;color:var(--text2)">${v.qt} nota${v.qt!==1?'s':''}</span>
          </span>
        </div>
        <div class="prog-wrap"><div class="prog-bar" style="width:${(v.val/maxFV*100).toFixed(0)}%;background:var(--red)"></div></div>
      </div>`).join('');

  // ─ Preenche filtro de fornecedor ──────────────────────────
  const sel = document.getElementById('flt-comp-forn');
  if (sel) {
    fornArr.forEach(([nome]) => {
      const o = document.createElement('option');
      o.value = nome; o.textContent = nome; sel.appendChild(o);
    });
  }

  // ─ Tabela de notas ────────────────────────────────────────
  filtrarCompras();

  // ─ Gráfico compras por dia ────────────────────────────────
  const porDia = {};
  compras.forEach(n => {
    const dia = (n.dhEmi||'').slice(0,10);
    if (dia) porDia[dia] = (porDia[dia]||0) + (n.vNF||0);
  });
  const diasK = Object.keys(porDia).sort();
  const diasV = diasK.map(d => porDia[d]);
  const diasL = diasK.map(d => d.slice(5).replace('-','/'));
  setTimeout(() => drawBarChart('chart-compras-dia', diasL, diasV, '#ef4444'), 50);

  // ─ Histórico de caixas ────────────────────────────────────
  const caixaData = CAIXAS.data || [];
  const tbody = document.querySelector('#tbl-caixas tbody');
  tbody.innerHTML = caixaData.length === 0
    ? '<tr><td colspan="6" style="color:var(--text2);text-align:center">Nenhum caixa encontrado</td></tr>'
    : caixaData.slice(0,30).map(cx => {
        const rec  = cx.total_receita||cx.receita||0;
        const desp = cx.total_despesa||cx.despesa||0;
        const sal  = rec - desp;
        return `<tr>
          <td>${fmtDate(cx.data_abertura||cx.created_at)}</td>
          <td>${cx.data_fechamento?fmtDate(cx.data_fechamento):'<span style="color:var(--yellow)">Aberto</span>'}</td>
          <td style="color:var(--green)">${fmt(rec)}</td>
          <td style="color:var(--red)">${fmt(desp)}</td>
          <td style="color:${sal>=0?'var(--green)':'var(--red)'}">${fmt(sal)}</td>
          <td><span class="badge ${cx.data_fechamento?'badge-ok':'badge-warn'}">${cx.data_fechamento?'FECHADO':'ABERTO'}</span></td>
        </tr>`;
      }).join('');
}

function filtrarCompras() {
  const compras = NOTAS_COMPRA || [];
  const busca   = (document.getElementById('busca-comp')?.value||'').toLowerCase();
  const forn    = document.getElementById('flt-comp-forn')?.value||'';

  let lista = compras.filter(n => {
    if (forn && n.xNome !== forn) return false;
    if (busca) {
      return (n.xNome||'').toLowerCase().includes(busca) ||
             String(n.nNF||'').includes(busca) ||
             (n.CNPJ||'').includes(busca) ||
             (n.natOp||'').toLowerCase().includes(busca);
    }
    return true;
  });
  lista.sort((a,b) => new Date(b.dhEmi) - new Date(a.dhEmi));

  const tbody = document.querySelector('#tbl-notas-comp tbody');
  if (!tbody) return;
  if (!lista.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--text2);padding:20px">Nenhuma nota encontrada</td></tr>';
    return;
  }
  tbody.innerHTML = lista.map(n => {
    const cnpj = (n.CNPJ||'').replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    const stat = (n.cSitNFe===1||n.status===0)
      ? '<span class="badge badge-ok">Autorizada</span>'
      : '<span class="badge badge-warn">'+n.cSitNFe+'</span>';
    return `<tr>
      <td>${fmtDate(n.dhEmi)}</td>
      <td>${n.nNF||'-'} <span style="font-size:.68rem;color:var(--text2)">s${n.serie||1}</span></td>
      <td style="font-weight:500">${n.xNome||'-'}</td>
      <td style="font-size:.75rem;color:var(--text2)">${cnpj||'-'}</td>
      <td style="font-size:.78rem;color:var(--text2)">${n.natOp||'-'}</td>
      <td style="color:var(--text2)">${fmt(n.vProd||0)}</td>
      <td style="font-weight:700;color:var(--red)">${fmt(n.vNF||0)}</td>
      <td>${stat}</td>
    </tr>`;
  }).join('');
}

// ═══ CHARTS ═══
function drawBarChart(id, labels, values, color) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth || 600;
  canvas.width = W; canvas.height = +canvas.getAttribute('height')||180;
  const H = canvas.height;
  const p = {t:20,r:20,b:40,l:65};
  const cw = W-p.l-p.r, ch = H-p.t-p.b;
  ctx.clearRect(0,0,W,H);
  const max = Math.max(...values,1);
  const bw  = Math.max(4, cw/values.length-4);
  ctx.strokeStyle='#2e3347'; ctx.lineWidth=1;
  for(let i=0;i<=4;i++){
    const y=p.t+ch-(i/4)*ch;
    ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(p.l+cw,y);ctx.stroke();
    ctx.fillStyle='#64748b';ctx.font='10px sans-serif';ctx.textAlign='right';
    ctx.fillText('R$'+(max*i/4/1000).toFixed(1)+'k',p.l-3,y+4);
  }
  values.forEach((v,i)=>{
    const x=p.l+i*(cw/values.length)+(cw/values.length-bw)/2;
    const bh=(v/max)*ch, y=p.t+ch-bh;
    const g=ctx.createLinearGradient(0,y,0,y+bh);
    g.addColorStop(0,color); g.addColorStop(1,color+'44');
    ctx.fillStyle=g;
    ctx.beginPath();
    ctx.roundRect?ctx.roundRect(x,y,bw,bh,3):ctx.rect(x,y,bw,bh);
    ctx.fill();
    if(labels[i]&&values.length<=25){
      ctx.fillStyle='#64748b';ctx.font='9px sans-serif';ctx.textAlign='center';
      ctx.fillText(labels[i],x+bw/2,H-p.b+13);
    }
  });
}

function drawLineChart(id, labels, values, color) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth || 600;
  canvas.width = W; canvas.height = +canvas.getAttribute('height')||240;
  const H = canvas.height;
  const p = {t:20,r:20,b:40,l:75};
  const cw=W-p.l-p.r, ch=H-p.t-p.b;
  ctx.clearRect(0,0,W,H);
  const min=Math.min(...values), max=Math.max(...values,min+1), range=max-min;
  const toY = v => p.t+ch-((v-min)/range)*ch;
  ctx.strokeStyle='#2e3347';ctx.lineWidth=1;
  for(let i=0;i<=4;i++){
    const y=p.t+(i/4)*ch;
    ctx.beginPath();ctx.moveTo(p.l,y);ctx.lineTo(p.l+cw,y);ctx.stroke();
    const val=max-(range*i/4);
    ctx.fillStyle='#64748b';ctx.font='10px sans-serif';ctx.textAlign='right';
    ctx.fillText('R$'+(val/1000).toFixed(0)+'k',p.l-3,y+4);
  }
  const n=values.length;
  ctx.beginPath();
  values.forEach((v,i)=>{const x=p.l+i*(cw/(n-1||1));i===0?ctx.moveTo(x,toY(v)):ctx.lineTo(x,toY(v));});
  ctx.lineTo(p.l+cw,p.t+ch);ctx.lineTo(p.l,p.t+ch);ctx.closePath();
  const g=ctx.createLinearGradient(0,p.t,0,p.t+ch);
  g.addColorStop(0,color+'44');g.addColorStop(1,color+'05');
  ctx.fillStyle=g;ctx.fill();
  ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=2;
  values.forEach((v,i)=>{const x=p.l+i*(cw/(n-1||1));i===0?ctx.moveTo(x,toY(v)):ctx.lineTo(x,toY(v));});
  ctx.stroke();
  values.forEach((v,i)=>{
    const x=p.l+i*(cw/(n-1||1));
    ctx.beginPath();ctx.arc(x,toY(v),3,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();
    if(labels[i]&&n<=25){ctx.fillStyle='#64748b';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText(labels[i],x,H-p.b+13);}
  });
}

function drawDonut(id, labels, values, colors) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth || 400;
  canvas.width = W; canvas.height = +canvas.getAttribute('height')||180;
  const H = canvas.height;
  ctx.clearRect(0,0,W,H);
  const total = values.reduce((s,v)=>s+v,0);
  if (!total) return;
  const cx=W*0.35, cy=H/2, r=Math.min(cx,cy)*0.82, ri=r*0.55;
  let ang=-Math.PI/2;
  values.forEach((v,i)=>{
    const sl=(v/total)*Math.PI*2;
    ctx.beginPath();ctx.moveTo(cx,cy);ctx.arc(cx,cy,r,ang,ang+sl);ctx.closePath();
    ctx.fillStyle=colors[i%colors.length];ctx.fill();
    ang+=sl;
  });
  ctx.beginPath();ctx.arc(cx,cy,ri,0,Math.PI*2);ctx.fillStyle='#1a1d27';ctx.fill();
  ctx.fillStyle='#e2e8f0';ctx.font='bold 12px sans-serif';ctx.textAlign='center';
  ctx.fillText(fmt(total),cx,cy+5);
  const lx=W*0.65, ly=cy-(labels.length*18)/2;
  labels.forEach((l,i)=>{
    ctx.fillStyle=colors[i%colors.length];ctx.fillRect(lx,ly+i*20,9,9);
    ctx.fillStyle='#94a3b8';ctx.font='10px sans-serif';ctx.textAlign='left';
    ctx.fillText(l+' ('+((values[i]/total)*100).toFixed(0)+'%)',lx+13,ly+i*20+8);
  });
}

// ═══ CHAT ═══
function sendChatInput() {
  const el = document.getElementById('chat-input');
  const txt = el.value.trim();
  if (!txt) return;
  el.value='';
  sendChat(txt);
}

function sendChat(txt) {
  const msgs = document.getElementById('chat-msgs');
  msgs.innerHTML += `<div class="msg user">${txt}</div>`;
  msgs.scrollTop = msgs.scrollHeight;
  setTimeout(()=>{
    const resp = agentRespond(txt);
    msgs.innerHTML += `<div class="msg agent">${resp}</div>`;
    msgs.scrollTop = msgs.scrollHeight;
  },350);
}

function agentRespond(q) {
  const ql = q.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const receita   = EXTOPT.order_revenue_total||0;
  const despesa   = EXTOPT.order_expense_total||0;
  const saldo     = receita-despesa;
  const nPed      = EXTOPT.order_count||0;
  const ticketMed = nPed>0?receita/nPed:0;

  if(/melhor dia|maior faturamento/.test(ql)){
    const best=[...VPD].sort((a,b)=>b.faturamento-a.faturamento)[0];
    const week=['domingo','segunda','terça','quarta','quinta','sexta','sábado'];
    const ds=new Date(best.data+'T12:00:00');
    return `&#128197; Melhor dia: <strong>${best.data.split('-').reverse().join('/')}</strong> (${week[ds.getDay()]})<br>&#128176; Faturamento: <strong>${fmt(best.faturamento)}</strong><br>&#128219; Pedidos: <strong>${best.pedidos}</strong>`;
  }
  if(/pior dia|menor faturamento/.test(ql)){
    const worst=[...VPD].filter(d=>d.faturamento>0).sort((a,b)=>a.faturamento-b.faturamento)[0];
    return `&#128202; Pior dia: <strong>${worst?.data?.split('-').reverse().join('/')||'-'}</strong> com <strong>${fmt(worst?.faturamento||0)}</strong>`;
  }
  if(/semana|ultimos 7|últimos 7/.test(ql)){
    const s=VPD.slice(-7),tot=s.reduce((x,d)=>x+d.faturamento,0),ped=s.reduce((x,d)=>x+d.pedidos,0);
    return `&#128200; Últimos 7 dias:<br>&#128176; Faturamento: <strong>${fmt(tot)}</strong><br>&#128219; Pedidos: <strong>${ped}</strong><br>&#127915; Ticket: <strong>${fmt(ped>0?tot/ped:0)}</strong>`;
  }
  if(/resumo|como foi o mes|como foi o mês/.test(ql)){
    return `&#128200; <strong>Resumo Março 2026 (01—19):</strong><br>
    &#128176; Receita: <strong>${fmt(receita)}</strong><br>
    &#128203; Despesas: <strong>${fmt(despesa)}</strong><br>
    &#9878; Resultado: <strong style="color:${saldo>=0?'#22c55e':'#ef4444'}">${fmt(saldo)}</strong><br>
    &#128219; Lançamentos: <strong>${nPed}</strong><br>
    &#127915; Ticket médio: <strong>${fmt(ticketMed)}</strong>`;
  }
  if(/tirar|remover|cardapio|cardápio/.test(ql)){
    const labels=DASH.chart_produto_labels||[],qtds=DASH.chart_produto_data||[];
    const menores=labels.map((l,i)=>({n:l,q:qtds[i]})).filter(p=>p.q>0).sort((a,b)=>a.q-b.q).slice(0,5);
    return `&#127869; <strong>Candidatos a remover</strong> (menos vendidos no mês):<br>
    ${menores.map((p,i)=>`${i+1}. <strong>${p.n}</strong> — ${p.q.toLocaleString('pt-BR')} un`).join('<br>')}<br>
    <small style="color:var(--text2)">Verifique a margem antes de decidir.</small>`;
  }
  if(/rentavel|rentável|mais lucro|mais lucrativo/.test(ql)){
    const top=PRODS.filter(p=>p.valor_venda>0&&p.valor_custo>0)
      .map(p=>({...p,mg:(p.valor_venda-p.valor_custo)/p.valor_venda*100}))
      .sort((a,b)=>b.mg-a.mg).slice(0,5);
    if(!top.length) return 'ℹ️ Não há dados de custo cadastrados nos produtos.';
    return `&#128142; <strong>Mais rentáveis (maior margem):</strong><br>
    ${top.map((p,i)=>`${i+1}. <strong>${p.descricao}</strong> — ${p.mg.toFixed(1)}%`).join('<br>')}`;
  }
  if(/falta|estoque|critico|crítico|acabando/.test(ql)){
    const crit=[];
    (ESTMIN.categorias||[]).forEach(cat=>(cat.produtos||[]).forEach(p=>{if(p.estoque_atual<0)crit.push(`<strong>${p.produto}</strong> (${p.estoque_atual} un)`)}));
    if(!crit.length) return '&#9989; Nenhum produto com estoque negativo.';
    return `&#128680; <strong>${crit.length} produto(s) crítico(s):</strong><br>${crit.slice(0,10).join('<br>')}${crit.length>10?`<br>...e mais ${crit.length-10}.`:''}`;
  }
  if(/margem/.test(ql)){
    const ruins=PRODS.filter(p=>p.valor_venda>0&&p.valor_custo>0)
      .map(p=>({...p,mg:(p.valor_venda-p.valor_custo)/p.valor_venda*100}))
      .filter(p=>p.mg<60).sort((a,b)=>a.mg-b.mg).slice(0,8);
    if(!ruins.length) return '&#9989; Sem produtos com margem abaixo de 60% (com custo cadastrado).';
    return `&#9888; <strong>Margem abaixo de 60%:</strong><br>${ruins.map(p=>`• <strong>${p.descricao}</strong> — ${p.mg.toFixed(1)}%`).join('<br>')}`;
  }
  if(/despesa|gasto/.test(ql)){
    const tot=EXTRATO.filter(e=>e.type==='e').reduce((s,e)=>s+e.value,0);
    const catD={};
    EXTRATO.filter(e=>e.type==='e').forEach(e=>{const c=e.category_name||'Outros';catD[c]=(catD[c]||0)+e.value;});
    const cats=Object.entries(catD).sort((a,b)=>b[1]-a[1]).slice(0,5);
    return `&#128203; <strong>Total despesas: ${fmt(tot)}</strong><br><br>${cats.map(([c,v])=>`• ${c}: <strong>${fmt(v)}</strong>`).join('<br>')}`;
  }
  if(/fornecedor|pagar|caixa/.test(ql)){
    const pendP=EXTOPT.pending_expense_total||0, pendR=EXTOPT.pending_revenue_total||0;
    return `&#128179; <strong>Situação financeira:</strong><br>
    &#9989; Receber: <strong style="color:#22c55e">${fmt(pendR)}</strong><br>
    &#9888; Pagar: <strong style="color:#f59e0b">${fmt(pendP)}</strong><br>
    &#9878; Saldo: <strong style="color:${saldo>=0?'#22c55e':'#ef4444'}">${fmt(saldo)}</strong><br>
    ${saldo>=pendP?'&#9989; Saldo cobre os pagamentos pendentes.':'&#9888; Saldo pode ser insuficiente para os pagamentos.'}`;
  }
  if(/ticket|media|média/.test(ql)){
    return `&#127915; Ticket médio: <strong>${fmt(ticketMed)}</strong><br>Baseado em ${nPed} lançamentos.`;
  }
  if(/pagamento|pix|debito|debito|credito|crédito/.test(ql)){
    const pl=DASH.chart_pagamento_labels||[],pd=DASH.chart_pagamento_data||[];
    const tot=pd.reduce((s,v)=>s+v,0);
    return `&#128179; <strong>Pagamentos do mês:</strong><br>${pl.map((l,i)=>`• ${l}: <strong>${fmt(pd[i])}</strong> (${tot>0?((pd[i]/tot)*100).toFixed(0):0}%)`).join('<br>')}`;
  }
  if(/faturamento|receita|vendeu|venda/.test(ql)){
    const best=[...VPD].sort((a,b)=>b.faturamento-a.faturamento)[0];
    return `&#128200; <strong>Faturamento Março (01—19):</strong><br>
    Total: <strong>${fmt(receita)}</strong><br>
    Melhor dia: <strong>${best?.data?.split('-').reverse().join('/')||'-'}</strong> — ${fmt(best?.faturamento||0)}<br>
    Média diária: <strong>${fmt(receita/19)}</strong>`;
  }
  return `&#129300; Não entendi exatamente. Posso responder sobre:<br>
  • <strong>Vendas</strong> (melhor/pior dia, ticket, faturamento)<br>
  • <strong>Estoque</strong> (crítico, abaixo do mínimo)<br>
  • <strong>Financeiro</strong> (despesas, caixa, contas)<br>
  • <strong>Produtos</strong> (margem, mais vendidos, remover)<br>
  Use as sugestões acima ou tente outra pergunta. &#128522;`;
}

// ═══ DESPESAS FIXAS ═══
const CAT_ICONS = {
  energia:'⚡',funcionarios:'👤',aluguel:'🏠',agua:'💧',gas:'🔥',
  internet:'📡',manutencao:'🔧',contabilidade:'📋',seguro:'🛡',
  marketing:'📣',outros:'💼'
};
const CAT_NOMES = {
  energia:'Energia Elétrica',funcionarios:'Funcionários',aluguel:'Aluguel',
  agua:'Água',gas:'Gás',internet:'Internet/Tel',manutencao:'Manutenção',
  contabilidade:'Contabilidade',seguro:'Seguro',marketing:'Marketing',outros:'Outros'
};

function loadDespesas() {
  try { return JSON.parse(localStorage.getItem('vg_despesas_fixas')||'[]'); } catch(e){ return []; }
}
function saveDespesas(arr) { localStorage.setItem('vg_despesas_fixas', JSON.stringify(arr)); }

function adicionarDespesa() {
  const nome   = document.getElementById('df-nome').value.trim();
  const cat    = document.getElementById('df-cat').value;
  const valor  = parseFloat(document.getElementById('df-valor').value||0);
  const recorr = document.getElementById('df-recorr').value;
  const dia    = parseInt(document.getElementById('df-dia').value||0);
  const obs    = document.getElementById('df-obs').value.trim();
  if (!nome||!valor) { alert('Preencha descrição e valor.'); return; }
  const arr = loadDespesas();
  arr.push({id:Date.now(), nome, cat, valor, recorr, dia, obs});
  saveDespesas(arr);
  document.getElementById('df-nome').value='';
  document.getElementById('df-valor').value='';
  document.getElementById('df-dia').value='';
  document.getElementById('df-obs').value='';
  renderDespesas();
  // Atualiza custos fixos na precificação
  sincronizarCustosFixos(arr);
}

function deletarDespesa(id) {
  if (!confirm('Remover esta despesa?')) return;
  saveDespesas(loadDespesas().filter(d=>d.id!==id));
  renderDespesas();
}

function sincronizarCustosFixos(arr) {
  const totalMensal = arr.reduce((s,d)=>{
    if(d.recorr==='anual') return s+d.valor/12;
    if(d.recorr==='semanal') return s+d.valor*4.33;
    if(d.recorr==='quinzenal') return s+d.valor*2;
    return s+d.valor;
  },0);
  const receita = EXTOPT.order_revenue_total||1;
  const pct = Math.min(50, (totalMensal/receita*100)).toFixed(1);
  const el = document.getElementById('cfg-fixos');
  if(el) el.value = pct;
}

function renderDespesas() {
  const arr = loadDespesas();
  const hoje = new Date();
  const mesAtual = hoje.getMonth()+1;

  // Cards
  const totalMensal = arr.reduce((s,d)=>{
    if(d.recorr==='anual') return s+d.valor/12;
    if(d.recorr==='semanal') return s+d.valor*4.33;
    if(d.recorr==='quinzenal') return s+d.valor*2;
    return s+d.valor;
  },0);
  const receita = EXTOPT.order_revenue_total||1;
  const pctFixos = (totalMensal/receita*100);
  const vencendoHoje = arr.filter(d=>d.dia===hoje.getDate());
  const vencendo7d   = arr.filter(d=>d.dia>hoje.getDate()&&d.dia<=hoje.getDate()+7);

  document.getElementById('cards-desp').innerHTML = [
    {label:'Total Despesas Fixas/Mês', value:fmt(totalMensal),           sub:'Todas as categorias',    cls:'red',    icon:'📋'},
    {label:'% sobre Faturamento',      value:fmtPct(pctFixos),           sub:fmt(receita)+' de receita',cls:pctFixos>30?'red':pctFixos>20?'yellow':'green', icon:'📊'},
    {label:'Vencendo Hoje',            value:vencendoHoje.length,        sub:'Dia '+hoje.getDate(),     cls:vencendoHoje.length>0?'red':'green',  icon:'⚠️'},
    {label:'Vencendo em 7 dias',       value:vencendo7d.length,          sub:'Próximos pagamentos',     cls:vencendo7d.length>0?'yellow':'green', icon:'📅'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // Tabela
  const tbody = document.querySelector('#tbl-desp-fixas tbody');
  if (!arr.length) {
    tbody.innerHTML='<tr><td colspan="7" style="text-align:center;color:var(--text2);padding:20px">Nenhuma despesa cadastrada. Use o formulário acima.</td></tr>';
  } else {
    tbody.innerHTML = arr.map(d=>{
      const vMensal = d.recorr==='anual'?d.valor/12:d.recorr==='semanal'?d.valor*4.33:d.recorr==='quinzenal'?d.valor*2:d.valor;
      const diaStr  = d.dia ? `Dia ${d.dia}` : '—';
      const hoje2   = new Date().getDate();
      const diaCol  = d.dia===hoje2?'var(--red)':d.dia&&d.dia>hoje2&&d.dia<=hoje2+7?'var(--yellow)':'var(--text)';
      return `<tr>
        <td>${CAT_ICONS[d.cat]||'💼'} <span style="color:var(--text2)">${CAT_NOMES[d.cat]||d.cat}</span></td>
        <td><strong>${d.nome}</strong></td>
        <td style="color:var(--red);font-weight:600">${fmt(vMensal)}<br><span style="color:var(--text2);font-size:.72rem">${d.recorr==='anual'?'('+fmt(d.valor)+'/ano)':''}</span></td>
        <td style="color:var(--text2)">${d.recorr}</td>
        <td style="color:${diaCol};font-weight:600">${diaStr}</td>
        <td style="color:var(--text2);font-size:.78rem">${d.obs||'—'}</td>
        <td>
          <button class="btn-del" onclick="deletarDespesa(${d.id})" title="Remover">🗑</button>
        </td>
      </tr>`;
    }).join('');
  }

  // Total
  document.getElementById('total-desp-fixas').textContent = fmt(totalMensal);

  // Gráfico por categoria
  const porCat = {};
  arr.forEach(d=>{
    const vM = d.recorr==='anual'?d.valor/12:d.recorr==='semanal'?d.valor*4.33:d.recorr==='quinzenal'?d.valor*2:d.valor;
    porCat[d.cat]=(porCat[d.cat]||0)+vM;
  });
  const catArr = Object.entries(porCat).sort((a,b)=>b[1]-a[1]);
  const colors = ['#6366f1','#22c55e','#f59e0b','#3b82f6','#a855f7','#14b8a6','#ef4444','#f97316','#84cc16','#ec4899','#06b6d4'];
  if(catArr.length>0) drawHorizBar('chart-desp-cat', catArr.map(c=>CAT_NOMES[c[0]]||c[0]), catArr.map(c=>c[1]), colors);

  // Calendário de vencimentos
  const cal = document.getElementById('calendario-desp');
  const porDia = {};
  arr.filter(d=>d.dia).forEach(d=>{
    const vM=d.recorr==='anual'?d.valor/12:d.recorr==='semanal'?d.valor*4.33:d.recorr==='quinzenal'?d.valor*2:d.valor;
    if(!porDia[d.dia]) porDia[d.dia]=[];
    porDia[d.dia].push({nome:d.nome,valor:vM,cat:d.cat});
  });
  const dias = Object.keys(porDia).sort((a,b)=>a-b);
  const hojeD = new Date().getDate();
  cal.innerHTML = dias.length===0
    ? '<p style="color:var(--text2);font-size:.82rem">Cadastre despesas com dia de vencimento para ver o calendário.</p>'
    : dias.map(dia=>{
        const cor = parseInt(dia)===hojeD?'var(--red)':parseInt(dia)<=hojeD+7&&parseInt(dia)>hojeD?'var(--yellow)':'var(--text2)';
        const total = porDia[dia].reduce((s,x)=>s+x.valor,0);
        return `<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--border)">
          <div style="min-width:36px;height:36px;background:var(--bg3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:700;color:${cor}">${dia}</div>
          <div style="flex:1">
            ${porDia[dia].map(x=>`<div style="font-size:.82rem"><span>${CAT_ICONS[x.cat]||'💼'} ${x.nome}</span> <span style="color:var(--red);float:right">${fmt(x.valor)}</span></div>`).join('')}
          </div>
          <div style="font-size:.82rem;font-weight:700;color:var(--red);white-space:nowrap">${fmt(total)}</div>
        </div>`;
      }).join('');
}

function drawHorizBar(id, labels, values, colors) {
  const canvas = document.getElementById(id);
  if(!canvas||!values.length) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth||500;
  canvas.width=W; canvas.height=+canvas.getAttribute('height')||220;
  const H=canvas.height;
  ctx.clearRect(0,0,W,H);
  const max = Math.max(...values,1);
  const pad = {t:10,r:10,b:10,l:130};
  const cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;
  const bh=Math.min(22,(ch/labels.length)-5);
  labels.forEach((l,i)=>{
    const y=pad.t+i*(ch/labels.length)+(ch/labels.length-bh)/2;
    const bw=(values[i]/max)*cw;
    ctx.fillStyle=colors[i%colors.length];
    ctx.beginPath();
    ctx.roundRect?ctx.roundRect(pad.l,y,bw,bh,3):ctx.rect(pad.l,y,bw,bh);
    ctx.fill();
    ctx.fillStyle='#94a3b8';ctx.font='10px sans-serif';ctx.textAlign='right';
    ctx.fillText(l.slice(0,18),pad.l-6,y+bh/2+4);
    ctx.fillStyle='#e2e8f0';ctx.textAlign='left';
    ctx.fillText(fmt(values[i]),pad.l+bw+6,y+bh/2+4);
  });
}

function initDespesas() { renderDespesas(); }

// ═══ IMPOSTOS ═══
const REGIMES_IMP = {
  simples_1:  {nome:'Simples Nacional (Faixa 1)',  aliq_total:4.0,  das:4.0,  pis:0,    cofins:0,   iss:0,    irpj:0,    csll:0},
  simples_2:  {nome:'Simples Nacional (Faixa 2)',  aliq_total:7.3,  das:7.3,  pis:0,    cofins:0,   iss:0,    irpj:0,    csll:0},
  simples_3:  {nome:'Simples Nacional (Faixa 3)',  aliq_total:9.5,  das:9.5,  pis:0,    cofins:0,   iss:0,    irpj:0,    csll:0},
  presumido:  {nome:'Lucro Presumido',             aliq_total:16.33,das:0,    pis:0.65, cofins:3.0, iss:5.0,  irpj:4.8,  csll:2.88},
  real:       {nome:'Lucro Real',                  aliq_total:22.0, das:0,    pis:1.65, cofins:7.6, iss:5.0,  irpj:5.0,  csll:2.75},
};

// Datas de vencimento por tributo (simplificado)
const VENC_TRIBUTOS = {
  das:        {nome:'DAS (Simples Nacional)', dia:20, guia:'PGDAS-D'},
  pis:        {nome:'PIS',                   dia:25, guia:'DARF'},
  cofins:     {nome:'COFINS',                dia:25, guia:'DARF'},
  iss:        {nome:'ISS Municipal',         dia:10, guia:'Prefeitura'},
  irpj:       {nome:'IRPJ',                  dia:30, guia:'DARF'},
  csll:       {nome:'CSLL',                  dia:30, guia:'DARF'},
};

function calcImpostos() {
  const regime = document.getElementById('imp-regime').value;
  const fatEl  = document.getElementById('imp-fat');
  const fat    = parseFloat(fatEl.value||0) || (EXTOPT.order_revenue_total||0);
  if (!fatEl.value) fatEl.value = fat.toFixed(2);

  const r = REGIMES_IMP[regime];
  const hoje = new Date();

  // Calcula valores por tributo
  const tributos = {};
  if (r.das > 0) {
    tributos.das = fat * r.das / 100;
  } else {
    if(r.pis)    tributos.pis    = fat * r.pis    / 100;
    if(r.cofins) tributos.cofins = fat * r.cofins / 100;
    if(r.iss)    tributos.iss    = fat * r.iss    / 100;
    if(r.irpj)   tributos.irpj   = fat * r.irpj   / 100;
    if(r.csll)   tributos.csll   = fat * r.csll   / 100;
  }
  const totalImp = Object.values(tributos).reduce((s,v)=>s+v,0);
  const pctEfet  = fat>0?(totalImp/fat*100):0;

  // Cards
  const despFixas = loadDespesas().reduce((s,d)=>{
    const vM=d.recorr==='anual'?d.valor/12:d.recorr==='semanal'?d.valor*4.33:d.recorr==='quinzenal'?d.valor*2:d.valor;
    return s+vM;
  },0);
  const cmvImp     = (NOTAS_COMPRA||[]).reduce((s,n)=>s+(n.vNF||0),0);
  const despOpImp  = EXTOPT.order_expense_total||0;
  const resultadoLiq = fat - cmvImp - despOpImp - despFixas - totalImp;

  document.getElementById('cards-imp').innerHTML = [
    {label:'Total de Impostos',    value:fmt(totalImp),      sub:fmtPct(pctEfet)+' do faturamento',            cls:'red',                          icon:'&#127963;'},
    {label:'CMV (Notas de Compra)',value:fmt(cmvImp),        sub:fmtPct(fat>0?cmvImp/fat*100:0)+' da receita', cls:'red',                          icon:'&#128666;'},
    {label:'Despesas Fixas',       value:fmt(despFixas),     sub:'Cadastradas na aba Despesas Fixas',           cls:'yellow',                       icon:'&#128203;'},
    {label:'Resultado Líquido',    value:fmt(resultadoLiq),  sub:'Fat - CMV - Fixas - Impostos',                cls:resultadoLiq>=0?'green':'red',  icon:'&#9878;'},
  ].map(d=>`<div class="card ${d.cls}"><div class="card-icon">${d.icon}</div><div class="card-label">${d.label}</div><div class="card-value">${d.value}</div><div class="card-sub">${d.sub}</div></div>`).join('');

  // Timeline de vencimentos
  const mesAtual = hoje.getMonth()+1;
  const anoAtual = hoje.getFullYear();
  const tl = document.getElementById('tax-timeline');
  tl.innerHTML = Object.entries(tributos).map(([key, val])=>{
    const info = VENC_TRIBUTOS[key];
    const vencDate = new Date(anoAtual, mesAtual, info.dia); // próximo mês
    const diffDias = Math.ceil((vencDate-hoje)/(1000*60*60*24));
    const cls = diffDias<0?'vencido':diffDias<=7?'proximo':'ok';
    const dStr = vencDate.toLocaleDateString('pt-BR');
    return `<div class="tl-item ${cls}">
      <div class="tl-label">${info.nome}</div>
      <div class="tl-value" style="color:${cls==='vencido'?'var(--red)':cls==='proximo'?'var(--yellow)':'var(--green)'}">${fmt(val)}</div>
      <div class="tl-date">Venc: ${dStr} · via ${info.guia}</div>
      <div style="margin-top:4px"><span class="venc-badge ${cls==='vencido'?'venc-venc':cls==='proximo'?'venc-warn':'venc-ok'}">${cls==='vencido'?'VENCIDO':cls==='proximo'?diffDias+'d':'Em dia'}</span></div>
    </div>`;
  }).join('');

  // Detalhes por imposto
  const det = document.getElementById('impostos-detalhes');
  const hasSimples = r.das > 0;
  det.innerHTML = `<div class="section">
    <div class="section-title">📊 Composição — ${r.nome}</div>
    ${hasSimples ? `
    <div class="dre-row"><span>Faturamento bruto</span><span class="dre-value pos">${fmt(fat)}</span></div>
    <div class="dre-row"><span>Alíquota DAS (${fmtPct(r.das)})</span><span class="dre-value neg">-${fmt(tributos.das||0)}</span></div>
    <div class="dre-row result"><span style="font-weight:600">= Receita após DAS</span><span class="dre-value pos">${fmt(fat-(tributos.das||0))}</span></div>
    <div style="margin-top:10px;padding:10px;background:var(--bg3);border-radius:8px;font-size:.8rem;color:var(--text2)">
      ℹ️ No Simples Nacional, o DAS unifica: PIS, COFINS, ISS, IRPJ, CSLL, CPP — recolhido via PGDAS-D até o dia 20 do mês seguinte.
    </div>` : `
    ${Object.entries(tributos).map(([k,v])=>`
    <div class="dre-row">
      <span>${VENC_TRIBUTOS[k]?.nome||k} <span style="color:var(--text2);font-size:.72rem">(${fmtPct(r[k]||0)})</span></span>
      <span class="dre-value neg">-${fmt(v)}</span>
    </div>`).join('')}
    <div class="dre-row result"><span style="font-weight:600">= Total de impostos</span><span class="dre-value neg">-${fmt(totalImp)}</span></div>
    <div class="dre-row"><span style="color:var(--text2)">Receita líquida após impostos</span><span class="dre-value pos">${fmt(fat-totalImp)}</span></div>`}
  </div>
  <div class="section" style="margin-top:0">
    <div class="section-title">💡 Análise de Enquadramento</div>
    <div style="font-size:.83rem;line-height:1.8">
      ${fat*12<180000?'<span style="color:var(--green)">✅ Faturamento anual projetado abaixo de R$180k — elegível para Simples Faixa 1.</span>':
        fat*12<360000?'<span style="color:var(--green)">✅ Projeção anual até R$360k — Simples Faixa 2.</span>':
        fat*12<720000?'<span style="color:var(--yellow)">⚠️ Projeção anual até R$720k — Simples Faixa 3.</span>':
        '<span style="color:var(--red)">⚠️ Projeção acima de R$720k — verifique enquadramento com contador.</span>'}
      <br>Projeção anual: <strong>${fmt(fat*12)}</strong>
      <br>Imposto anual estimado: <strong style="color:var(--red)">${fmt(totalImp*12)}</strong>
      <br>Carga tributária efetiva: <strong>${fmtPct(pctEfet)}</strong>
    </div>
  </div>`;

  // Pizza de impostos
  if(Object.keys(tributos).length>0) {
    const labels = Object.keys(tributos).map(k=>VENC_TRIBUTOS[k]?.nome||k);
    const vals   = Object.values(tributos);
    drawDonut('chart-impostos-pizza', labels, vals, ['#6366f1','#a855f7','#3b82f6','#f59e0b','#ef4444']);
  }

  // Guia de recolhimento
  document.getElementById('guia-recolhimento').innerHTML = Object.entries(tributos).map(([k,v])=>{
    const info = VENC_TRIBUTOS[k];
    const vencDate = new Date(anoAtual, mesAtual, info.dia);
    return `<div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:5px 0">
      <span>📄 ${info.nome} — <strong>${info.guia}</strong></span>
      <span style="color:var(--red)">${fmt(v)}</span>
      <span style="color:var(--text2);font-size:.75rem">até ${vencDate.toLocaleDateString('pt-BR')}</span>
    </div>`;
  }).join('');

  // Simulação anual
  const meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const histFat = {};
  // Usa dados reais do dashboard onde disponível
  if(DASH.top_chart_labels && DASH.top_chart_data) {
    DASH.top_chart_labels.forEach((m,i)=>{ histFat[m]=DASH.top_chart_data[i]||fat; });
  }
  const tbody = document.querySelector('#tbl-imp-anual tbody');
  tbody.innerHTML = meses.map((m,i)=>{
    const f = histFat[m.toLowerCase().replace('.,','')]||fat;
    const das_v   = r.das   > 0 ? f*r.das/100   : 0;
    const pis_v   = r.pis   > 0 ? f*r.pis/100   : 0;
    const cof_v   = r.cofins> 0 ? f*r.cofins/100 : 0;
    const iss_v   = r.iss   > 0 ? f*r.iss/100   : 0;
    const ir_v    = (r.irpj >0?f*r.irpj/100:0)+(r.csll>0?f*r.csll/100:0);
    const tot     = das_v+pis_v+cof_v+iss_v+ir_v;
    const isCur   = i===mesAtual-2 || i===mesAtual-1;
    return `<tr style="${isCur?'background:var(--bg3)':''}">
      <td style="font-weight:${isCur?700:400}">${m}/26${isCur?' ◀':''}</td>
      <td>${fmt(f)}</td>
      <td>${das_v>0?`<span style="color:var(--red)">${fmt(das_v)}</span>`:'—'}</td>
      <td>${pis_v>0?fmt(pis_v):'—'}</td>
      <td>${cof_v>0?fmt(cof_v):'—'}</td>
      <td>${iss_v>0?fmt(iss_v):'—'}</td>
      <td>${ir_v>0?fmt(ir_v):'—'}</td>
      <td style="color:var(--red);font-weight:700">${fmt(tot)}</td>
    </tr>`;
  }).join('');
}

function initImpostos() {
  const fat = EXTOPT.order_revenue_total||0;
  document.getElementById('imp-fat').value = fat.toFixed(2);
  calcImpostos();
}

// ═══ NOTAS FISCAIS ═══
let _notasInited = false;

function cStatLabel(c) {
  if (c === 100 || c === 1) return '<span class="badge badge-ok">Autorizada</span>';
  if (c === 101 || c === 135) return '<span class="badge badge-warn">Cancelada</span>';
  return '<span class="badge badge-info">'+(c||'?')+'</span>';
}

function initNotas() {
  if (_notasInited) return;
  _notasInited = true;

  // ─ Notas saída ─────────────────────────────────────────────
  const nfce  = NOTAS.nfce_lista || [];
  const nfe   = NOTAS.nfe_lista  || [];
  const saida = [...nfce, ...nfe];

  // ─ Notas de Compra (Entrada) ────────────────────────────────
  const compras = NOTAS_COMPRA || [];

  // Totais
  const totSaida   = saida.reduce((a,n)   => a + (n.vNF||0), 0);
  const totCompras = compras.reduce((a,n) => a + (n.vNF||0), 0);
  const balanco    = totSaida - totCompras;

  // ─ Cards resumo ────────────────────────────────────────────
  document.getElementById('nf-cards').innerHTML = `
    <div class="nf-card saida">
      <div class="nf-card-label">&#128228; Total Saída (NFC-e + NF-e)</div>
      <div class="nf-card-value">${fmt(totSaida)}</div>
      <div class="nf-card-sub">${saida.length} nota${saida.length!==1?'s':''} emitida${saida.length!==1?'s':''}</div>
    </div>
    <div class="nf-card entrada">
      <div class="nf-card-label">&#128229; Total Compras (Notas de Entrada)</div>
      <div class="nf-card-value">${fmt(totCompras)}</div>
      <div class="nf-card-sub">${compras.length} nota${compras.length!==1?'s':''} recebida${compras.length!==1?'s':''}</div>
    </div>
    <div class="nf-card total">
      <div class="nf-card-label">&#9971; Balanço (Saída − Compras)</div>
      <div class="nf-card-value" style="color:${balanco>=0?'var(--green)':'var(--red)'}">${fmt(balanco)}</div>
      <div class="nf-card-sub">CMV via NF: ${totSaida>0?(totCompras/totSaida*100).toFixed(1)+'%':'—'}</div>
    </div>
    <div class="nf-card">
      <div class="nf-card-label">&#128200; NFC-e emitidas</div>
      <div class="nf-card-value" style="color:var(--blue)">${nfce.length}</div>
      <div class="nf-card-sub">${fmt(nfce.reduce((a,n)=>a+(n.vNF||0),0))} (cupons mod.65)</div>
    </div>
  `;

  // ─ Resumo saída por status/modelo ──────────────────────────
  const resumoSaida = {};
  saida.forEach(n => {
    const k = (n.cStat===100||n.cStat===1)?'Autorizada':'Outro';
    if (!resumoSaida[k]) resumoSaida[k] = {qt:0,val:0};
    resumoSaida[k].qt++;
    resumoSaida[k].val += n.vNF||0;
  });
  document.getElementById('nf-saida-count').textContent =
    saida.length+' nota(s) | '+
    Object.entries(resumoSaida).map(([k,v])=>k+': '+v.qt+' ('+fmt(v.val)+')').join(' · ');

  document.getElementById('nf-resumo-saida').innerHTML = `
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px">
      ${Object.entries(resumoSaida).map(([k,v])=>`
        <div style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 16px;min-width:160px">
          <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em">${k}</div>
          <div style="font-size:1.15rem;font-weight:700;color:${k==='Autorizada'?'var(--green)':'var(--red)'}">${fmt(v.val)}</div>
          <div style="font-size:.75rem;color:var(--text2)">${v.qt} nota${v.qt!==1?'s':''}</div>
        </div>`).join('')}
      <div style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 16px;min-width:160px">
        <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em">NFC-e (mod.65)</div>
        <div style="font-size:1.15rem;font-weight:700;color:var(--blue)">${fmt(nfce.reduce((a,n)=>a+(n.vNF||0),0))}</div>
        <div style="font-size:.75rem;color:var(--text2)">${nfce.length} cupons</div>
      </div>
      <div style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 16px;min-width:160px">
        <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em">NF-e Saída (mod.55)</div>
        <div style="font-size:1.15rem;font-weight:700;color:#a78bfa">${fmt(nfe.reduce((a,n)=>a+(n.vNF||0),0))}</div>
        <div style="font-size:.75rem;color:var(--text2)">${nfe.length} nota${nfe.length!==1?'s':''}</div>
      </div>
    </div>`;

  // ─ Resumo compras por fornecedor ───────────────────────────
  const porFornec = {};
  compras.forEach(n => {
    const nome = n.xNome || 'Desconhecido';
    if (!porFornec[nome]) porFornec[nome] = {qt:0,val:0,vProd:0};
    porFornec[nome].qt++;
    porFornec[nome].val   += n.vNF||0;
    porFornec[nome].vProd += n.vProd||0;
  });

  document.getElementById('nf-entrada-count').textContent =
    compras.length+' nota(s) de compra | Total: '+fmt(totCompras)+' | '+Object.keys(porFornec).length+' fornecedores';

  document.getElementById('nf-resumo-entrada').innerHTML = `
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px">
      ${Object.entries(porFornec).sort((a,b)=>b[1].val-a[1].val).map(([nome,v])=>`
        <div style="background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 16px;min-width:200px;flex:1">
          <div style="font-size:.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px">${nome}</div>
          <div style="font-size:1.1rem;font-weight:700;color:var(--green)">${fmt(v.val)}</div>
          <div style="font-size:.75rem;color:var(--text2)">${v.qt} nota${v.qt!==1?'s':''}</div>
        </div>`).join('')}
    </div>`;

  // Preenche o select de fornecedor
  const sel = document.getElementById('flt-nf-forn');
  if (sel) {
    const nomes = [...new Set(compras.map(n=>n.xNome||'?'))].sort();
    nomes.forEach(n => { const o=document.createElement('option'); o.value=n; o.textContent=n; sel.appendChild(o); });
  }

  // Armazena para uso nas tabelas
  window._nfSaida   = saida;
  window._nfEntrada = compras;
  renderNFTable('saida');
  renderNFTable('entrada');
}

function toggleNFDetail(tipo) {
  const block = document.getElementById('nf-detail-'+tipo);
  const btn   = document.getElementById('btn-det-'+tipo);
  const vis = block.classList.toggle('visible');
  btn.classList.toggle('active', vis);
  const label = tipo==='saida'?'Sa\u00edda':'Compras';
  btn.innerHTML = vis
    ? '\u25b2 Ocultar Detalhes'
    : '\uD83D\uDD0D Detalhar '+label;
}

function renderNFTable(tipo) {
  const tbody = document.querySelector('#tbl-nf-'+tipo+' tbody');
  if (!tbody) return;

  if (tipo === 'saida') {
    const notas  = window._nfSaida || [];
    const busca  = (document.getElementById('busca-nf-saida')?.value||'').toLowerCase();
    const modelo = document.getElementById('flt-nf-saida')?.value||'todas';

    let lista = notas.filter(n => {
      if (modelo!=='todas' && String(n.modelo||n.mod)!==modelo) return false;
      if (busca) {
        const dest = n.destinatario?.xNome||'';
        return dest.toLowerCase().includes(busca) ||
               String(n.nNF||'').includes(busca) ||
               (n.chNFe||'').includes(busca);
      }
      return true;
    });
    lista.sort((a,b)=>new Date(b.dhEmi||b.data)-new Date(a.dhEmi||a.data));

    if (!lista.length) {
      tbody.innerHTML='<tr><td colspan="7" style="text-align:center;color:var(--text2);padding:20px">Nenhuma nota encontrada</td></tr>';
      return;
    }
    tbody.innerHTML = lista.map(n=>{
      const dest = n.destinatario?.xNome||'(consumidor)';
      const modLabel = (n.modelo||n.mod)===65
        ? '<span class="nf-type-label nf-type-nfce">NFC-e</span>'
        : '<span class="nf-type-label nf-type-nfe">NF-e</span>';
      return `<tr>
        <td>${fmtDate(n.dhEmi||n.data)}</td>
        <td>${n.nNF||'-'} <span style="font-size:.68rem;color:var(--text2)">s${n.serie||1}</span></td>
        <td>${modLabel}</td>
        <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${dest}">${dest}</td>
        <td style="font-size:.78rem;color:var(--text2)">${n.natOp||'-'}</td>
        <td style="font-weight:600;color:var(--blue)">${fmt(n.vNF||0)}</td>
        <td>${cStatLabel(n.cStat)}</td>
      </tr>`;
    }).join('');

  } else {
    // Notas de Compra
    const notas = window._nfEntrada || [];
    const busca = (document.getElementById('busca-nf-entrada')?.value||'').toLowerCase();
    const forn  = document.getElementById('flt-nf-forn')?.value||'';

    let lista = notas.filter(n => {
      if (forn && n.xNome !== forn) return false;
      if (busca) {
        return (n.xNome||'').toLowerCase().includes(busca) ||
               String(n.nNF||'').includes(busca) ||
               (n.CNPJ||'').includes(busca);
      }
      return true;
    });
    lista.sort((a,b)=>new Date(b.dhEmi)-new Date(a.dhEmi));

    if (!lista.length) {
      tbody.innerHTML='<tr><td colspan="8" style="text-align:center;color:var(--text2);padding:20px">Nenhuma nota de compra encontrada</td></tr>';
      return;
    }
    tbody.innerHTML = lista.map(n=>{
      const cnpj = (n.CNPJ||'').replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,'$1.$2.$3/$4-$5');
      return `<tr>
        <td>${fmtDate(n.dhEmi)}</td>
        <td>${n.nNF||'-'} <span style="font-size:.68rem;color:var(--text2)">s${n.serie||1}</span></td>
        <td style="font-size:.82rem">${n.xNome||'-'}</td>
        <td style="font-size:.75rem;color:var(--text2)">${cnpj||'-'}</td>
        <td style="font-size:.78rem;color:var(--text2)">${n.natOp||'-'}</td>
        <td style="color:var(--text2)">${fmt(n.vProd||0)}</td>
        <td style="font-weight:600;color:var(--green)">${fmt(n.vNF||0)}</td>
        <td>${cStatLabel(n.cSitNFe)}</td>
      </tr>`;
    }).join('');
  }
}

// ═══ INIT ═══
document.addEventListener('DOMContentLoaded',()=>{
  initVisao();
  initFinanceiro();
  initProdutos();
  initEstoque();
  initCompras();
  initPrecificacao();
  initDespesas();
  initImpostos();
});
window.addEventListener('resize',()=>{
  const active=document.querySelector('.page.active')?.id;
  if(active==='tab-visao') redrawVisao();
  if(active==='tab-financeiro') redrawFluxo();
});
</script>
</body>
</html>"""

# Injeta os dados no placeholder
final = HTML.replace('__DATA_PLACEHOLDER__', DATA_JS)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8", errors="replace") as f:
    f.write(final)

print(f"Dashboard gerado: {OUT}")
print(f"Tamanho: {OUT.stat().st_size/1024:.0f} KB")
