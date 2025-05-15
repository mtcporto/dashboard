# Dashboard

Um painel de gerenciamento de projetos Flask que facilita a criação e administração de aplicações web usando a arquitetura MVC (Model-View-Controller).

## 📋 Descrição do Projeto

Dashboard é uma ferramenta de gerenciamento que permite criar e administrar projetos Flask de forma simples e eficiente. A aplicação oferece uma interface web intuitiva para:

- Criar novos projetos Flask com estrutura MVC pré-configurada
- Visualizar e gerenciar todos os seus projetos em um único lugar
- Explorar a estrutura de arquivos dos projetos (Modelos, Controladores e Views)
- Editar arquivos diretamente pela interface web
- Excluir projetos quando necessário

O Dashboard facilita o desenvolvimento de aplicações web Flask, automatizando a criação da estrutura básica e fornecendo um ambiente integrado para gerenciamento de projetos.

## 🛠️ Tecnologias Utilizadas

O projeto foi desenvolvido utilizando as seguintes tecnologias:

### Frontend
- **HTML** (44.3%): Estruturação das páginas e templates
- **CSS** (19.8%): Estilização da interface e componentes visuais
- **JavaScript**: Interatividade da interface de usuário

### Backend
- **Python** (35.9%): Linguagem principal para o backend
- **Flask**: Framework web para desenvolvimento da aplicação
  - Blueprint: Organização modular das rotas
  - Jinja2: Sistema de templates para renderização HTML

### Estrutura MVC
- **Models**: Representação dos dados e lógica de negócio
- **Views**: Templates HTML para apresentação
- **Controllers**: Lógica de controle e rotas da aplicação

## 🚀 Como Usar

1. Clone este repositório
2. Instale as dependências necessárias:
   ```
   pip install flask
   ```
3. Execute a aplicação:
   ```
   python app.py
   ```
4. Acesse a aplicação em seu navegador através do endereço: `http://localhost:5000`

## 📁 Estrutura do Projeto

```
dashboard/
├── app.py                    # Arquivo principal da aplicação
├── controllers/              # Controladores da aplicação
│   └── dashboard.py          # Controlador principal do dashboard
├── templates/                # Templates HTML (Views)
│   ├── base.html             # Template base
│   ├── home.html             # Página inicial
│   ├── projeto.html          # Visualização de projeto
│   └── editar_arquivo.html   # Editor de arquivo
├── static/                   # Arquivos estáticos
│   └── css/                  # Folhas de estilo
│       └── style.css         # Estilo principal
└── utils/                    # Utilitários
    └── filetools.py          # Ferramentas para manipulação de arquivos
```

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença [MIT](LICENSE).
