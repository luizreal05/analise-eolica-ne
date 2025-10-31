# Análise de Geração Eólica - Nordeste

[🔗 Acesse a versão publicada](https://luizreal05.github.io/analise-eolica-ne/)

Sistema de análise e visualização de dados de geração eólica no subsistema Nordeste, comparando dados reais, de referência e previsões.

## 📊 Características

- **Análise temporal detalhada**: Visualizações semi-horárias, diárias e de modulação
- **Comparação entre anos**: Gráficos lado a lado para análise de padrões anuais
- **Tratamento de outliers**: Interpolação linear para dados anômalos
- **Interface web interativa**: Navegação fácil entre diferentes visualizações
- **Tabelas de modulação**: Análise do padrão intradiário por mês

## 🎯 Fontes de Dados

O projeto compara três séries temporais:

1. **Geração Real**: Soma de `val_geracao` da `tbl_restricao_eolica` (subsistema NE)
2. **Geração Referência**: Soma de `val_geracaoreferencia` da `tbl_restricao_eolica` (subsistema NE)
3. **Previsão NE_UEE**: Campo `NE_UEE` da `tbl_renovaveis` (previsão agregada do NE)

## 📁 Estrutura do Projeto

```
.
├── config_db.example.py          # Exemplo de configuração (copiar para config_db.py)
├── comparacao_eolica_ne.py       # Script principal - análise mensal NE
├── comparacao_anos.py            # Script de comparação entre anos
├── gerar_tabelas_modulacao.py    # Geração de tabelas HTML
├── index.html                    # Página principal de visualização
├── comparacao_anos.html          # Página de comparação entre anos
├── tabelas_modulacao.html        # Tabelas de modulação por mês
├── resultados/                   # Dados e gráficos gerados
│   ├── mensal/                   # Gráficos mensais (46 meses)
│   ├── comparacao_anos/          # Comparações anuais (84 arquivos)
│   ├── barras_mensal.png
│   └── *.csv                     # Dados processados
└── docs/                         # Documentação adicional
```

## 🚀 Instalação e Configuração

### 1. Requisitos

```bash
pip install pandas pymysql matplotlib numpy
```

### 2. Configurar Banco de Dados

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp config_db.example.py config_db.py
```

Edite `config_db.py` com suas credenciais do MySQL:

```python
DB_CONFIG_MIDDLE = {
    'host': 'seu-host.rds.amazonaws.com',
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'database': 'middle',
    'port': 3306
}

DB_CONFIG_DESSEM = {
    'host': 'seu-host.rds.amazonaws.com',
    'user': 'seu_usuario',
    'password': 'sua_senha',
    'database': 'dessem',
    'port': 3306
}
```

**⚠️ Importante**: O arquivo `config_db.py` está no `.gitignore` e não será commitado.

### 3. Executar Análises

```bash
# Análise mensal detalhada do NE
python comparacao_eolica_ne.py

# Comparação entre anos (mesmo mês)
python comparacao_anos.py

# Gerar tabelas de modulação
python gerar_tabelas_modulacao.py
```

### 4. Visualizar Resultados

Abra `index.html` em um navegador ou use um servidor local:

```bash
python -m http.server 8000
# Acesse: http://localhost:8000
```

## 📈 Visualizações Disponíveis

### Página Principal (index.html)

Para cada mês (2021-10 a 2025-10):
- **📊 Semi-horário**: Comparação temporal completa (resolução 30 min)
- **📈 Diário**: Médias diárias das três séries
- **📉 Modulação**: Série temporal de modulação (% da média diária)
- **📋 Tabela**: Valores de modulação por hora

### Comparação entre Anos (comparacao_anos.html)

Para cada mês do ano (Janeiro a Dezembro):

**Gráficos da Aba Principal (anos lado a lado)**:
- Semi-horário de cada ano disponível
- Modulação de cada ano disponível

**Gráficos Comparativos**:
- 3 gráficos de modulação comparando anos (Real, Ref, Prev)
- 3 tabelas comparativas por hora

### Tabelas de Modulação (tabelas_modulacao.html)

- 3 tabelas completas (Real, Referência, Previsão)
- 46 meses × 25 horas
- Código de cores para facilitar análise

## 🔧 Tratamento de Dados

### Outliers

- **Threshold NE**: Valores < 1000 MW
- **Método**: Interpolação linear
- Os outliers são automaticamente identificados e tratados

### Modulação Diária

Calculada como percentual em relação à média diária:

```
modulação = (valor_hora / média_diária) × 100
```

Onde 100% representa a média do dia.

## 📊 Período de Análise

- **Início**: Outubro de 2021
- **Fim**: Outubro de 2025
- **Total**: 46 meses
- **Granularidade**: Semi-horária (30 minutos)

## 🎨 Código de Cores

### Séries
- 🔵 **Azul (#2196F3)**: Geração Real
- 🟠 **Laranja (#FF9800)**: Geração Referência
- 🟢 **Verde (#4CAF50)**: Previsão NE_UEE

### Anos (Comparação)
- 🔴 **2021**: #FF6B6B
- 🔵 **2022**: #4ECDC4
- 🟦 **2023**: #45B7D1
- 🟠 **2024**: #FFA07A
- 🟢 **2025**: #98D8C8

## 📝 Arquivos Gerados

### CSVs
- `cache_dados_brutos.csv`: Cache dos dados extraídos do banco
- `dados_completos.csv`: Dataset processado completo
- `dados_diarios.csv`: Médias diárias

### Gráficos
- **184 gráficos mensais** (46 meses × 4 visualizações)
- **84 gráficos de comparação anual** (12 meses × 7 visualizações)
- **1 gráfico de barras mensais**

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido para análise interna de dados de geração eólica.

## 📧 Contato

Para dúvidas ou sugestões, consulte a documentação adicional na pasta `docs/`.

---

**Desenvolvido com**: Python 3, Pandas, Matplotlib, PyMySQL
