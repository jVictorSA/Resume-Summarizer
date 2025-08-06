# Resume-Summarizer

API para análise assíncrona de currículos em PDF, JPEG, PNG e JPG utilizando LLMs
<br>
<br>
## Sumário
- [Descrição do Projeto](#descrição-do-projeto)
- [Output da Análise](#output-da-análise)
  - [Sumarização de Currículos](#sumarização-de-currículos)
  - [Análise de Currículos com base em Query](#análise-de-currículos-com-base-em-query)
- [Fluxo de processamento dos currículos](#fluxo-de-processamento-dos-currículos)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Como executar o projeto](#como-executar-o-projeto)
- [Considerações](#considerações)
- [Melhorias futuras](#melhorias-futuras)

<br>
<br>

## Descrição do Projeto
A API tem por funcionalidade principal analisar informações de currículos em PDF ou imagens (arquivos JPEG, PNG e JPG) utilizando LLMs, para gerar relatóŕios sobre os currículos, a fim de facilitar o trabalho de análise de currículos.

O usuário pode enviar vários currículos numa mesma requisição, e pode informar ou não uma "query" (que pode ser uma descrição completa de vaga, qualidade/conhecimento desejada(o) ou similares) que será utilizada para relacionar as informações extraídas nos documentos pela LLM, a fim de analisar os currículos com base no que a query pede.

Caso o usuário não insira a query, o sistema efetua apenas a sumarização dos documentos, gerando para cada currículo:
- um sumário do currículo do candidato
- os pontos fortes e fracos do currículo
- uma pontuação do currículo com base em quão bom (completos, descritivos, com experiências relevantes) ele é

<br>
Caso o usuário insira uma query, o sistema efetua o processo de sumarização citado acima, e após isto analisa os currículos com base na query. Dessa forma, o sistema gera as mesmas informações de sumário, pontos fortes e fracos do currículo, como também gera para cada currículo:

- uma análise do currículo do candidato com base na query
- uma lista de pontos do porque o currículo tem aderência com a query
- uma lista de pontos a se atentar no currículo do candidato (possíveis red flags)
- como também uma pontuação do quanto o currículo se adequa com a query, possibilitando rankear os currículos com base na aderência com a query

<br>
Quando o usuário efetua a requisição a tarefa assíncrona é iniciada o endpoint retorna um objeto contendo o id da requisição. Com este id é possível consumir o endpoint de resultados do sistema (endpoint de logs) a fim de obter o resultado de sua análise após o processamento dos documentos ter acabado.

O endpoint de Logs possui operações de CREATE, GET_BY_ID, GET_ALL (de forma paginada com skip), e SEARCH (busca logs com palavras específicas na query passada na criação do log).
> Não habilitei endpoints de UPDATE e DELETE pois o usuário não deve editar logs e tampouco deletá-los. No máximo, poderia ser feito um Soft-Delete nos logs
<br>

O banco de dados utilizado foi o MongoDB.

O processamento dos documentos é feito de forma assíncrona utilizando workers do Celery (com RabbitMQ como broker), extraindo o texto dos documentos em PDF e em imagens com estratégias específicas para cada tipo de arquivo.

## Output da Análise
A seguir, seguem os outputs (em JSON) das análises dos currículos, a depender se o parâmetro de query fora ou não passado:
<br>
<br>

### Sumarização de Currículos
```json
{
  "created_at": "Data da criação do objeto",
  "updated_at": "Data de atualização do objeto. Quando a análise terminou e o resultado foi salvo no banco de dados",
  "request_id": "Id da requisição",
  "user_id": "Id do usuário",
  "timestamp": "Data da criação do objeto",
  "query": "",
  "result": {
    "summaries": [
      {
        "summary": "Sumário do currículo",
        "strong_points": ["Lista de pontos fortes do currículo"],
        "weak_points": ["Lista de pontos fracos do currículo"],
        "score": "Pontuação da qualidade do currículo"
      }
    ]
  },
  "status": "Status da requisição. Enum com valores 'Pendente, Falhado, ou Bem sucedido"
}
```
<br>
<br>

### Análise de Currículos com base em Query
```json
{
  "created_at": "Data da criação do objeto",
  "updated_at": "Data de atualização do objeto. Quando a análise terminou e o resultado foi salvo no banco de dados",
  "request_id": "Id da requisição",
  "user_id": "Id do usuário",
  "timestamp": "Data da criação do objeto",
  "query": "Query do usuário para analisar os currículos",
  "result": {
    "cvs_analysis_process": "Processo de análise da LLM com base na query",
    "cvs_analysis": [
      {
        "cv_analysis": "Análise do currículo com base na query"
        "summary": "Sumário do currículo. Independente da query",
        "strong_points": ["Lista de pontos fortes do currículo"],
        "weak_points": ["Lista de pontos fracos do currículo"],
        "why_it_fits": ["Lista de pontos do porque o candidato se adequa para a vaga"],
        "things_to_watch_out": ["Lista de pontos a se atentar no currículo do candidato. Pode apontar red flags no currículo do candidato"],
        "ranking_score": "Pontuação da qualidade do currículo"
      }
    ]
  },
  "status": "Status da requisição. Enum com valores 'Pendente, Falhado, ou Bem sucedido"
}
```
<br>
<br>

## Fluxo de processamento dos currículos
```mermaid
sequenceDiagram
    participant User
<<<<<<< HEAD
    participant Middleware
=======
>>>>>>> 66816f61931b4ffed8f083a4084b028d404c3733
    participant API as API Endpoint
    participant RabbitMQ
    participant Worker as Celery Worker
    participant MongoDB
    participant Gemini

<<<<<<< HEAD
    User->>Middleware: POST /summarize (files, query?)
    Middleware->>Middleware: Criação de request_id usando uuid4
    Middleware->>API: Propagando request para Endpoint
=======
    User->>API: POST /summarize (files, query?)
>>>>>>> 66816f61931b4ffed8f083a4084b028d404c3733
    API->>API: Validação dos dados recebidos
    API->>API: Salva arquivos em /tmp/
    API->>RabbitMQ: Enfileira task (request_id, file_paths, query)
    API->>MongoDB: Salva log pendente no banco de dados
<<<<<<< HEAD
    API->>Middleware: Propaga retorno do endpoint para usuário
    Middleware->>User: Retorna log para usuário: { request_id, status, etc }
=======
    API->>User: Retorna log para usuário: { request_id, status, etc }
>>>>>>> 66816f61931b4ffed8f083a4084b028d404c3733

    RabbitMQ->>Worker: Processa task
    Worker->>Worker: Agrupa imagens por similaridade de nome
    Worker->>Worker: Extrai texto de PDFs (pypdf)
    Worker->>Worker: Extrai texto de imagens (pytesseract)
    
    loop Para cada currículo processado
        Worker->>Gemini: Envia texto + prompt de sumarização
        Gemini-->>Worker: Retorna sumário estruturado (Summary)
    end
    
    alt query não fornecida
        Worker->>MongoDB: Salva sumários no banco + status COMPLETED
    else query fornecida
        Worker->>Gemini: Envia query + textos + sumários estruturados 
        Gemini-->>Worker: Retorna análise estruturada
        Worker->>MongoDB: Salva análise no banco + status COMPLETED
    end

    Worker->>Worker: Deleta arquivos salvos em /tmp/
    Worker->>RabbitMQ: Confirma conclusão da task
```
<br>
<br>

## Tecnologias utilizadas
- [FastAPI](https://fastapi.tiangolo.com) - Framework web Python assíńcrono moderno, com integração nativa com Pydantic.
- [Pydantic](https://docs.pydantic.dev/latest/) - Biblioteca de validação de dados, garantindo a tipagem correta de dados. Pydantic link
- [Celery](https://docs.celeryq.dev/en/stable/) - Celery é um sistema de enfileiramento de tarefas distribuído escrito em Python. Celery link
- [RabbitMQ](https://www.rabbitmq.com) - Broker de mensagens confiável que enfileira tarefas de processamento assíncronas. RabbitMQ link
- [MongoDB](https://www.mongodb.com) - Banco de dados NoSQL flexível e escalável. MongoDB link
- [Beanie](https://beanie-odm.dev) - Um ODM (Object Document Mapper) assíncrono para o MongoDB via Motor. Beanie link
- [Google Gemini](gemini.google.com) - Modelo de IA Generativa criada pelo Google. Gemini link
- [Instructor](https://useinstructor.com) - Biblioteca que transforma saídas de LLMs em objetos estruturados validados via Pydantic. Instructor Link
- [Pypdf](https://pypdf.readthedocs.io/en/stable/) - Extrai texto de arquivos PDF de forma simples e direta. Pypdf link
- [Pytesseract](https://github.com/madmaze/pytesseract) - Biblioteca para conversão de imagens em texto via OCR. Pytesseract link
<br>
<br>

## Como executar o projeto
Para executar o projeto mais facilmente, é necessário ter o [Docker](https://docs.docker.com) instalado, após clonar este repositório, use o arquivo ```./api/.env.example``` para definir as variáveis de ambiente:
<br>
<br>

```env
GEMINI_API_KEY=<API-DO-GOOGLE-GEMINI>
LLM_MODEL=<MODELO-DO-GOOGLE-GEMINI> >#foram testados os modelos gemini-1.5-flash e gemini-2.0-flash 

RABBITMQ_DEFAULT_USER=<USUARIO-DO-RABBITMQ>
RABBITMQ_DEFAULT_PASS=<SENHA-DO-RABBITMQ>
RABBITMQ_DEFAULT_HOST=<HOST-DO-RABBITMQ>
RABBITMQ_DEFAULT_PORT=<PORT-DO-RABBITMQ>

MONGO_HOST=<HOST-DO-MONGODB>
MONGO_PORT=<PORT-DO-MONGODB>
MONGO_DB_NAME=<NOME-DO-BANCO-DO-MONGODB>
MONGO_INITDB_ROOT_USERNAME=<USUARIO-DO-MONGODB>
MONGO_INITDB_ROOT_PASSWORD=<SENHA-DO_MONGODB>
```

<br>
Após isso, execute no terminal na pasta raiz do projeto:
<br>
<br>

```bash
docker compose up --build -d
```

Então, acesse o endpoint ```localhost:8000/docs```, e interaga com a API pela interface SwaggerUI
<br>
<br>

## Considerações

### Escolha da LLM
Utilizei do Google Gemini devido seu plano gratuito oferecer modelos que provém bons resultados, como o modelo ```2.0-flash```. Mas quaisquer outros modelos poderiam ter sido usados para este projeto.

### Agrupamento de imagens de currículo
Como os currículos podem ter várias páginas, o processo de transfomação de PDF para imagem irá gerar vários arquivos diferentes para um mesmo currículo. Então é necessário fazer agrupamento de imagens de currículos.
<br>
<br>
O agrupamento de imagens se dá utilizando o nome do arquivo enviado, ex: ```CV_mauro_márcio...```. Porém esta não é uma estratégia robusta para este tipo de aplicação pois muitas pessoas salvam arquivos de currículos com nomes genéricos ou abreviações de seus nomes (que podem se repetir, ex: ```CV_josé_slva```).
<br>
<br>

Outras estratégias devem ser utilizadas, como agrupamento semântico do contéudo das imagens; ou análise da estrutura do currículo via análise da imagem. Essas estratégias valem caso a estrutura de se poder enviar imagens avulsas de currículos for mantida. Mas algo que poderia sanar facilmente este problema seria o envio de de imagens zipadas, pois assim um único arquivo (.zip) teria todas as imagens de um mesmo currículo, e seria fácil descompactar este arquiuvo zipado e realizar a extração do texto das imagens.

### MongoDB usando padrão de projeto Singleton
Optei por usar um Singleton na classe responsável por gerenciar o MongoDB na aplicação, para facilitar conexões/desconexões, manter uma mesma instância do banco rodando na aplicação e deixar o gerenciamento do MongoDB mais thread-safe na aplicação.

### Extenso uso de logs no sistema
Utilizei extensivamente a criação de logs com a biblioteca nativa do Python ```logging```. Senti a necessidade de registrar ativamente a execução do código, a fim de melhorar a observabilidade em tempo de execução. Partindo desse princípio, também utilizei o request_id das requisições no logging, a fim de facilitar a inspeção de erros que possam ocorrer no sistema. Porém, é necessário refinar o logging da aplicação, utilizando serviços de registros de logs para melhorar a observabilidade do sistema.

### Passagem de request_id durante as chamadas de função no sistema
Como explicado anteriormente, o request_id das requisições são passados para todas as funções chamadas pelos endpoints da API, para melhorar a observabilidade. Porém, passar o request_id como parâmetro de funções não é uma solução elegante, e deve ser refatorada no futuro.
<br>
<br>

## Melhorias futuras

- Suporte multi-LLM
- Refatoração do uso de request_ids nas funções da aplicação
  - Deve-se melhorar o uso de request_ids para logging dentro da aplicação.
- Melhorar a estratégia de agrupamento de imagens de currículos
- Utilizar processamento assíncrono durante extração de texto e interações com LLM dentro do worker
  - Por mais que o processamento dos documentos seja assíncrono em relação à API, todo o processo dentro da task de sumarização de currículos do Worker é feito de forma sequencial, mas não deveria, visto que todos currículos são independentes, e poderiam ser processados (tanto na extração quanto na sumarização com a LLM) em threads separadas.
  - Deve-se manter atenção às imagens de currículos, caso elas ainda sejam avulsas. Pode-se manter o processamento do agrupamento antes das extrações de textos como é hoje.
- Separação da API e do Worker estruturalmente na aplicação
  - É necessário separar o worker da pasta da API no projeto, a fim de otimizar as imagens Docker dos dois serviços da aplicação
- Adicionar testes
  - É necessário adicionar testes unitários e de integração na API, fora efetuar análises com testes mutantes periodicamente a fim de deixar a suite de teste mais robusta
  - Adicionar testes de qualidade da geração da LLM