| id    | requisitos_suplementares |
|-------|---------------------------|
| title | Requisitos Suplementares  |

# Requisitos Suplementares

## Plataforma de E-commerce com Arquitetura de Nuvem Híbrida e Logística Last-Mile Inteligente

---

## 1. Introdução

### 1.1 Propósito

Este documento apresenta os requisitos suplementares da plataforma de e-commerce, complementando o Documento de Visão do projeto.

São definidos os requisitos não funcionais relacionados a desempenho, disponibilidade, segurança, escalabilidade, armazenamento, monitoramento, manutenção e custos da solução.

### 1.2 Escopo

Os requisitos se aplicam ao portal de e-commerce desenvolvido em Django, à API transacional, ao pipeline de eventos logísticos e aos serviços utilizados na infraestrutura AWS.

Os requisitos funcionais, casos de uso e detalhamento das interfaces não fazem parte deste documento.

### 1.3 Referências

- Documento de Visão do projeto;
- AWS Well-Architected Framework;
- Lei Geral de Proteção de Dados — LGPD (Lei nº 13.709/2018);
- Plano de Ensino da disciplina.

---

## 2. Contexto e Restrições

O projeto será desenvolvido por uma equipe de **3 integrantes**, dentro do prazo acadêmico de **20 semanas**.

A aplicação principal deverá utilizar **Python e Django** e será hospedada na AWS.

A região AWS utilizada será definida pela equipe considerando disponibilidade dos serviços, latência e custo da infraestrutura.

O custo mensal da infraestrutura não deverá ultrapassar **US$ 1.500,00**.

A infraestrutura utilizará os seguintes serviços:

- VPC;
- EC2;
- RDS;
- S3;
- DynamoDB;
- API Gateway;
- Lambda;
- Secrets Manager;
- CloudWatch;
- CodePipeline;
- KMS.

Os componentes críticos deverão utilizar pelo menos duas Zonas de Disponibilidade quando o serviço utilizado oferecer esse recurso.

---

## 3. Desempenho e Capacidade

### RNF-PER-01 — Latência da ingestão logística

O endpoint responsável pela ingestão de eventos logísticos deverá apresentar latência inferior a **80 ms no percentil 95 (p95)**.

**Critério de aceitação:** pelo menos 95% das requisições realizadas durante o teste de carga deverão apresentar latência inferior a 80 ms.

### RNF-PER-02 — Tempo de resposta do portal

As principais páginas e APIs do e-commerce deverão apresentar tempo de resposta inferior a **2 segundos no p95**.

**Critério de aceitação:** pelo menos 95% das requisições realizadas durante o teste deverão apresentar tempo de resposta inferior a 2 segundos.

### RNF-PER-03 — Usuários simultâneos

A plataforma deverá suportar pelo menos **1.000 usuários simultâneos**.

**Critério de aceitação:** durante o teste com 1.000 usuários simultâneos, a taxa de erros HTTP 5xx deverá permanecer inferior a 1%.

### RNF-PER-04 — Eventos logísticos

O pipeline deverá suportar **100 eventos por segundo**, com picos de até **500 eventos por segundo**.

**Critério de aceitação:** o sistema deverá processar 100 eventos/s continuamente e suportar testes de pico de 500 eventos/s sem perda de eventos.

### RNF-PER-05 — Taxa de erros

A taxa de respostas HTTP 5xx deverá permanecer abaixo de **1%** dentro da capacidade definida para o sistema.

**Critério de aceitação:** menos de 1% das requisições realizadas durante o teste de carga poderão retornar erro HTTP 5xx.

---

## 4. Escalabilidade

### RNF-ESC-01 — Escalabilidade da aplicação

As instâncias EC2 da aplicação Django deverão utilizar Auto Scaling.

**Critério de aceitação:** deverá ser possível aumentar ou reduzir automaticamente a quantidade de instâncias de acordo com a utilização dos recursos.

### RNF-ESC-02 — Escalabilidade dos eventos logísticos

O processamento dos eventos logísticos deverá utilizar API Gateway, Lambda e DynamoDB.

**Critério de aceitação:** o aumento da quantidade de eventos não deverá exigir o provisionamento manual de novos servidores.

### RNF-ESC-03 — Separação das cargas

Os eventos de rastreamento não deverão utilizar o mesmo banco de dados responsável pelas operações transacionais do e-commerce.

**Critério de aceitação:** pedidos, clientes e catálogo deverão utilizar RDS, enquanto os eventos logísticos deverão utilizar DynamoDB.

---

## 5. Disponibilidade e Confiabilidade

### RNF-DIS-01 — Disponibilidade

A plataforma deverá possuir disponibilidade mínima de **99,95%**.

**Critério de aceitação:** a disponibilidade deverá ser monitorada por métricas registradas no CloudWatch.

### RNF-DIS-02 — Redundância

Os componentes críticos deverão ser distribuídos entre pelo menos duas Zonas de Disponibilidade quando possível.

**Critério de aceitação:** o RDS deverá utilizar Multi-AZ e as instâncias da aplicação deverão permitir distribuição entre Zonas de Disponibilidade.

### RNF-DIS-03 — Falha de instância

A falha de uma instância EC2 não deverá causar a indisponibilidade completa da aplicação.

**Critério de aceitação:** outra instância disponível deverá continuar atendendo às requisições em caso de falha de uma das instâncias.

---

## 6. Backup e Recuperação

### RNF-BCP-01 — RPO

O RPO máximo para os dados transacionais será de **15 minutos**.

**Critério de aceitação:** deverá ser possível recuperar os dados com perda máxima de 15 minutos.

### RNF-BCP-02 — RTO

O RTO deverá ser **inferior a 1 hora**.

**Critério de aceitação:** os componentes críticos deverão possuir procedimento de recuperação que permita restabelecer a operação em menos de uma hora.

### RNF-BCP-03 — Backup

O RDS deverá utilizar backups automáticos e Point-in-Time Recovery.

**Critério de aceitação:** essas configurações deverão estar habilitadas no ambiente AWS.

---

## 7. Segurança e LGPD

### RNF-SEG-01 — Criptografia em trânsito

As comunicações públicas deverão utilizar **HTTPS com TLS 1.2 ou superior**.

**Critério de aceitação:** informações sensíveis não poderão ser transmitidas por HTTP sem criptografia.

### RNF-SEG-02 — Criptografia em repouso

Os dados armazenados no RDS e DynamoDB deverão possuir criptografia em repouso.

**Critério de aceitação:** a criptografia deverá estar habilitada utilizando AWS KMS quando aplicável.

### RNF-SEG-03 — Credenciais

Senhas, tokens e chaves de API não poderão ser armazenados diretamente no código-fonte.

**Critério de aceitação:** as credenciais utilizadas pela aplicação deverão ser armazenadas no AWS Secrets Manager.

### RNF-SEG-04 — Controle de acesso

O sistema terá os seguintes perfis:

- Cliente;
- Gestor/Administrador;
- Operador Logístico.

Cada perfil deverá possuir acesso somente às funcionalidades necessárias para sua função.

**Critério de aceitação:** um usuário não poderá acessar recursos exclusivos de outro perfil sem possuir a permissão correspondente.

### RNF-SEG-05 — MFA

Contas administrativas e acessos privilegiados à AWS deverão utilizar autenticação multifator.

**Critério de aceitação:** as contas administrativas deverão possuir MFA habilitado.

### RNF-SEG-06 — Dados de cartão

Dados completos de cartões não deverão ser armazenados pela plataforma.

**Critério de aceitação:** os pagamentos deverão ser processados por um gateway externo, mantendo no sistema somente os dados necessários para identificar a transação e seu status.

### RNF-SEG-07 — LGPD

A plataforma deverá limitar a coleta e o armazenamento de dados pessoais às informações necessárias para seu funcionamento.

**Critério de aceitação:** os dados pessoais deverão possuir acesso restrito e proteção por criptografia quando armazenados ou transmitidos.

---

## 8. Dados e Retenção

### RNF-DAD-01 — Persistência

Os dados transacionais deverão ser armazenados no RDS e os eventos logísticos no DynamoDB.

**Critério de aceitação:** os dois tipos de informação deverão utilizar os respectivos bancos definidos na arquitetura.

### RNF-DAD-02 — Retenção dos eventos

Os eventos de rastreamento deverão permanecer disponíveis no DynamoDB por até **12 meses**.

**Critério de aceitação:** deverá existir uma política para remoção ou arquivamento dos eventos após esse período.

### RNF-DAD-03 — Arquivamento

Dados históricos que não necessitem de acesso frequente poderão ser armazenados no S3.

**Critério de aceitação:** a arquitetura deverá permitir a transferência de dados históricos para o S3.

---

## 9. Operação e Monitoramento

### RNF-OPS-01 — Monitoramento

Os principais componentes da aplicação deverão ser monitorados pelo CloudWatch.

**Critério de aceitação:** deverão ser registradas métricas de disponibilidade, latência, erros e utilização de recursos.

### RNF-OPS-02 — Alarmes

Deverão existir alarmes para identificar problemas na aplicação e infraestrutura.

**Critério de aceitação:** deverão ser configurados alarmes para indisponibilidade, aumento da taxa de erros, aumento da latência e falhas nas funções Lambda.

### RNF-OPS-03 — Logs

Os logs operacionais deverão ser mantidos por pelo menos **90 dias**.

**Critério de aceitação:** os grupos de logs deverão possuir retenção configurada para 90 dias ou mais.

### RNF-OPS-04 — Rastreabilidade

Os registros deverão permitir identificar quando ocorreu um evento, qual recurso foi afetado e qual foi o resultado da operação.

**Critério de aceitação:** os logs deverão permitir consultar as informações necessárias para analisar um incidente.

---

## 10. Manutenção e Implantação

### RNF-MAN-01 — Versionamento

O código-fonte deverá ser versionado utilizando Git e GitHub.

**Critério de aceitação:** o repositório deverá manter o histórico das alterações realizadas no projeto.

### RNF-MAN-02 — Infraestrutura como Código

Os principais componentes da infraestrutura deverão possuir definições automatizadas utilizando uma ferramenta de **Infrastructure as Code (IaC)**.

Poderão ser utilizadas ferramentas como Terraform ou AWS CloudFormation, de acordo com a decisão técnica da equipe.

**Critério de aceitação:** os principais recursos da infraestrutura deverão poder ser provisionados a partir de arquivos de configuração versionados no projeto.

### RNF-MAN-03 — CI/CD

O processo de implantação deverá utilizar o AWS CodePipeline integrado ao repositório do projeto.

**Critério de aceitação:** alterações aprovadas na branch principal deverão iniciar o pipeline configurado para implantação.

---

## 11. Usabilidade e Compatibilidade

### RNF-USA-01 — Navegadores

O portal deverá funcionar nas versões recentes dos principais navegadores.

**Critério de aceitação:** as funcionalidades principais deverão ser testadas no Google Chrome, Mozilla Firefox, Microsoft Edge e Safari.

### RNF-USA-02 — Responsividade

O portal deverá possuir interface adaptável para desktop e dispositivos móveis.

**Critério de aceitação:** as principais funcionalidades deverão permanecer utilizáveis em resoluções desktop e mobile.

### RNF-USA-03 — Feedback

O sistema deverá informar ao usuário o resultado das principais operações realizadas.

**Critério de aceitação:** operações relevantes deverão apresentar indicação de carregamento, sucesso ou erro quando necessário.

---

## 12. Custos

### RNF-CUS-01 — Orçamento

O custo mensal da infraestrutura AWS não deverá ultrapassar **US$ 1.500,00**.

**Critério de aceitação:** a estimativa mensal dos serviços utilizados deverá permanecer dentro do orçamento definido.

### RNF-CUS-02 — Alertas de custo

Deverão existir alertas quando os gastos atingirem **70%, 85% e 100%** do orçamento mensal.

**Critério de aceitação:** os alertas deverão estar configurados na conta AWS utilizada pelo projeto.

### RNF-CUS-03 — Auto Scaling

A capacidade das instâncias EC2 deverá ser reduzida durante períodos de baixa utilização.

**Critério de aceitação:** deverão existir políticas de Auto Scaling configuradas para aumento e redução da capacidade.

### RNF-CUS-04 — Serverless

O pipeline de eventos logísticos deverá utilizar serviços serverless para evitar servidores dedicados para essa carga.

**Critério de aceitação:** a ingestão deverá utilizar API Gateway, Lambda e DynamoDB.

---

## 13. SLA e SLO

| Indicador | Meta |
|---|---|
| Disponibilidade | ≥ 99,95% |
| Latência da ingestão logística | < 80 ms (p95) |
| Tempo de resposta do portal | < 2 s (p95) |
| Usuários simultâneos | ≥ 1.000 |
| Eventos logísticos | ≥ 100 eventos/s |
| Pico de eventos | 500 eventos/s |
| Erros HTTP 5xx | < 1% |
| RPO | ≤ 15 minutos |
| RTO | < 1 hora |
| Retenção dos eventos | 12 meses |
| Retenção dos logs | ≥ 90 dias |
| Custo mensal AWS | ≤ US$ 1.500 |

---

## 14. Riscos e Critérios de Aprovação

### 14.1 Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Aumento do custo da infraestrutura | Alto | Alertas de custo e Auto Scaling |
| Sobrecarga em períodos de pico | Alto | Auto Scaling e testes de carga |
| Alto volume de eventos logísticos | Alto | API Gateway, Lambda e DynamoDB |
| Falha de instância EC2 | Alto | Redundância entre Zonas de Disponibilidade |
| Falha no banco de dados | Alto | RDS Multi-AZ e backups |
| Vazamento de credenciais | Alto | Secrets Manager e controle de acesso |
| Problemas com dados pessoais | Alto | Criptografia e aplicação da LGPD |
| Falha de serviços externos | Médio | Tratamento de erros e monitoramento |
| Prazo de desenvolvimento | Médio | Divisão das atividades entre os 3 integrantes |

### 14.2 Critérios de Aprovação

O projeto deverá atender aos seguintes pontos para aprovação dos requisitos suplementares:

- atendimento aos limites de desempenho definidos;
- suporte à carga especificada;
- disponibilidade dos mecanismos de backup e recuperação;
- utilização de criptografia em trânsito e em repouso;
- armazenamento seguro das credenciais;
- monitoramento e alarmes configurados;
- infraestrutura dentro do orçamento definido;
- infraestrutura principal documentada e versionada;
- execução dos testes necessários para verificar os critérios de aceitação.

---

## 15. Adendo AP2 — Requisitos da solução implantada (EC2 + Docker + PostgreSQL)

Na AP2 a arquitetura-alvo foi reduzida a uma **implantação mínima e verificável**: uma instância
**Amazon EC2** executando **Docker Compose** com dois contêineres (`web`: Django REST + gunicorn;
`db`: **PostgreSQL 16** com volume nomeado `pgdata`). Os requisitos abaixo valem para essa implantação
e apontam a evidência no repositório (`src/`).

### 15.1 Decisões de implantação

| ID | Decisão | Justificativa |
| :--- | :--- | :--- |
| DEC-01 | **EC2** (Ubuntu 24.04) em vez de Elastic Beanstalk | Controle do ambiente e deploy reproduzível por `docker compose` |
| DEC-02 | **Docker Compose** com serviços `web` e `db` | Mesma definição roda no Windows (desenvolvimento) e na EC2 |
| DEC-03 | **PostgreSQL em contêiner** com volume `pgdata` | Menor custo para o escopo acadêmico; comparação com RDS em `dimensionamento_rds.md` §13 |
| DEC-04 | Banco **multimodelo** no mesmo PostgreSQL (tabelas relacionais + JSONB com índice GIN) | Evita um segundo banco (ex.: DynamoDB) mantendo ACID no pedido e flexibilidade nos atributos |
| DEC-05 | Segredos em `.env` fora do Git | `.env` no `.gitignore`/`.dockerignore`; apenas `.env.example` é versionado |

### 15.2 Requisitos não funcionais da implantação

| ID | Requisito | Meta / critério de aceite | Evidência |
| :--- | :--- | :--- | :--- |
| RNF-AP2-01 | Disponibilidade da API | `GET /health/` responde 200 com o banco acessível; `restart: unless-stopped` nos dois contêineres | `docker-compose.yml`, `loja/views.py::health`, teste `test_health` |
| RNF-AP2-02 | Persistência | Dados sobrevivem a `docker compose down`/`up` (sem `-v`) | Volume nomeado `pgdata`; roteiro no README §6 |
| RNF-AP2-03 | Isolamento do banco | Porta 5432 **não publicada**; Security Group libera apenas 22 (IP do grupo) e 8000 | `docker-compose.yml` (serviço `db` sem `ports`) |
| RNF-AP2-04 | Segredos | Nenhuma senha/`SECRET_KEY` no Git; `SECRET_KEY` obrigatória com `DEBUG=False` | `settings.py`, `.env.example` |
| RNF-AP2-05 | Integridade transacional | Checkout grava pedido, itens, entrega, evento e estoque numa transação; falha desfaz tudo (HTTP 409) | `loja/services.py`; testes `CheckoutTransacaoTests` |
| RNF-AP2-06 | Desempenho de consulta JSON | Filtro por chave JSONB usa índice GIN (contenção `@>`) | `loja/filters.py`; medição em `dimensionamento_rds.md` §13.2 |
| RNF-AP2-07 | Recuperação | Backup diário por `pg_dump` (retém 7) e restauração testada | `scripts/backup.sh`; §13.4 de `dimensionamento_rds.md` |
| RNF-AP2-08 | Reprodutibilidade do deploy | `git push` → `git pull` → `docker compose up -d --build` em um único script | `scripts/deploy.sh`; `estrategias_deploy.md` §10 |
| RNF-AP2-09 | Qualidade | Suíte automatizada com PostgreSQL real, 22 testes passando | `python manage.py test` |

### 15.3 Restrições assumidas na AP2

- Instância **única** (sem Multi-AZ): uma falha de AZ derruba a API; aceitável para a avaliação, e a evolução para ALB + RDS Multi-AZ continua descrita nos documentos de Elaboração.
- Tráfego **HTTP** na porta 8000, sem TLS (sem domínio); a evolução é um ALB/CloudFront com ACM.
- Autenticação por sessão/Basic Auth do Django; leitura pública e escrita autenticada.
