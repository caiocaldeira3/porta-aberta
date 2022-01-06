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

### Rodando o backend
Para rodar o servidor primeiro é necessário instalar todos os requisitos executando o seguinte comando pip `pip install -r requirements.txt` na pasta raiz deste repositório. Depois disso, e assumindo que está sendo utilizada uma versão do python adequada, 3.9.7+, deve-se caminhar até a pasta <i>server</i> e executar o script run.py a partir do comando `python run.py`. Após isso o servidor deve estar rodando localmente.

Como o melhor jeito que encontrei para armazenar as chaves utilizadas no processo de encriptação foi salvá-las localmente na pasta do repositório, este repositório é o equivalente a um usuário. Caso seja do interesse do testador simular vários usuários conversando, por agora, é aconselhado clonar este repositório quantas vezes tiverem usuários. Isso também significa que pode ser necessário garantir que a seguinte pasta esteja presente no repositório, criando-a, se necessário:

├── zap2-userside  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── scripts  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── user  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── util  
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <b>encrypted_keys*</b>  

Para criar uma sessão, simplesmente rode `python run.py` na pasta <i>user</i>, dentro do repositório, e experimente com os comandos disponíveis:
  * login
  * logout
  * signup
  * create-chat
  * send-message
  * info  

Enquanto todos os dispositivos comuniquem com o mesmo servidor, deve ser possível enviar mensagens entre os repositórios.

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

#### História 1: Desenhar e desenvolver o ORM do banco de dados do porta aberta: [[ CAIO, VICTOR ]]
* Estudar a implementação desse banco de dados com SQLAlchemy e Redis;
* Criar modelos das tabelas: `chat`, `user`, `message` e suas relações no banco de dados do usuário;
* Criar modelos das tabelas: `user` e `pb_key` e suas relações no banco de dados do usuário;
* Traduzir banco de dados do Flask-Alchemy para SQLAlchemy.

#### História 2: Desenvolver o acesso à interface gráfica de: [[ NATHAN, LUIZ ]]
* Uma página inicial, contendo minha lista de amigos;
* Uma página que contenha a minha lista de conversas e que me permita me levar até uma conversa com um clique;
* Uma página de conversa, pela qual possa enviar uma mensagem para o meu remetente;
* Uma página do meu perfil de usuário.

#### História 3: Implementar a criptografia das mensagens enviadas: [[ CAIO ]]
* Estudar a respeito dos protocolos de criptografia implementados pelo signal, matrix e whats app;
* Organizar a geração e armazenamento de chaves privadas e públicas;
* Utilizar assinatura de chaves ED para autenticar a sessão do usuário;
* Implementar o protocolo de criptografia Double Ratchet com um arquivo para teste local.

#### História 4: Implementar a conexão entre o servidor e o usuário em tempo real: [[ CAIO, VICTOR ]]
* Estudar a respeito das ferramentas utilizadas, principalmente websockets;
* Implementar um sistema rudimentar de comunicação utilizando uma REST API, com Flask;
* Atualizar a comunicação para utilizar de WebSockets, um protocolo mais interessante para comunicação em tempo real.

#### História 5: Tratar mensagens com erro para que sejam re-enviadas após certo tempo: [[ VICTOR ]]
* Analisar a melhor abordagem para isso, passando por ferramentas como Redis ou outros bancos de dados;
* Implementar essa fila de serviços para ser ativada quando o usuário der ping;
* Armazenar de forma segura os dados das mensagens.

#### História 6: Implementar a pesquisa por grupos de conversa com base em tags ou categorias: [[ LUIZ ]]
* Implementar as buscas nos modelos de banco de dados para isso;
* Permitir a criação de grupos de usuários a partir de criptografia todos-para-todos;
* Estudar outros protocolos possíveis, p.ex Matrix.

#### História 7: Atualizar o acesso com uma ferramenta simples para a configuração do servidor: [[ CAIO, NATHAN ]]
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
