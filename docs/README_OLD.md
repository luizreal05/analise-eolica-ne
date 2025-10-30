# Comparação Eólica Nordeste - Restrição vs Previsão

## Descrição

Este projeto compara dados de geração eólica no Nordeste de duas fontes diferentes:

1. **tbl_restricao_eolica** (banco `middle`): Dados de restrição eólica
   - Colunas: `val_geracao` e `val_geracaoreferencia`
   - Filtrado por `id_subsistema = 'NE'`
   - Agregado por semi-hora (soma de todas as usinas)

2. **tbl_renovaveis** (banco `dessem`): Dados de previsão
   - Coluna: `NE_UEE` (já agregado para o Nordeste)
   - Granularidade: semi-horária

## Estrutura de Arquivos

```
pasta_claude/
├── comparacao_eolica_ne.py   # Script principal de análise
├── index.html                 # Visualização web dos resultados
├── README.md                  # Este arquivo
└── resultados/                # Pasta gerada com os resultados
    ├── dados_completos.csv    # Dataset completo
    ├── dados_diarios.csv      # Médias diárias
    ├── semihorario/           # Gráficos semi-horários por mês
    ├── diario/                # Gráficos diários por mês
    ├── boxplot_mensal.png     # Box plot comparativo mensal
    └── serie_temporal_completa.png  # Série temporal completa
```

## Como Usar

### 1. Instalar Dependências

```bash
pip install pandas pymysql matplotlib numpy
```

### 2. Executar a Análise

```bash
cd pasta_claude
python comparacao_eolica_ne.py
```

O script irá:
- Conectar aos bancos de dados `middle` e `dessem`
- Extrair os dados necessários
- Processar e mesclar as informações
- Gerar gráficos semi-horários e diários por mês
- Criar gráficos comparativos gerais
- Salvar dados em CSV

### 3. Visualizar os Resultados

Abra o arquivo `index.html` em um navegador para visualizar:
- Série temporal completa
- Box plots mensais
- Gráficos semi-horários por mês
- Gráficos diários por mês com diferenças

Ou use um servidor HTTP local:

```bash
# Python 3
python -m http.server 8000

# Acesse: http://localhost:8000/index.html
```

## Métricas Comparadas

### Geração Real (azul)
- Soma de `val_geracao` da `tbl_restricao_eolica` para o subsistema NE
- Representa a geração real verificada

### Geração Referência (laranja)
- Soma de `val_geracaoreferencia` da `tbl_restricao_eolica` para o subsistema NE
- Valor de referência sem restrições

### Previsão NE_UEE (verde)
- Campo `NE_UEE` da `tbl_renovaveis`
- Previsão de geração eólica no Nordeste

## Visualizações Geradas

### 1. Plots Semi-horários
- Resolução: 30 minutos
- Comparação das três séries ao longo do mês
- Um gráfico por mês

### 2. Plots Diários
- Médias diárias das três séries
- Diferenças em relação à previsão
- Dois subplots: valores absolutos e diferenças

### 3. Plots Comparativos Gerais
- **Box plot mensal**: Distribuição dos valores por mês
- **Série temporal completa**: Visualização de todo o período

## Análises Possíveis

Com os dados gerados, você pode:

1. **Identificar padrões de curtailment**
   - Comparar Geração Real vs Geração Referência
   - Diferença indica restrições aplicadas

2. **Avaliar precisão da previsão**
   - Comparar Previsão NE_UEE vs Geração Real
   - Calcular métricas de erro (MAE, RMSE, etc.)

3. **Análise sazonal**
   - Observar variações mensais
   - Identificar meses com maior/menor geração

4. **Análise de diferenças**
   - Entender quando e por quanto as fontes divergem
   - Investigar causas das diferenças

## Dados de Saída

### CSV Completo (`dados_completos.csv`)
Colunas:
- `timestamp`: Data e hora
- `geracao_total`: Soma val_geracao (NE)
- `geracao_referencia_total`: Soma val_geracaoreferencia (NE)
- `NE_UEE`: Previsão eólica NE
- `ano`, `mes`, `dia`, `hora`, `minuto`: Componentes de data/hora
- `data`: Data (sem hora)
- `ano_mes`: Período ano-mês
- `diferenca_geracao`: geracao_total - NE_UEE
- `diferenca_referencia`: geracao_referencia_total - NE_UEE

### CSV Diário (`dados_diarios.csv`)
Médias diárias de todas as métricas

## Observações

- O script filtra automaticamente valores `NULL`
- As séries são mescladas com `outer join` para preservar todos os timestamps
- Gráficos são salvos em alta resolução (150 DPI)
- Cores consistentes em todos os gráficos para facilitar comparação

## Autor

Gerado via Claude Code para análise de geração eólica no Nordeste.
