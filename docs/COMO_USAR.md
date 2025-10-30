# Como Usar a Análise de Eólica NE

## Acesso Rápido

### Visualização Web
1. Abra o arquivo [index.html](index.html) em seu navegador
2. Navegue pelos gráficos interativos
3. Clique nas imagens para ampliar (lightbox)

### Dados CSV
- **[dados_completos.csv](resultados/dados_completos.csv)**: Todos os dados semi-horários (67.152 registros)
- **[dados_diarios.csv](resultados/dados_diarios.csv)**: Médias diárias agregadas

---

## Estrutura do Projeto

```
pasta_claude/
├── comparacao_eolica_ne.py      # Script Python para análise
├── index.html                    # Visualização web interativa
├── README.md                     # Documentação técnica completa
├── RESUMO_ESTATISTICO.md         # Estatísticas e insights
├── COMO_USAR.md                  # Este arquivo
└── resultados/                   # Todos os resultados gerados
    ├── boxplot_mensal.png        # Distribuição mensal
    ├── serie_temporal_completa.png
    ├── dados_completos.csv
    ├── dados_diarios.csv
    ├── semihorario/              # 46 gráficos semi-horários
    │   ├── 2021-10_semihorario.png
    │   ├── 2022-01_semihorario.png
    │   └── ...
    └── diario/                   # 46 gráficos diários
        ├── 2021-10_diario.png
        ├── 2022-01_diario.png
        └── ...
```

**Total**: 94 gráficos PNG gerados (~41 MB)

---

## Principais Visualizações

### 1. Série Temporal Completa
Mostra toda a série histórica (2021-2025) com as três métricas:
- Geração Real (azul)
- Geração Referência (laranja)
- Previsão NE_UEE (verde)

📊 [Ver gráfico](resultados/serie_temporal_completa.png)

### 2. Box Plot Mensal
Distribuição estatística por mês para comparação:
- Mediana, quartis, valores extremos
- Fácil identificação de outliers
- Comparação visual entre as fontes

📊 [Ver gráfico](resultados/boxplot_mensal.png)

### 3. Análise Diária por Mês
Para cada mês, dois gráficos:
- **Superior**: Médias diárias das três séries
- **Inferior**: Diferenças em relação à previsão

📁 [Ver pasta diario/](resultados/diario/)

### 4. Análise Semi-horária por Mês
Comparação detalhada em resolução de 30 minutos:
- Padrões intradiários
- Variações horárias
- Eventos específicos

📁 [Ver pasta semihorario/](resultados/semihorario/)

---

## Insights Principais

### Diferença Média: Previsão vs Realizado
A **previsão NE_UEE é 7,8% maior** que a geração real, em média:
- Média da previsão: **11.627 MW**
- Média da geração real: **9.828 MW**
- Diferença: **-899 MW (-7,8%)**

### Curtailment Observado
Diferença entre Geração Referência e Geração Real:
- Média: **117 MW (1,1%)**
- Máximo: **24.439 MW**

### Variabilidade
- Alto desvio padrão (~2.000 MW) indica grande variabilidade
- Necessário análise contextual por período

📄 [Ver detalhes no resumo estatístico](RESUMO_ESTATISTICO.md)

---

## Como Reprocessar os Dados

Se quiser atualizar os dados ou modificar a análise:

```bash
# 1. Edite o script se necessário
nano comparacao_eolica_ne.py

# 2. Execute novamente
python comparacao_eolica_ne.py

# 3. Atualize o navegador para ver novos resultados
```

---

## Análises Sugeridas

### Com os CSVs fornecidos, você pode:

1. **Calcular métricas de erro**
   ```python
   import pandas as pd
   df = pd.read_csv('resultados/dados_completos.csv')
   mae = abs(df['geracao_total'] - df['NE_UEE']).mean()
   ```

2. **Análise sazonal**
   - Comparar meses de safra vs entressafra de vento
   - Identificar padrões anuais

3. **Análise horária**
   - Extrair padrões por hora do dia
   - Verificar comportamento ao meio-dia (máximo solar)

4. **Correlação com fatores externos**
   - Cruzar com dados de vento
   - Relacionar com preços (PLD)
   - Analisar junto com demanda do sistema

5. **Detecção de anomalias**
   - Identificar períodos atípicos
   - Investigar eventos extremos de curtailment

---

## Suporte e Documentação

- **Documentação técnica completa**: [README.md](README.md)
- **Estatísticas detalhadas**: [RESUMO_ESTATISTICO.md](RESUMO_ESTATISTICO.md)
- **Código fonte comentado**: [comparacao_eolica_ne.py](comparacao_eolica_ne.py)

---

## Requisitos

### Para visualizar
- Navegador web moderno (Chrome, Firefox, Edge)

### Para reprocessar
- Python 3.7+
- Bibliotecas: pandas, pymysql, matplotlib, numpy
- Acesso aos bancos de dados `middle` e `dessem`

---

**Última atualização**: 2025-10-30
**Período de dados**: 2021-10-01 a 2025-10-30
**Total de registros**: 67.152
