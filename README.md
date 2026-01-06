
# 🎮 Gameslog - Biblioteca Unificada de Jogos

Gameslog é um aplicativo desktop minimalista, inspirado na Steam, para organizar, personalizar e acompanhar sua coleção de jogos de PC ou console. Todos os seus jogos, conquistas e prints em um só lugar, com visual dark, perfil personalizável e backup automático!

## ✨ Principais Recursos

- **Interface moderna e minimalista** (Dark, menu top estilo Steam, design responsivo)
- **Biblioteca de jogos**: Adicione, edite, remova e pesquise jogos facilmente
- **Modal de adição**: Adicione jogos via modal bonito com inputs organizados
- **Capa automática**: Busca automática de capa pela internet (RAWG) ou faça upload
- **Favoritos**: Marque/desmarque favoritos e veja na aba especial
- **Status e notas**: Defina status, nota pessoal, anotações e detalhes para cada jogo
- **Busca inteligente**: Filtro instantâneo por nome, plataforma, gênero, status, etc
- **Feed de prints**: Poste prints/screenshots dos seus jogos (tipo rede social)
- **Perfil personalizável**: Avatar, nickname, papel de parede/wallpaper só no perfil
- **Posts do usuário**: Adicione prints com comentários, tipo feed social no perfil
- **Conquistas e jogos zerados**: Veja contagem de conquistas e jogos finalizados
- **Backup automático incremental**: Salva backup da biblioteca a cada mudança em `/backups`
- **Exportação fácil**: Exporte a biblioteca inteira para Excel com um clique
- **Temas personalizáveis**: Escolha entre temas Dark, Light, Neon ou crie seu próprio
- **Wallpaper do perfil**: Escolha e remova papel de parede só do perfil, sem afetar o resto
- **Arraste & solte**: Suporte a Drag&Drop de capas diretamente nos jogos
- **Modais bonitos**: Diálogos elegantes para adicionar, editar e visualizar detalhes dos jogos
- **Backup incremental**: Todo backup é salvo com data/hora única, nada se perde!
- **Prints de jogos**: Salve suas screenshots dentro do app para sempre lembrar dos momentos!
- **Nenhum dado na nuvem**: Todos os dados são salvos localmente, privacidade total

## 🚀 Instalação e Execução

> **Requisitos**  
> - Python 3.8 ou superior  
> - [Pip](https://pip.pypa.io/en/stable/)  
> - (Opcional) [Virtualenv](https://virtualenv.pypa.io/en/latest/)

### 1. Clone o repositório

```bash
git clone https://github.com/maidenzinho/GamesLog.git
cd gameslog
```

### 2. Instale as dependências

Ambiente virtual recomendado:

```bash
python -m venv venv
```

Ou Dependências:

```bash
pip install PyQt5 pandas matplotlib pillow requests
```

### 3. Configure sua chave da API RAWG (opcional, para busca automática de jogos)

- Crie uma conta grátis e obtenha sua chave em: https://rawg.io/apidocs
- Abra o arquivo `main.py` e troque:
  ```python
  RAWG_KEY = "SUA_CHAVE_AQUI"
  ```
  ![image](https://github.com/user-attachments/assets/9d5e5a2d-b43e-4892-b2d9-0376f28dc385)

  Coloque sua chave ali (sem ela, só upload manual de capas).

### 4. Execute o programa

```bash
python main.py
```

---

## 🗃️ Estrutura de Pastas

```
main.py                 # Código principal
biblioteca.json         # Biblioteca dos jogos
perfil.json             # Dados do perfil do usuário
prints/                 # Pasta dos prints do perfil (criada automaticamente)
backups/                # Backups automáticos incrementais
README.md               # Este arquivo
```

---

## 🖼️ Prints do App

![Biblioteca](https://github.com/user-attachments/assets/966f9ff2-a1cb-4ae4-ac42-e10b28ccd745)

![Perfil](https://github.com/user-attachments/assets/5e3a95dd-8038-411f-80e2-f93ebfef963b)


---

## 🛠️ Personalização

- Adicione temas novos em `main.py` (variável `THEMES`)
- Wallpapers do perfil podem ser qualquer imagem .jpg ou .png
- Prints ficam salvos em `/prints`, vinculados ao perfil
- Os backups incrementais da biblioteca vão para `/backups` automaticamente
- Exporte para Excel em dois cliques pela aba "Exportar"

---

## 📋 Recursos Avançados

- **Perfil editável**: Altere nome, avatar, wallpaper, faça anotações
- **Remover papel de parede**: Botão para remover wallpaper e voltar ao padrão
- **Posts com prints**: Feed com imagens e comentários do usuário
- **Jogos finalizados**: Lista de jogos zerados exibida no perfil
- **Conquistas**: Contador automático (integração futura com Steam)
- **Backup incremental**: Toda modificação gera um backup seguro em `/backups`
- **Nenhuma dependência online obrigatória**: Tudo salvo local, sem login ou upload em nuvem
- ** Importe seu arquivos**: txt, xlsx, xls, json e csv

# 📥 Importação de Jogos — Guia de Preenchimento (TXT e Excel)

Este guia explica **como preencher corretamente arquivos Excel (.xlsx/.xls) e TXT**
para importar jogos automaticamente para a biblioteca do sistema.

---

## ✅ Formatos Aceitos
- **Excel:** `.xlsx`, `.xls`
- **Texto:** `.txt`
- **CSV:** `.csv`
- **JSON:** `.json` ou `.txt` contendo JSON

---

## 📌 Campos Reconhecidos

### Obrigatórios
- **Nome** → Nome do jogo

### Opcionais (recomendados)
- Plataforma  
- Data de compra  
- Preço pago  
- Nº comprovante  
- Nota pessoal  
- Status  
- Anotações  
- Imagem  
- Gênero  
- Desenvolvedor  
- Data lançamento  
- Link  
- Favorito  

> ⚠️ Os nomes das colunas **não diferenciam maiúsculas/minúsculas**.

---

## 📊 Exemplo — Excel (.xlsx)

| Nome              | Plataforma | Data de compra | Preço pago | Nº comprovante | Nota pessoal | Status     | Anotações            |
|-------------------|------------|---------------|------------|----------------|--------------|------------|----------------------|
| Cyberpunk 2077    | Steam      | 2023-11-25    | 149.90     | STEAM123       | 9            | Finalizado | História excelente   |
| GTA V             | Epic Games | 2022-06-10    | 0          | EPICFREE       | 8            | Jogando    | Modo online          |

📌 **Data aceita:** `YYYY-MM-DD`

---

## 📄 Exemplo — TXT Delimitado (; , | TAB)

```
Nome;Plataforma;Data de compra;Preço pago;Nº comprovante;Nota pessoal;Status;Anotações
Cyberpunk 2077;Steam;2023-11-25;149.90;STEAM123;9;Finalizado;História excelente
GTA V;Epic Games;2022-06-10;0;EPICFREE;8;Jogando;Modo online
```

Delimitadores aceitos:
- `;` (recomendado)
- `,`
- `|`
- TAB

---

## 🧾 Exemplo — TXT ou JSON

```
[
  {
    "Nome": "Cyberpunk 2077",
    "Plataforma": "Steam",
    "Data de compra": "2023-11-25",
    "Preço pago": 149.90,
    "Nota pessoal": 9,
    "Status": "Finalizado"
  },
  {
    "Nome": "GTA V",
    "Plataforma": "Epic Games",
    "Status": "Jogando"
  }
]
```

---

## 🎮 Status Aceitos
- Não jogado
- Jogando
- Finalizado
- Dropado
- Platinado

(O sistema corrige automaticamente variações como: *finalizei*, *zerado*, *playing* etc.)

---

## ❌ Erros Comuns
- Arquivo sem a coluna **Nome**
- Datas fora do padrão
- Texto salvo como `.txt` com encoding estranho (use UTF-8)
- Linhas vazias no meio do arquivo

---

## ✨ Dicas
✔ Use Excel para grandes bibliotecas  
✔ Use TXT para edição rápida  
✔ Evite duplicar jogos (o sistema ignora repetidos)  
✔ Quanto mais campos preencher, mais organizada fica a biblioteca  

---

## 🚀 Importação
No sistema:
**Exportar → Importar Excel/TXT/CSV/JSON**

Pronto! 🎉


---

## 🤝 Colabore!

Sugestões, issues e PRs são bem-vindos!

---

## 📜 Licença

MIT

---

**Desenvolvido com 💜 por [Maiden](https://github.com/maidenzinho)**
