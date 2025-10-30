"""
Script para gerar tabelas de modulação por mês
Cria 3 tabelas HTML mostrando modulação por hora para cada mês
"""
import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv('resultados/dados_completos.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['data'] = pd.to_datetime(df['data'])

# Calcular modulação para todos os meses
def calcular_modulacao_mensal(df):
    """Calcula modulação por mês e hora"""

    # Adicionar colunas necessárias
    df['ano_mes'] = df['timestamp'].dt.to_period('M').astype(str)
    df['hora'] = df['timestamp'].dt.hour
    df['minuto'] = df['timestamp'].dt.minute
    df['hora_decimal'] = df['hora'] + df['minuto'] / 60.0

    # Calcular médias diárias para cada dia
    df['data_str'] = df['timestamp'].dt.date
    medias_diarias = df.groupby(['ano_mes', 'data_str']).agg({
        'geracao_total': 'mean',
        'geracao_referencia_total': 'mean',
        'NE_UEE': 'mean'
    }).reset_index()
    medias_diarias.columns = ['ano_mes', 'data_str', 'media_dia_real', 'media_dia_ref', 'media_dia_prev']

    # Merge
    df = df.merge(medias_diarias, on=['ano_mes', 'data_str'], how='left')

    # Calcular percentual
    df['pct_real'] = (df['geracao_total'] / df['media_dia_real']) * 100
    df['pct_ref'] = (df['geracao_referencia_total'] / df['media_dia_ref']) * 100
    df['pct_prev'] = (df['NE_UEE'] / df['media_dia_prev']) * 100

    # Arredondar hora para agrupar
    df['hora_int'] = df['hora_decimal'].round().astype(int)

    # Calcular média por mês e hora
    resultado = df.groupby(['ano_mes', 'hora_int']).agg({
        'pct_real': 'mean',
        'pct_ref': 'mean',
        'pct_prev': 'mean'
    }).reset_index()

    return resultado

print("Calculando modulação por mês...")
modulacao = calcular_modulacao_mensal(df)

# Pivotar dados para ter meses nas linhas e horas nas colunas
pivot_real = modulacao.pivot(index='ano_mes', columns='hora_int', values='pct_real')
pivot_ref = modulacao.pivot(index='ano_mes', columns='hora_int', values='pct_ref')
pivot_prev = modulacao.pivot(index='ano_mes', columns='hora_int', values='pct_prev')

# Ordenar meses do mais novo para o mais antigo
meses_ordenados = sorted(pivot_real.index, reverse=True)
pivot_real = pivot_real.loc[meses_ordenados]
pivot_ref = pivot_ref.loc[meses_ordenados]
pivot_prev = pivot_prev.loc[meses_ordenados]

# Garantir que temos todas as horas de 0 a 24
horas = list(range(25))
for hora in horas:
    if hora not in pivot_real.columns:
        pivot_real[hora] = np.nan
    if hora not in pivot_ref.columns:
        pivot_ref[hora] = np.nan
    if hora not in pivot_prev.columns:
        pivot_prev[hora] = np.nan

pivot_real = pivot_real[horas]
pivot_ref = pivot_ref[horas]
pivot_prev = pivot_prev[horas]

def gerar_html_tabela(pivot_data, titulo, cor):
    """Gera HTML para uma tabela"""
    html = f'''
    <div class="tabela-container">
        <h3 style="color: {cor};">{titulo}</h3>
        <div class="tabela-scroll">
            <table class="tabela-modulacao">
                <thead>
                    <tr>
                        <th class="mes-col">Mês</th>
'''

    # Cabeçalho das horas
    for hora in range(25):
        html += f'                        <th>{hora:02d}:00</th>\n'

    html += '''                    </tr>
                </thead>
                <tbody>
'''

    # Dados
    for mes in pivot_data.index:
        html += f'                    <tr>\n                        <td class="mes-col">{mes}</td>\n'
        for hora in range(25):
            valor = pivot_data.loc[mes, hora]
            if pd.isna(valor):
                html += '                        <td class="na-cell">-</td>\n'
            else:
                # Colorir células baseado no valor
                if valor < 80:
                    classe = 'low'
                elif valor > 120:
                    classe = 'high'
                else:
                    classe = 'mid'
                html += f'                        <td class="{classe}">{valor:.1f}%</td>\n'
        html += '                    </tr>\n'

    html += '''                </tbody>
            </table>
        </div>
    </div>
'''
    return html

print("Gerando HTML...")

# HTML completo
html_completo = f'''<!DOCTYPE html>
<html>
<head>
    <title>Tabelas de Modulação por Mês</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .descricao {{
            color: #666;
            font-size: 1.1em;
            line-height: 1.6;
            max-width: 1200px;
            margin: 15px auto;
        }}
        .tabela-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin: 30px auto;
            max-width: 95%;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        .tabela-container h3 {{
            text-align: center;
            font-size: 1.8em;
            margin: 0 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }}
        .tabela-scroll {{
            overflow-x: auto;
            margin-top: 20px;
        }}
        .tabela-modulacao {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        .tabela-modulacao th {{
            background: #667eea;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
            border: 1px solid #5568d3;
        }}
        .tabela-modulacao th.mes-col {{
            background: #764ba2;
            min-width: 100px;
            position: sticky;
            left: 0;
            z-index: 11;
        }}
        .tabela-modulacao td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #ddd;
            font-size: 0.95em;
        }}
        .tabela-modulacao td.mes-col {{
            font-weight: bold;
            background: #f8f9fa;
            position: sticky;
            left: 0;
            z-index: 5;
            border-right: 2px solid #764ba2;
        }}
        .tabela-modulacao tr:nth-child(even) td:not(.mes-col) {{
            background: #f8f9fa;
        }}
        .tabela-modulacao tr:hover td:not(.mes-col) {{
            background: #e3f2fd;
        }}
        .low {{
            background: #ffebee !important;
            color: #c62828;
            font-weight: bold;
        }}
        .mid {{
            background: #fff9e6 !important;
            color: #555;
        }}
        .high {{
            background: #e8f5e9 !important;
            color: #2e7d32;
            font-weight: bold;
        }}
        .na-cell {{
            background: #f5f5f5 !important;
            color: #999;
        }}
        .legenda {{
            background: #FFF3CD;
            border: 2px solid #FFC107;
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            max-width: 1200px;
        }}
        .legenda h4 {{
            color: #F57C00;
            margin-top: 0;
        }}
        .legenda-cores {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        .legenda-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .cor-box {{
            width: 40px;
            height: 25px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }}
        .nav {{
            text-align: center;
            margin: 20px 0;
        }}
        .nav a {{
            display: inline-block;
            padding: 12px 30px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transition: all 0.3s;
        }}
        .nav a:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.25);
            background: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Tabelas de Modulação por Mês</h1>
        <div class="descricao">
            <strong>Modulação Diária:</strong> Percentual em relação à média do dia<br>
            <strong>Leitura:</strong> Valores > 100% indicam geração acima da média diária | Valores < 100% indicam geração abaixo da média<br>
            <strong>Período:</strong> Outubro/2021 a Outubro/2025 | <strong>Dados:</strong> Média mensal por hora
        </div>
    </div>

    <div class="legenda">
        <h4>🎨 Legenda de Cores</h4>
        <div class="legenda-cores">
            <div class="legenda-item">
                <div class="cor-box" style="background: #e8f5e9;"></div>
                <span><strong>Verde:</strong> Alta geração (> 120%)</span>
            </div>
            <div class="legenda-item">
                <div class="cor-box" style="background: #fff9e6;"></div>
                <span><strong>Amarelo:</strong> Geração média (80% - 120%)</span>
            </div>
            <div class="legenda-item">
                <div class="cor-box" style="background: #ffebee;"></div>
                <span><strong>Vermelho:</strong> Baixa geração (< 80%)</span>
            </div>
        </div>
    </div>

    <div class="nav">
        <a href="index.html">← Voltar para Análise Principal</a>
    </div>

'''

# Adicionar as 3 tabelas
html_completo += gerar_html_tabela(pivot_real, '🔵 Geração Real - Modulação por Hora (%)', '#2196F3')
html_completo += gerar_html_tabela(pivot_ref, '🟠 Geração Referência - Modulação por Hora (%)', '#FF9800')
html_completo += gerar_html_tabela(pivot_prev, '🟢 Previsão NE_UEE - Modulação por Hora (%)', '#4CAF50')

html_completo += '''
    <div class="nav" style="margin-top: 40px;">
        <a href="index.html">← Voltar para Análise Principal</a>
    </div>

    <script>
        // Log de carregamento
        console.log('Tabelas de modulação carregadas com sucesso!');
    </script>
</body>
</html>
'''

# Salvar HTML
with open('tabelas_modulacao.html', 'w', encoding='utf-8') as f:
    f.write(html_completo)

print("\n" + "="*80)
print("✅ TABELAS GERADAS COM SUCESSO!")
print("="*80)
print(f"\nArquivo salvo: tabelas_modulacao.html")
print(f"Meses incluídos: {len(pivot_real)} meses")
print(f"Horas por mês: 0:00 a 24:00 (25 colunas)")
print("\nTabelas geradas:")
print("  1. 🔵 Geração Real")
print("  2. 🟠 Geração Referência")
print("  3. 🟢 Previsão NE_UEE")
