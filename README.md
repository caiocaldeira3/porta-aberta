# Alô quem fala?
Este é um trabalho de engenharia de software no qual nos comprometemos a desenvolver um serviço de encontro e comunicação para ser utilizado entre porteiros e vigias.  
Vigias e porteiros muitas vezes trabalham por longas horas e sozinhos, podendo passar toda madrugada em sua cabine por toda uma noite. Esperamos que, com esse projeto, possa se encontrar uma saída simples e rápida para encontrar pessoas em situações semelhantes de emprego e com interesses semelhantes para se fazerem companhia nessas horas de pouco movimento.

## Grupo:
Nome: Caio Alves Caldeira | Matrícula: 2017068734  
Nome: Luiz Henrique | Matrícula: 2018113555  
Nome: Nathan Nogueira | Matrícula: 2017086023  
Nome: Victor Vieira | Matrícula: 2018054346  

## Tema: Rede Social para Porteiros

### Requisitos Funcionais:

- Cadastro e Login de Usuários;
- Chat App para que possam trocar mensagens pelo aplicativo;
- Fóruns de discussão ou grupos onde os usuários possam encontrar usuários com mesmos interesses;
- Lista de amigos do usuário;
- Desenvolver um container para subir a aplicação.

### Requisitos Não-Funcionais:
- Responsabilidade;
- Páginas de Perfil;

### Funcionalidades Futuras Desejadas:
- Navegação no site;
- Implementação de grupos para o Chat App.
- Feed do usuário com seus posts e posts de amigos;
- Feed com scroll.

### Variáveis de Ambiente \#TODO
1. Na raiz do projeto, rode o comando e altere as variáveis de ambiente necessárias no arquivo ```.env```.
    ```bash
    cp .env.example .env
    ```
2. Vá até a pasta do frontend, rode o comando e altere as variáveis de ambiente necessárias no arquivo ```.env```.
    ```bash
    cd frontend
    cp .env.example .env
    ```

### Backlog do Sprint

#### Como desenvolvedor, gostaria de ter um ORM do banco de dados do porta aberta: [[ CAIO, VICTOR ]]
* Estudar a implementação desse banco de dados com SQLAlchemy e Redis;
* Criar modelos das tabelas: `chat`, `user`, `message` e suas relações no banco de dados do usuário;
* Criar modelos das tabelas: `user` e `pb_key` e suas relações no banco de dados do usuário;
* Traduzir banco de dados do Flask-Alchemy para SQLAlchemy.

#### Como usuário, gostaria de ter acesso a interface gráfica de: [[ NATHAN, LUIZ ]]
* Uma página inicial, contendo minha lista de amigos;
* Uma página que contenha a minha lista de conversas e que me permita me levar até uma conversa com um clique;
* Uma página de conversa, pela qual possa enviar uma mensagem para o meu remetente;
* Uma página do meu perfil de usuário.

#### Como desenvolvedor, quero implementar a criptografia das mensagens enviadas: [[ CAIO ]]
* Estudar a respeito dos protocolos de criptografia implementados pelo signal, matrix e whats app;
* Organizar a geração e armazenamento de chaves privadas e públicas;
* Utilizar assinatura de chaves ED para autenticar a sessão do usuário;
* Implementar o protocolo de criptografia Double Ratchet com um arquivo para teste local.

#### Como desenvolvedor, quero implementar a conexão entre o servidor e o usuário em tempo real: [[ CAIO, VICTOR ]]
* Estudar a respeito das ferramentas utilizadas, principalmente websockets;
* Implementar um sistema rudimentar de comunicação utilizando uma REST API, com Flask;
* Atualizar a comunicação para utilizar de WebSockets, um protocolo mais interessante para comunicação em tempo real.

#### Como desenvolvedor, gostaria que mensagens com erro sejam re-enviadas após certo tempo: [[ VICTOR ]]
* Analisar a melhor abordagem para isso, passando por ferramentas como Redis ou outros bancos de dados;
* Implementar essa fila de serviços para ser ativada quando o usuário der ping;
* Armazenar de forma segura os dados das mensagens.

#### Como usuário, gostaria de poder pesquisar por grupos de conversa com base em tags ou categorias: [[ LUIZ ]]
* Implementar as buscas nos modelos de banco de dados para isso;
* Permitir a criação de grupos de usuários a partir de criptografia todos-para-todos;
* Estudar outros protocolos possíveis, p.ex Matrix.

#### Como desenvolvedor, gostaria de ter acesso a uma ferramenta simples para a configuração do servidor: [[ CAIO, NATHAN ]]
* Estudar as ferramentas de Docker e docker-compose;
* Implementar o Dockerfile para subir o servidor dentro de um ambiente próprio;
* Estudar a possibilidade e necessidade de utilizar um docker-compose para configuração do ambiente de usuário também.

### Tecnologias:

#### Backend:
- Python (Flask)
- WebSocket
- Double Ratchet Encryption
- Docker

#### Frontend:
- ReactJS
- Typescript.
- VueJS

#### Banco de Dados:
- Relacional SQLite ou MongoDB*
- Redis* 

#### Organização:
- Trello
