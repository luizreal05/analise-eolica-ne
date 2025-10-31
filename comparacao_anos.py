"""
Script para comparar o mesmo mês entre diferentes anos
Gera gráficos de modulação e tabelas comparativas
"""
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

print("="*80)
print("COMPARAÇÃO ENTRE ANOS - MESMO MÊS")
print("="*80)

# Carregar dados
print("\nCarregando dados...")
df_ne = pd.read_csv('resultados/dados_completos.csv')
df_ne['timestamp'] = pd.to_datetime(df_ne['timestamp'])

MESES_NOMES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

def calcular_modulacao(df, tem_previsao=True):
    """Calcula modulação para cada ano-mês"""
    df['ano'] = df['timestamp'].dt.year
    df['mes'] = df['timestamp'].dt.month
    df['hora'] = df['timestamp'].dt.hour
    df['minuto'] = df['timestamp'].dt.minute
    df['hora_decimal'] = df['hora'] + df['minuto'] / 60.0
    df['data'] = df['timestamp'].dt.date

    # Calcular médias diárias
    if tem_previsao:
        cols_geracao = ['geracao_total', 'geracao_referencia_total', 'NE_UEE']
        medias_diarias = df.groupby(['ano', 'mes', 'data']).agg({
            'geracao_total': 'mean',
            'geracao_referencia_total': 'mean',
            'NE_UEE': 'mean'
        }).reset_index()
        medias_diarias.columns = ['ano', 'mes', 'data', 'media_dia_real', 'media_dia_ref', 'media_dia_prev']
    else:
        cols_geracao = ['geracao', 'geracao_referencia']
        medias_diarias = df.groupby(['ano', 'mes', 'data']).agg({
            'geracao': 'mean',
            'geracao_referencia': 'mean'
        }).reset_index()
        medias_diarias.columns = ['ano', 'mes', 'data', 'media_dia_real', 'media_dia_ref']

    # Merge
    df = df.merge(medias_diarias, on=['ano', 'mes', 'data'], how='left')

    # Calcular percentual
    if tem_previsao:
        df['pct_real'] = (df['geracao_total'] / df['media_dia_real']) * 100
        df['pct_ref'] = (df['geracao_referencia_total'] / df['media_dia_ref']) * 100
        df['pct_prev'] = (df['NE_UEE'] / df['media_dia_prev']) * 100
    else:
        df['pct_real'] = (df['geracao'] / df['media_dia_real']) * 100
        df['pct_ref'] = (df['geracao_referencia'] / df['media_dia_ref']) * 100

    # Arredondar hora
    df['hora_int'] = df['hora_decimal'].round().astype(int)

    # Calcular média por ano-mês-hora
    if tem_previsao:
        resultado = df.groupby(['ano', 'mes', 'hora_int']).agg({
            'pct_real': 'mean',
            'pct_ref': 'mean',
            'pct_prev': 'mean'
        }).reset_index()
    else:
        resultado = df.groupby(['ano', 'mes', 'hora_int']).agg({
            'pct_real': 'mean',
            'pct_ref': 'mean'
        }).reset_index()

    return resultado


def calcular_modulacao_diaria_mes(df_mes):
    """Calcula modulação diária para preservar série temporal do mês."""
    df_mes = df_mes.copy().sort_values('timestamp')

    df_mes['hora'] = df_mes['timestamp'].dt.hour
    df_mes['minuto'] = df_mes['timestamp'].dt.minute
    df_mes['hora_decimal'] = df_mes['hora'] + df_mes['minuto'] / 60.0
    df_mes['data'] = df_mes['timestamp'].dt.date

    agregacoes = {
        'geracao_total': 'mean',
        'geracao_referencia_total': 'mean'
    }
    tem_previsao = 'NE_UEE' in df_mes.columns and df_mes['NE_UEE'].notna().any()
    if tem_previsao:
        agregacoes['NE_UEE'] = 'mean'

    medias_diarias = df_mes.groupby('data').agg(agregacoes).reset_index()
    renomear = {
        'geracao_total': 'media_dia_real',
        'geracao_referencia_total': 'media_dia_ref'
    }
    if tem_previsao:
        renomear['NE_UEE'] = 'media_dia_prev'
    medias_diarias = medias_diarias.rename(columns=renomear)

    df_mes = df_mes.merge(medias_diarias, on='data', how='left')

    df_mes['pct_real'] = np.where(
        df_mes['media_dia_real'] != 0,
        (df_mes['geracao_total'] / df_mes['media_dia_real']) * 100,
        np.nan
    )
    df_mes['pct_ref'] = np.where(
        df_mes['media_dia_ref'] != 0,
        (df_mes['geracao_referencia_total'] / df_mes['media_dia_ref']) * 100,
        np.nan
    )

    if tem_previsao:
        df_mes['pct_prev'] = np.where(
            df_mes['media_dia_prev'] != 0,
            (df_mes['NE_UEE'] / df_mes['media_dia_prev']) * 100,
            np.nan
        )

    return df_mes


def criar_modulacao_por_ano_uniforme(df, output_dir):
    """Gera gráficos de modulação por ano com escala uniforme por mês."""
    print("\nGerando modulação por ano com escala uniforme...")

    os.makedirs(output_dir, exist_ok=True)

    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['ano'] = df['timestamp'].dt.year
    df['mes'] = df['timestamp'].dt.month

    modulacoes_por_periodo = {}
    limites_por_mes = {}

    for (ano, mes), df_periodo in df.groupby(['ano', 'mes']):
        if df_periodo.empty:
            continue

        df_modulacao = calcular_modulacao_diaria_mes(df_periodo)
        modulacoes_por_periodo[(ano, mes)] = df_modulacao

        colunas_pct = ['pct_real', 'pct_ref']
        if 'pct_prev' in df_modulacao.columns:
            colunas_pct.append('pct_prev')

        valores_pct = df_modulacao[colunas_pct].to_numpy().flatten()
        valores_pct = valores_pct[np.isfinite(valores_pct)]
        max_pct = valores_pct.max() if valores_pct.size else 0

        limites_por_mes[mes] = max(limites_por_mes.get(mes, 0), max_pct)

    limites_por_mes = {
        mes: max(10 * np.ceil(limite / 10.0), 120) if limite > 0 else 120
        for mes, limite in limites_por_mes.items()
    }

    arquivos_gerados = 0
    meses_com_registro = set()

    for (ano, mes), df_modulacao in modulacoes_por_periodo.items():
        meses_com_registro.add(mes)
        y_max = limites_por_mes.get(mes, 120)

        fig, ax = plt.subplots(figsize=(14, 8))

        ax.plot(df_modulacao['timestamp'], df_modulacao['pct_real'],
                label='Geração Real', color='#2196F3', linewidth=1.5, alpha=0.8)
        ax.plot(df_modulacao['timestamp'], df_modulacao['pct_ref'],
                label='Geração Referência', color='#FF9800', linewidth=1.5, alpha=0.8)

        if 'pct_prev' in df_modulacao.columns:
            ax.plot(df_modulacao['timestamp'], df_modulacao['pct_prev'],
                    label='Previsão NE_UEE', color='#4CAF50', linewidth=2, alpha=0.9)

        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7,
                   label='Média Diária (100%)')

        ax.set_xlabel('Data', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(
            f"Modulação Diária - {ano}-{mes:02d} ({MESES_NOMES.get(mes, mes)})",
            fontsize=16, fontweight='bold', pad=20
        )
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, y_max)
        ax.set_xlim(df_modulacao['timestamp'].min(), df_modulacao['timestamp'].max())
        plt.xticks(rotation=45)

        plt.tight_layout()

        filename = f"{output_dir}/{ano}-{mes:02d}_modulacao_uniforme.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()

        arquivos_gerados += 1
        print(f"  Salvo: {filename}")

    return arquivos_gerados, meses_com_registro

def criar_graficos_comparacao(modulacao, output_dir, nome_arquivo, titulo_base=""):
    """Cria gráficos comparando anos para cada mês - apenas NE"""

    os.makedirs(output_dir, exist_ok=True)

    # Para cada mês (1 a 12)
    cores_anos = {
        2021: '#FF6B6B',
        2022: '#4ECDC4',
        2023: '#45B7D1',
        2024: '#FFA07A',
        2025: '#98D8C8'
    }

    for mes in range(1, 13):
        df_mes = modulacao[modulacao['mes'] == mes]

        if len(df_mes) == 0:
            continue

        anos_disponiveis = sorted(df_mes['ano'].unique())

        if len(anos_disponiveis) < 2:
            continue  # Precisa de pelo menos 2 anos para comparar

        # === GRÁFICO DE MODULAÇÃO - GERAÇÃO REAL ===
        fig, ax = plt.subplots(figsize=(14, 8))

        for ano in anos_disponiveis:
            df_ano = df_mes[df_mes['ano'] == ano].sort_values('hora_int')
            cor = cores_anos.get(ano, '#333333')
            ax.plot(df_ano['hora_int'], df_ano['pct_real'],
                    label=f'{ano}', color=cor, linewidth=2.5, marker='o', markersize=4, alpha=0.8)

        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Média Diária (100%)')

        ax.set_xlabel('Hora do Dia', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração Real (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(f'{titulo_base} - Modulação Geração Real - {MESES_NOMES[mes]} (Comparação entre Anos)',
                     fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 24)
        ax.set_ylim(bottom=0)
        ax.set_xticks(range(0, 25, 2))

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_real.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === GRÁFICO DE MODULAÇÃO - GERAÇÃO REFERÊNCIA ===
        fig, ax = plt.subplots(figsize=(14, 8))

        for ano in anos_disponiveis:
            df_ano = df_mes[df_mes['ano'] == ano].sort_values('hora_int')
            cor = cores_anos.get(ano, '#333333')
            ax.plot(df_ano['hora_int'], df_ano['pct_ref'],
                    label=f'{ano}', color=cor, linewidth=2.5, marker='s', markersize=4, alpha=0.8)

        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Média Diária (100%)')

        ax.set_xlabel('Hora do Dia', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração Referência (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(f'{titulo_base} - Modulação Geração Referência - {MESES_NOMES[mes]} (Comparação entre Anos)',
                     fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 24)
        ax.set_ylim(bottom=0)
        ax.set_xticks(range(0, 25, 2))

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_ref.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === GRÁFICO DE PREVISÃO ===
        fig, ax = plt.subplots(figsize=(14, 8))

        for ano in anos_disponiveis:
            df_ano = df_mes[df_mes['ano'] == ano].sort_values('hora_int')
            if 'pct_prev' in df_ano.columns:
                cor = cores_anos.get(ano, '#333333')
                ax.plot(df_ano['hora_int'], df_ano['pct_prev'],
                        label=f'{ano}', color=cor, linewidth=2.5, marker='^', markersize=4, alpha=0.8)

        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Média Diária (100%)')

        ax.set_xlabel('Hora do Dia', fontsize=12, fontweight='bold')
        ax.set_ylabel('Previsão NE_UEE (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(f'{titulo_base} - Modulação Previsão - {MESES_NOMES[mes]} (Comparação entre Anos)',
                     fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='best', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 24)
        ax.set_ylim(bottom=0)
        ax.set_xticks(range(0, 25, 2))

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_prev.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === TABELA REAL ===
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('tight')
        ax.axis('off')

        table_data_real = [['Hora'] + [str(ano) for ano in anos_disponiveis]]
        for hora in range(25):
            row = [f'{hora:02d}:00']
            for ano in anos_disponiveis:
                df_ano_hora = df_mes[(df_mes['ano'] == ano) & (df_mes['hora_int'] == hora)]
                if len(df_ano_hora) > 0:
                    row.append(f"{df_ano_hora['pct_real'].iloc[0]:.1f}%")
                else:
                    row.append('-')
            table_data_real.append(row)

        table = ax.table(cellText=table_data_real, cellLoc='center', loc='center',
                        colWidths=[0.15] + [0.85/len(anos_disponiveis)]*len(anos_disponiveis))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)

        for i in range(len(anos_disponiveis) + 1):
            cell = table[(0, i)]
            cell.set_facecolor('#2196F3')
            cell.set_text_props(weight='bold', color='white', fontsize=11)

        for i in range(1, len(table_data_real)):
            cell = table[(i, 0)]
            cell.set_facecolor('#1976D2')
            cell.set_text_props(weight='bold', color='white', fontsize=10)
            for j in range(1, len(anos_disponiveis) + 1):
                cell = table[(i, j)]
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_tabela_real.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === TABELA REFERÊNCIA ===
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('tight')
        ax.axis('off')

        table_data_ref = [['Hora'] + [str(ano) for ano in anos_disponiveis]]
        for hora in range(25):
            row = [f'{hora:02d}:00']
            for ano in anos_disponiveis:
                df_ano_hora = df_mes[(df_mes['ano'] == ano) & (df_mes['hora_int'] == hora)]
                if len(df_ano_hora) > 0:
                    row.append(f"{df_ano_hora['pct_ref'].iloc[0]:.1f}%")
                else:
                    row.append('-')
            table_data_ref.append(row)

        table = ax.table(cellText=table_data_ref, cellLoc='center', loc='center',
                        colWidths=[0.15] + [0.85/len(anos_disponiveis)]*len(anos_disponiveis))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)

        for i in range(len(anos_disponiveis) + 1):
            cell = table[(0, i)]
            cell.set_facecolor('#FF9800')
            cell.set_text_props(weight='bold', color='white', fontsize=11)

        for i in range(1, len(table_data_ref)):
            cell = table[(i, 0)]
            cell.set_facecolor('#F57C00')
            cell.set_text_props(weight='bold', color='white', fontsize=10)
            for j in range(1, len(anos_disponiveis) + 1):
                cell = table[(i, j)]
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_tabela_ref.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === TABELA PREVISÃO ===
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('tight')
        ax.axis('off')

        table_data_prev = [['Hora'] + [str(ano) for ano in anos_disponiveis]]
        for hora in range(25):
            row = [f'{hora:02d}:00']
            for ano in anos_disponiveis:
                df_ano_hora = df_mes[(df_mes['ano'] == ano) & (df_mes['hora_int'] == hora)]
                if len(df_ano_hora) > 0 and 'pct_prev' in df_ano_hora.columns:
                    row.append(f"{df_ano_hora['pct_prev'].iloc[0]:.1f}%")
                else:
                    row.append('-')
            table_data_prev.append(row)

        table = ax.table(cellText=table_data_prev, cellLoc='center', loc='center',
                        colWidths=[0.15] + [0.85/len(anos_disponiveis)]*len(anos_disponiveis))
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)

        for i in range(len(anos_disponiveis) + 1):
            cell = table[(0, i)]
            cell.set_facecolor('#4CAF50')
            cell.set_text_props(weight='bold', color='white', fontsize=11)

        for i in range(1, len(table_data_prev)):
            cell = table[(i, 0)]
            cell.set_facecolor('#388E3C')
            cell.set_text_props(weight='bold', color='white', fontsize=10)
            for j in range(1, len(anos_disponiveis) + 1):
                cell = table[(i, j)]
                cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_tabela_prev.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

        # === GRÁFICO HORÁRIO DO MÊS INTEIRO ===
        fig, ax = plt.subplots(figsize=(14, 8))

        for ano in anos_disponiveis:
            df_ano = df_mes[df_mes['ano'] == ano].sort_values('hora_int')
            if 'pct_real' in df_ano.columns:
                cor = cores_anos.get(ano, '#333333')
                # Plotar todas as variáveis juntas
                ax.plot(df_ano['hora_int'], df_ano['pct_real'],
                        label=f'{ano} - Real', color=cor, linewidth=2, alpha=0.7, linestyle='-')

        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Média Diária (100%)')

        ax.set_xlabel('Hora do Dia', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(f'{titulo_base} - Dados Horários do Mês - {MESES_NOMES[mes]} (Comparação entre Anos)',
                     fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=10, loc='best', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 24)
        ax.set_ylim(bottom=0)
        ax.set_xticks(range(0, 25, 2))

        plt.tight_layout()
        filename = f"{output_dir}/{nome_arquivo}_{mes:02d}_horario.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Salvo: {filename}")

# Processar dados NE
print("\n" + "="*80)
print("PROCESSANDO: NE COMPLETO")
print("="*80)
modulacao_ne = calcular_modulacao(df_ne, tem_previsao=True)
dir_modulacao_uniforme = 'resultados/comparacao_anos/modulacao_uniforme'
total_mod_uniforme, meses_mod_uniforme = criar_modulacao_por_ano_uniforme(
    df_ne,
    dir_modulacao_uniforme
)
criar_graficos_comparacao(modulacao_ne, 'resultados/comparacao_anos', 'ne',
                          titulo_base='NE Completo')

print("\n" + "="*80)
print("ANÁLISE CONCLUÍDA COM SUCESSO!")
print("="*80)
print("\nArquivos salvos em: resultados/comparacao_anos/")
print("  • 12 meses × 7 visualizações = 84 arquivos")
print("  • 3 gráficos de modulação (Real, Ref, Prev)")
print("  • 3 tabelas (Real, Ref, Prev)")
print("  • 1 gráfico horário do mês inteiro")
print(f"  • Modulação por ano (escala uniforme): {total_mod_uniforme} arquivos em {len(meses_mod_uniforme)} meses")
