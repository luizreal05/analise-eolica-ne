import argparse
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymysql

# Importar configurações de banco de dados
from config_db import DB_CONFIG_MIDDLE, DB_CONFIG_DESSEM

def extrair_restricao_eolica():
    """
    Extrai dados de restrição eólica do NE (middle.tbl_restricao_eolica)
    Agrega val_geracao e val_geracaoreferencia por semi-hora
    """
    print("Conectando ao banco middle...")
    conn = pymysql.connect(**DB_CONFIG_MIDDLE)

    query = """
    SELECT
        din_instante,
        SUM(val_geracao) as geracao_total,
        SUM(val_geracaoreferencia) as geracao_referencia_total
    FROM tbl_restricao_eolica
    WHERE id_subsistema = 'NE'
        AND din_instante IS NOT NULL
        AND val_geracao IS NOT NULL
    GROUP BY din_instante
    ORDER BY din_instante
    """

    print("Extraindo dados de restrição eólica...")
    df_restricao = pd.read_sql(query, conn)
    conn.close()

    df_restricao['din_instante'] = pd.to_datetime(df_restricao['din_instante'])
    print(f"Total de registros (restrição eólica): {len(df_restricao)}")
    print(f"Período: {df_restricao['din_instante'].min()} a {df_restricao['din_instante'].max()}")

    return df_restricao

def extrair_renovaveis():
    """
    Extrai dados de previsão eólica NE (dessem.tbl_renovaveis)
    Campo NE_UEE já contém o valor agregado do Nordeste
    """
    print("\nConectando ao banco dessem...")
    conn = pymysql.connect(**DB_CONFIG_DESSEM)

    query = """
    SELECT
        timestamp,
        NE_UEE
    FROM tbl_renovaveis
    WHERE timestamp IS NOT NULL
        AND NE_UEE IS NOT NULL
    ORDER BY timestamp
    """

    print("Extraindo dados de previsão eólica...")
    df_renovaveis = pd.read_sql(query, conn)
    conn.close()

    df_renovaveis['timestamp'] = pd.to_datetime(df_renovaveis['timestamp'])
    print(f"Total de registros (previsão): {len(df_renovaveis)}")
    print(f"Período: {df_renovaveis['timestamp'].min()} a {df_renovaveis['timestamp'].max()}")

    return df_renovaveis

def tratar_outliers_referencia(df):
    """
    Trata outliers na geração de referência (valores muito baixos)
    """
    print("\nTratando outliers na geração de referência...")

    # Definir threshold para outliers (< 1000 MW)
    threshold = 1000

    # Identificar outliers
    mask_outliers = df['geracao_referencia_total'] < threshold
    n_outliers = mask_outliers.sum()

    print(f"Outliers detectados (< {threshold} MW): {n_outliers}")

    if n_outliers > 0:
        # Criar cópia para tratamento
        df_tratado = df.copy()

        # Substituir outliers por interpolação linear
        df_tratado.loc[mask_outliers, 'geracao_referencia_total'] = np.nan
        df_tratado['geracao_referencia_total'] = df_tratado['geracao_referencia_total'].interpolate(
            method='linear',
            limit_direction='both'
        )

        # Verificar se ainda há NaN após interpolação
        if df_tratado['geracao_referencia_total'].isna().any():
            # Preencher com média móvel se interpolação falhou
            df_tratado['geracao_referencia_total'] = df_tratado['geracao_referencia_total'].fillna(
                df_tratado['geracao_referencia_total'].rolling(window=48, center=True, min_periods=1).mean()
            )

        # Estatísticas do tratamento
        valores_corrigidos = df_tratado.loc[mask_outliers, 'geracao_referencia_total']
        print(f"Valores corrigidos - Mínimo: {valores_corrigidos.min():.2f} MW")
        print(f"Valores corrigidos - Máximo: {valores_corrigidos.max():.2f} MW")
        print(f"Valores corrigidos - Média: {valores_corrigidos.mean():.2f} MW")

        return df_tratado
    else:
        print("Nenhum outlier detectado.")
        return df


def calcular_modulacao_diaria(df_mes):
    """
    Calcula a modulação diária (padrão intradiário)
    Retorna percentual em relação à média diária para cada dia
    """
    # Adicionar hora e minuto se não existir
    if 'hora' not in df_mes.columns:
        df_mes['hora'] = df_mes['timestamp'].dt.hour
    if 'minuto' not in df_mes.columns:
        df_mes['minuto'] = df_mes['timestamp'].dt.minute

    # Criar coluna de hora decimal (0.0, 0.5, 1.0, 1.5, ...)
    df_mes['hora_decimal'] = df_mes['hora'] + df_mes['minuto'] / 60.0

    # Para cada dia, calcular a média diária
    df_mes['data'] = df_mes['timestamp'].dt.date
    medias_diarias = df_mes.groupby('data').agg({
        'geracao_total': 'mean',
        'geracao_referencia_total': 'mean',
        'NE_UEE': 'mean'
    }).reset_index()
    medias_diarias.columns = ['data', 'media_dia_real', 'media_dia_ref', 'media_dia_prev']

    # Merge com dados originais
    df_mes = df_mes.merge(medias_diarias, on='data', how='left')

    # Calcular percentual em relação à média do dia
    df_mes['pct_real'] = (df_mes['geracao_total'] / df_mes['media_dia_real']) * 100
    df_mes['pct_ref'] = (df_mes['geracao_referencia_total'] / df_mes['media_dia_ref']) * 100
    df_mes['pct_prev'] = (df_mes['NE_UEE'] / df_mes['media_dia_prev']) * 100

    # Retornar dataframe completo com modulação de cada dia
    return df_mes

def criar_plots_mensais(df, output_dir):
    """
    Cria 4 visualizações por mês:
    1. Semi-horário: comparação temporal completa
    2. Diário: médias diárias
    3. Modulação diária: padrão intradiário médio
    4. Tabela: valores de modulação por hora
    """
    print("\nCriando plots mensais (4 visualizações por mês)...")

    os.makedirs(f"{output_dir}/mensal", exist_ok=True)

    # Agrupar por ano-mês - ordenar do mais novo para o mais antigo
    meses = sorted(df['ano_mes'].dropna().unique(), reverse=True)

    for ano_mes in meses:
        df_mes = df[df['ano_mes'] == ano_mes].copy()

        if len(df_mes) == 0:
            continue

        # === GRÁFICO SEMI-HORÁRIO ===
        fig, ax = plt.subplots(figsize=(14, 8))

        ax.plot(df_mes['timestamp'], df_mes['geracao_total'],
                label='Geração Real', color='#2196F3', linewidth=1.5, alpha=0.8)
        ax.plot(df_mes['timestamp'], df_mes['geracao_referencia_total'],
                label='Geração Referência', color='#FF9800', linewidth=1.5, alpha=0.8)
        ax.plot(df_mes['timestamp'], df_mes['NE_UEE'],
                label='Previsão NE_UEE', color='#4CAF50', linewidth=2, alpha=0.9)

        ax.set_xlabel('Data', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração (MW)', fontsize=12, fontweight='bold')
        ax.set_title(f'Comparação Semi-horária - {ano_mes}', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Salvar semi-horário
        filename_semi = f"{output_dir}/mensal/{ano_mes}_semihorario.png"
        plt.savefig(filename_semi, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Salvo: {filename_semi}")

        # === GRÁFICO DIÁRIO ===
        fig, ax = plt.subplots(figsize=(14, 8))

        # Calcular médias diárias
        df_diario = df_mes.groupby('data').agg({
            'geracao_total': 'mean',
            'geracao_referencia_total': 'mean',
            'NE_UEE': 'mean'
        }).reset_index()

        ax.plot(df_diario['data'], df_diario['geracao_total'],
                label='Geração Real (Média Diária)', color='#2196F3',
                linewidth=2.5, marker='o', markersize=6, alpha=0.8)
        ax.plot(df_diario['data'], df_diario['geracao_referencia_total'],
                label='Geração Referência (Média Diária)', color='#FF9800',
                linewidth=2.5, marker='s', markersize=6, alpha=0.8)
        ax.plot(df_diario['data'], df_diario['NE_UEE'],
                label='Previsão NE_UEE (Média Diária)', color='#4CAF50',
                linewidth=2.5, marker='^', markersize=6, alpha=0.9)

        ax.set_xlabel('Data', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração Média Diária (MW)', fontsize=12, fontweight='bold')
        ax.set_title(f'Comparação Diária - {ano_mes}', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Salvar diário
        filename_diario = f"{output_dir}/mensal/{ano_mes}_diario.png"
        plt.savefig(filename_diario, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Salvo: {filename_diario}")

        # === GRÁFICO DE MODULAÇÃO DIÁRIA (SÉRIE TEMPORAL) ===
        fig, ax = plt.subplots(figsize=(14, 8))

        # Calcular modulação (retorna df completo com todos os dias)
        df_modulacao = calcular_modulacao_diaria(df_mes)

        # Plotar modulação como série temporal (mesmo formato do semi-horário)
        ax.plot(df_modulacao['timestamp'], df_modulacao['pct_real'],
                label='Geração Real', color='#2196F3', linewidth=1.5, alpha=0.8)
        ax.plot(df_modulacao['timestamp'], df_modulacao['pct_ref'],
                label='Geração Referência', color='#FF9800', linewidth=1.5, alpha=0.8)
        ax.plot(df_modulacao['timestamp'], df_modulacao['pct_prev'],
                label='Previsão NE_UEE', color='#4CAF50', linewidth=2, alpha=0.9)

        # Linha de referência em 100%
        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='Média Diária (100%)')

        ax.set_xlabel('Data', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geração (% da Média Diária)', fontsize=12, fontweight='bold')
        ax.set_title(f'Modulação Diária - {ano_mes}', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)  # Começar eixo Y em zero
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Salvar modulação
        filename_modulacao = f"{output_dir}/mensal/{ano_mes}_modulacao.png"
        plt.savefig(filename_modulacao, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Salvo: {filename_modulacao}")

        # === TABELA DE MODULAÇÃO POR HORA ===
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.axis('tight')
        ax.axis('off')

        # Preparar dados da tabela - calcular média por hora completa do mês
        df_modulacao['hora_int'] = df_modulacao['hora_decimal'].round().astype(int)
        tabela_dados = df_modulacao.groupby('hora_int').agg({
            'pct_real': 'mean',
            'pct_ref': 'mean',
            'pct_prev': 'mean'
        }).reset_index()

        # Criar dados para a tabela
        table_data = []
        table_data.append(['Hora', 'Geração Real (%)', 'Geração Referência (%)', 'Previsão NE_UEE (%)'])

        for _, row in tabela_dados.iterrows():
            hora = f"{int(row['hora_int']):02d}:00"
            real = f"{row['pct_real']:.1f}%"
            ref = f"{row['pct_ref']:.1f}%"
            prev = f"{row['pct_prev']:.1f}%"
            table_data.append([hora, real, ref, prev])

        # Criar tabela
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.2, 0.27, 0.27, 0.26])

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)

        # Estilizar cabeçalho
        for i in range(4):
            cell = table[(0, i)]
            cell.set_facecolor('#2196F3')
            cell.set_text_props(weight='bold', color='white', fontsize=11)

        # Estilizar linhas alternadas
        for i in range(1, len(table_data)):
            for j in range(4):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#f0f0f0')
                else:
                    cell.set_facecolor('white')

        plt.tight_layout()

        # Salvar tabela
        filename_tabela = f"{output_dir}/mensal/{ano_mes}_tabela.png"
        plt.savefig(filename_tabela, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"  Salvo: {filename_tabela}")


def criar_plots_comparativos_gerais(df, output_dir):
    """
    Cria plots comparativos gerais
    """
    print("\nCriando plots comparativos gerais...")

    # 1. Gráfico de barras por mês com linha de previsão
    fig, ax = plt.subplots(figsize=(24, 10))

    # Calcular médias mensais
    df_mensal = df.groupby('ano_mes').agg({
        'geracao_total': 'mean',
        'geracao_referencia_total': 'mean',
        'NE_UEE': 'mean'
    }).reset_index()

    meses = df_mensal['ano_mes'].astype(str).values
    x_pos = np.arange(len(meses))

    width = 0.35

    # Barras para geração real e referência
    bars1 = ax.bar(x_pos - width/2, df_mensal['geracao_total'], width,
                   label='Geração Real (Média)', color='#2196F3', alpha=0.8)
    bars2 = ax.bar(x_pos + width/2, df_mensal['geracao_referencia_total'], width,
                   label='Geração Referência (Média)', color='#FF9800', alpha=0.8)

    # Linha para previsão
    ax2 = ax.twinx()
    line = ax2.plot(x_pos, df_mensal['NE_UEE'],
                    label='Previsão NE_UEE (Média)', color='#4CAF50',
                    linewidth=3, marker='o', markersize=8, zorder=5)

    # Configurações eixo y esquerdo (barras)
    ax.set_xlabel('Mês', fontsize=14, fontweight='bold')
    ax.set_ylabel('Geração Real e Referência (MW)', fontsize=14, fontweight='bold', color='#333')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(meses, rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='y', labelcolor='#333')

    # Configurações eixo y direito (linha)
    ax2.set_ylabel('Previsão NE_UEE (MW)', fontsize=14, fontweight='bold', color='#4CAF50')
    ax2.tick_params(axis='y', labelcolor='#4CAF50')

    # Alinhar os eixos y
    y1_min, y1_max = ax.get_ylim()
    y2_min, y2_max = ax2.get_ylim()

    # Usar os mesmos limites para ambos os eixos
    y_min = min(y1_min, y2_min)
    y_max = max(y1_max, y2_max)
    ax.set_ylim(y_min, y_max)
    ax2.set_ylim(y_min, y_max)

    # Título
    ax.set_title('Comparação Mensal - Geração Eólica NE (Médias Mensais)',
                 fontsize=18, fontweight='bold', pad=20)

    # Legenda combinada
    lines_labels = [ax.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
    lines = lines_labels[0][0] + lines_labels[1][0]
    labels = lines_labels[0][1] + lines_labels[1][1]
    ax.legend(lines, labels, fontsize=12, loc='upper left')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/barras_mensal.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo: {output_dir}/barras_mensal.png")

    # 2. Série temporal completa
    fig, ax = plt.subplots(figsize=(24, 8))

    ax.plot(df['timestamp'], df['geracao_total'],
            label='Geração Real', color='#2196F3', linewidth=1, alpha=0.6)
    ax.plot(df['timestamp'], df['geracao_referencia_total'],
            label='Geração Referência', color='#FF9800', linewidth=1, alpha=0.6)
    ax.plot(df['timestamp'], df['NE_UEE'],
            label='Previsão NE_UEE', color='#4CAF50', linewidth=1, alpha=0.6)

    ax.set_xlabel('Data', fontsize=12, fontweight='bold')
    ax.set_ylabel('Geração (MW)', fontsize=12, fontweight='bold')
    ax.set_title('Série Temporal Completa - Eólica NE', fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/serie_temporal_completa.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo: {output_dir}/serie_temporal_completa.png")

def salvar_dados_csv(df, output_dir):
    """
    Salva os dados processados em CSV
    """
    print("\nSalvando dados em CSV...")

    # CSV completo
    df.to_csv(f"{output_dir}/dados_completos.csv", index=False)
    print(f"  Salvo: {output_dir}/dados_completos.csv")

    # CSV com médias diárias
    df_diario = df.groupby('data').agg({
        'geracao_total': 'mean',
        'geracao_referencia_total': 'mean',
        'NE_UEE': 'mean',
        'diferenca_geracao': 'mean',
        'diferenca_referencia': 'mean'
    }).reset_index()

    df_diario.to_csv(f"{output_dir}/dados_diarios.csv", index=False)
    print(f"  Salvo: {output_dir}/dados_diarios.csv")

def main():
    """
    Função principal
    """
    print("="*80)
    print("ANÁLISE COMPARATIVA - EÓLICA NORDESTE")
    print("="*80)

    # Criar diretório de saída
    output_dir = "resultados"
    os.makedirs(output_dir, exist_ok=True)

    # Verificar se existe cache em CSV
    cache_file = f"{output_dir}/cache_dados_brutos.csv"

    if os.path.exists(cache_file):
        print(f"\nUsando cache: {cache_file}")
        print("(Para atualizar do banco, delete este arquivo)")
        df = pd.read_csv(cache_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['data'] = pd.to_datetime(df['data'])
        df['ano_mes'] = df['timestamp'].dt.to_period('M')
    else:
        # Extrair dados do banco
        df_restricao = extrair_restricao_eolica()
        df_renovaveis = extrair_renovaveis()

        # Processar (sem tratamento ainda)
        df_restricao = df_restricao.rename(columns={'din_instante': 'timestamp'})
        df = pd.merge(df_restricao, df_renovaveis, on='timestamp', how='outer').sort_values('timestamp')

        df['ano'] = df['timestamp'].dt.year
        df['mes'] = df['timestamp'].dt.month
        df['dia'] = df['timestamp'].dt.day
        df['hora'] = df['timestamp'].dt.hour
        df['minuto'] = df['timestamp'].dt.minute
        df['data'] = df['timestamp'].dt.date
        df['ano_mes'] = df['timestamp'].dt.to_period('M')

        # Salvar cache
        print(f"\nSalvando cache em: {cache_file}")
        df.to_csv(cache_file, index=False)

    # Aplicar tratamento de outliers
    df = tratar_outliers_referencia(df)

    # Calcular diferenças
    df['diferenca_geracao'] = df['geracao_total'] - df['NE_UEE']
    df['diferenca_referencia'] = df['geracao_referencia_total'] - df['NE_UEE']

    print(f"\nTotal de registros: {len(df)}")

    # Salvar CSVs
    salvar_dados_csv(df, output_dir)

    # Criar visualizações
    criar_plots_comparativos_gerais(df, output_dir)
    criar_plots_mensais(df, output_dir)

    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print(f"\nResultados salvos em: {output_dir}")
    print(f"  - Gráfico de barras mensal: {output_dir}/barras_mensal.png")
    print(f"  - Série temporal completa: {output_dir}/serie_temporal_completa.png")
    print(f"  - Plots mensais: {output_dir}/mensal/")
    print(f"  - Dados CSV: {output_dir}/dados_*.csv")

if __name__ == "__main__":
    main()
