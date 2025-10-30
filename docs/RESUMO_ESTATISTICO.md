# Resumo Estatístico - Análise Eólica Nordeste

## Período Analisado
**2021-10-01 00:00:00 a 2025-10-30 23:30:00**

Total de registros: **67.152**

---

## Estatísticas de Geração (MW)

### Geração Real (tbl_restricao_eolica)
| Métrica | Valor |
|---------|-------|
| Média | 9.827,96 MW |
| Mediana | 9.588,67 MW |
| Máximo | 22.095,42 MW |
| Mínimo | 135,94 MW |

### Geração Referência (tbl_restricao_eolica)
| Métrica | Valor |
|---------|-------|
| Média | 9.175,67 MW |
| Mediana | 8.098,66 MW |
| Máximo | 27.214,26 MW |
| Mínimo | 1,16 MW |

### Previsão NE_UEE (tbl_renovaveis)
| Métrica | Valor |
|---------|-------|
| Média | 11.627,13 MW |
| Mediana | 11.635,95 MW |
| Máximo | 23.536,00 MW |
| Mínimo | 887,00 MW |

---

## Diferenças Médias em Relação à Previsão

### Geração Real - Previsão
- **Diferença média**: -899,23 MW (**-7,8%**)
- **Desvio padrão**: 1.993,16 MW
- **Interpretação**: A geração real é, em média, 7,8% menor que a previsão NE_UEE

### Geração Referência - Previsão
- **Diferença média**: -782,36 MW (**-6,8%**)
- **Desvio padrão**: 2.462,07 MW
- **Interpretação**: A geração de referência é, em média, 6,8% menor que a previsão NE_UEE

---

## Curtailment Estimado

### Diferença: Geração Referência - Geração Real
- **Diferença média**: 116,87 MW
- **Percentual médio**: **1,1%**
- **Curtailment máximo observado**: 24.438,61 MW

### Interpretação
A diferença entre a Geração Referência e a Geração Real pode indicar restrições aplicadas ao sistema. Em média, observa-se um curtailment de aproximadamente 1,1% da capacidade de referência.

---

## Insights Principais

1. **Previsão vs Realizado**: A previsão NE_UEE tende a ser superior à geração real em média 7,8%, sugerindo:
   - Possível superestimação da previsão
   - Restrições operacionais não previstas
   - Diferenças metodológicas entre as fontes

2. **Curtailment**: O curtailment médio de 1,1% é relativamente baixo, mas há eventos extremos com até 24.438 MW de restrição.

3. **Variabilidade**: O alto desvio padrão das diferenças (~2.000 MW) indica:
   - Grande variabilidade nas condições operacionais
   - Necessidade de análise por período/contexto
   - Possíveis eventos sazonais ou operacionais específicos

4. **Capacidade Instalada**: O máximo observado de 27.214 MW na geração de referência indica a capacidade teórica do sistema eólico NE no período.

---

## Próximos Passos Sugeridos

1. **Análise Temporal**: Investigar padrões sazonais e tendências ao longo do tempo
2. **Análise de Eventos**: Identificar períodos com curtailment extremo
3. **Correlação com Fatores Externos**: Cruzar com dados de vento, demanda, preço
4. **Métricas de Precisão**: Calcular MAE, RMSE, MAPE para avaliar a previsão
5. **Análise Horária**: Verificar se há padrões intradiários específicos

---

## Fontes de Dados

- **tbl_restricao_eolica** (banco middle): Dados de restrição operacional
- **tbl_renovaveis** (banco dessem): Previsões de geração renovável

Gerado em: 2025-10-30
