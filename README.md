# Gerador de Faturas

<p align="center">
  <img src="https://i.imgur.com/1GwVnfg.png" alt="Logo" width="40%" />
</p>

Sistema automatizado para geração de faturas baseado em dados de timesheet obtidos via API GraphQL.

## Estrutura do Projeto

```
gerador-fatura/
├── gerador_fatura.py     # Arquivo principal
├── config.py             # Configurações e dados pessoais
├── cliente_api.py        # Cliente para interação com API
├── processar_dados.py    # Processamento de dados
├── gerar_PDF.py          # Geração de PDF
├── utils_data.py         # Utilitários de data
├── requirements.txt      # Dependências
├── faturas/              # PDFs organizados por ano e mês
└── README.md             # Este arquivo
```

## Instalação

### Pré-requisitos

- Python **3.10 ou superior**
- Python 3.10 venv instalado (`apt install python3.10-venv`)
- `git` instalado (`sudo apt install -y git`)

### Clone o repositório

```bash
git clone https://github.com/AlbertoLucass/gerador-fatura.git
cd gerador-fatura
```

### Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate.bat  # Windows
```

### Atualize o gerenciador de pacotes

```bash
pip install --upgrade pip
```

### Instale as dependências

```bash
pip install -r requirements.txt
```

## Configuração

### Variáveis de Ambiente

O sistema agora utiliza variáveis de ambiente para configurações sensíveis. Crie um arquivo `.env` baseado no template `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas informações:

```bash
# API Credentials
EMAIL=seu.email@exemplo.com
PASSWORD=sua_senha_aqui

# Company Information
RAZAO_SOCIAL=Sua Empresa LTDA
CNPJ=00.000.000/0001-00
ENDERECO=Seu Endereço Completo
PIX=seu-pix@email.com

# Client Information
CLIENTE_NOME=Nome do Cliente LTDA
CLIENTE_CNPJ=00.000.000/0001-00
CLIENTE_ENDERECO=Endereço do Cliente

# Invoice Configuration
NUMERO_FATURA=          # Opcional: leave empty for automatic numbering based on directory structure
TAXA_HORA=60.0
MES_COMPLETO=          # Opcional: leave empty to automatically use the previous month
TAGS_INTERESSE=development,meeting
```

**Configurações importantes:**

- `NUMERO_FATURA`: Número da fatura. **Se deixado vazio, calcula automaticamente** baseado nas pastas existentes em `faturas/{ano}/`. Por exemplo, se existem pastas `10-janeiro`, `11-fevereiro`, a próxima será `12`
- `MES_COMPLETO`: Período da fatura no formato `MM/YYYY`. **Se deixado vazio, usa automaticamente o mês anterior** — ideal para rodar todo dia 5 do mês corrente
- `TAXA_HORA`: Valor da hora trabalhada
- `TAGS_INTERESSE`: Tags de timesheet separadas por vírgula (ex: `development,meeting,tests`)

### Numeração Automática de Faturas

O sistema calcula automaticamente o número da fatura quando `NUMERO_FATURA` não está definido:

1. Verifica o diretório `faturas/{ano_atual}/`
2. Extrai o maior número das pastas existentes (ex: `11-fevereiro` → 11)
3. Incrementa esse número para a próxima fatura

**Exemplo:**

```
faturas/2026/
├── 10-janeiro/
├── 11-fevereiro/
└── (próxima fatura será número 12)
```

**Continuidade entre anos:** Se o diretório do ano atual estiver vazio (ex: janeiro de 2027), o sistema verifica o ano anterior para manter a sequência. Assim, se 2026 terminou com `21-dezembro`, a primeira fatura de 2027 será `22`.

Se precisar sobrescrever manualmente, basta definir `NUMERO_FATURA` no arquivo `.env`.

⚠️ **Importante**: O arquivo `.env` contém informações sensíveis e não deve ser commitado no git. Ele já está incluído no `.gitignore`.

## Uso

Execute o arquivo principal:

```bash
python gerador_fatura.py
# ou
python3 gerador_fatura.py
```

O sistema irá:

1. Fazer login na API
2. Buscar dados de timesheet do período configurado
3. Processar os dados
4. Gerar um PDF com a fatura

## Estrutura dos Módulos

### `gerador_fatura.py`

Arquivo principal que orquestra todo o processo.

### `config.py`

Contém todas as configurações, credenciais e dados pessoais.

### `cliente_api.py`

Responsável pela comunicação com a API GraphQL:

- Autenticação
- Consultas de dados

### `processar_dados.py`

Processa os dados brutos da API:

- Filtragem por período
- Agrupamento por tags
- Formatação de dados

### `gerar_PDF.py`

Gera o PDF da fatura:

- Formatação do documento
- Tabelas e estilos
- Cálculos de valores

### `utils_data.py`

Utilitários para manipulação de datas:

- Cálculo de períodos
- Formatação de nomes de arquivo
- Validação de datas

## Personalização

### Adicionar Novas Tags

Edite a lista `TAGS_INTERESSE` no arquivo `config.py`:

```python
TAGS_INTERESSE = ['development', 'meeting', 'tests', 'nova_tag']
```

### Modificar Layout do PDF

Edite os métodos em `gerar_PDF.py` para personalizar:

- Estilos de texto
- Cores das tabelas
- Estrutura do documento

### Alterar Formato de Datas

Modifique os métodos em `utils_data.py` para diferentes formatos.

## Tratamento de Erros

O sistema possui tratamento de erros para:

- Falhas de autenticação
- Problemas de conexão com API
- Dados inválidos
- Erros na geração de PDF

## Arquivos Gerados

Os PDFs são automaticamente salvos organizados por ano e número sequencial dentro de `faturas/`, com pastas criadas automaticamente:

```
faturas/{ANO}/{NUMERO_FATURA}-{nome_mes}/Fatura_[NUMERO]_[DATA_INICIO]_a_[DATA_FIM].pdf
```

Exemplo: `faturas/2026/12-março/Fatura_12_01-03-2026_a_31-03-2026.pdf`

**Nota:** O número da pasta corresponde ao número sequencial da fatura (definido automaticamente ou manualmente), não ao número do mês calendarário.

## Dependências

- `requests`: Para comunicação com API
- `pandas`: Para manipulação de dados
- `reportlab`: Para geração de PDF
- `python-dateutil`: Para manipulação de datas
- `python-dotenv`: Para carregamento de variáveis de ambiente

## Troubleshooting

### Erro de Autenticação

Verifique se:

- Email e senha estão corretos no `config.py`
- A API está acessível
- As credenciais têm permissões adequadas

### Nenhum Dado Encontrado

Verifique se:

- O período está correto
- Existem dados de timesheet para o período
- As tags estão configuradas corretamente

### Erro na Geração do PDF

Verifique se:

- Todas as dependências estão instaladas
- Há permissão de escrita no diretório
- Os dados processados são válidos
