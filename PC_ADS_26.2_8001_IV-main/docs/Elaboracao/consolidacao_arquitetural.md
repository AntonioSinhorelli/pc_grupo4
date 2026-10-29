# Modelo de Design (Consolidação Arquitetural)

## Diagramas de Sequência e de Comunicação dos Fluxos Críticos

## Plataforma de E-commerce com Arquitetura de Nuvem Híbrida e Logística Last-Mile Inteligente

---

| **Informação do Documento** | |
| :--- | :--- |
| **Projeto** | Plataforma de E-commerce com Logística Last-Mile Inteligente |
| **Documento** | Modelo de Design (Sequência/Comunicação) - Consolidação Arquitetural |
| **Versão** | 1.0 |
| **Data** | 29/10/2026 |
| **Status** | Em Revisão |
| **Responsável** | Grupo E-commerce |
| **Disciplina** | Projeto de Cloud - Semana 7 |
| **Fase RUP/UP** | Elaboração (Elaboration) |

---

## 1. Introdução

### 1.1. Propósito

Este documento consolida a arquitetura da plataforma de e-commerce na AWS, mostrando **como os componentes definidos nos artefatos anteriores interagem** nos fluxos críticos do sistema. Cada fluxo é descrito por um diagrama de sequência (ordem temporal das mensagens) e um diagrama de comunicação (quem conversa com quem), acompanhados da tabela de mensagens e dos riscos.

O documento é derivado dos seguintes artefatos:

- **Documento de Visão** (Semana 1) - Funcionalidades principais e arquitetura AWS
- **Documento de Requisitos Suplementares** (Semana 2) - Metas de desempenho, disponibilidade, segurança e custo
- **Modelo de Casos de Uso Arquiteturais** (Semana 3) - UC-ARQ-001 a UC-ARQ-007
- **Modelo de Análise (Pacotes/Subsistemas)** (Semana 4) - Pacotes de segurança
- **Modelo de Análise (Classes) - RDS** (Semana 5) e **- EC2** (Semana 6) - Classes e premissas de carga

### 1.2. Escopo

Fluxos cobertos:

1. Checkout (criação do pedido e pagamento)
2. Ingestão de evento logístico (serverless)
3. Consulta de rastreamento do pedido
4. Autenticação e autorização por perfil (com MFA para o gestor)
5. Envio do comprovante de entrega (S3)
6. Failover do RDS (Multi-AZ)
7. Deploy automatizado (CI/CD Blue/Green)

**Fora do escopo:** análises de Big Data (EMR, Redshift), o detalhamento interno do gateway de pagamento (serviço de terceiros, conforme o Documento de Visão) e a interface gráfica.

### 1.3. Definições e Siglas

| **Sigla** | **Definição** |
| :--- | :--- |
| **ALB** | Application Load Balancer |
| **EC2** | Elastic Compute Cloud |
| **RDS** | Relational Database Service |
| **S3** | Simple Storage Service |
| **SNS** | Simple Notification Service (envio de alertas) |
| **KMS** | Key Management Service |
| **NAT** | Network Address Translation (saída das sub-redes privadas para a internet) |
| **CI/CD** | Continuous Integration / Continuous Delivery (integração e entrega contínuas) |
| **MFA** | Multi-Factor Authentication (autenticação multifator) |
| **TOTP** | Time-based One-Time Password (código de 6 dígitos do app autenticador) |
| **RBAC** | Role-Based Access Control (controle de acesso por perfil) |
| **ORM** | Object-Relational Mapping |
| **TTL** | Time To Live (expiração automática de itens no DynamoDB) |
| **p95** | Percentil 95 |
| **RPO / RTO** | Recovery Point Objective / Recovery Time Objective |
| **SLA** | Service Level Agreement |
| **LGPD** | Lei Geral de Proteção de Dados |
| **PCI-DSS** | Payment Card Industry Data Security Standard |

### 1.4. Referências

- Documento de Visão - E-commerce (v1.0)
- Documento de Requisitos Suplementares - E-commerce (v1.0)
- Modelo de Casos de Uso Arquiteturais - E-commerce (v1.0)
- Modelo de Análise (Pacotes/Subsistemas) - E-commerce (v1.0)
- Modelo de Análise (Classes) - RDS - E-commerce (v1.0)
- Modelo de Análise (Classes) - EC2 - E-commerce (v1.0)
- FOWLER, M. *UML Essencial* (UML Distilled)
- AWS Well-Architected Framework - Operational Excellence e Reliability Pillars

---

## 2. Visão Geral dos Fluxos Críticos

### 2.1. Mapa de Fluxos

| **Fluxo** | **Descrição** | **Ator** | **Componentes Principais** | **Prioridade** | **Requisitos** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fluxo 1** | Checkout (pedido + pagamento) | Cliente | ALB, EC2, RDS, Secrets Manager, NAT, gateway de pagamento | Crítica | < 2 s p95, 1.000 usuários, sem dados de cartão |
| **Fluxo 2** | Ingestão de evento logístico | App do entregador | API Gateway, Lambda, DynamoDB, SNS | Crítica | 100 ev/s (pico 500), < 80 ms p95 |
| **Fluxo 3** | Consulta de rastreamento | Cliente / Gestor | ALB, EC2, RDS, DynamoDB | Alta | < 2 s p95, separação de cargas |
| **Fluxo 4** | Autenticação e autorização | Cliente / Gestor | ALB, EC2 (Django auth), RDS | Alta | 3 perfis, MFA para o gestor |
| **Fluxo 5** | Envio do comprovante de entrega | App do entregador | API Gateway, Lambda, S3, KMS | Média | Criptografia, acesso restrito (LGPD) |
| **Fluxo 6** | Failover do RDS | Sistema AWS | RDS Primary/Standby, CloudWatch, SNS | Alta | RPO 15 min, RTO < 1 h |
| **Fluxo 7** | Deploy automatizado | Engenheiro de DevOps | GitHub, CodePipeline, CodeBuild, CodeDeploy, ALB | Média | Deploy < 10 min, rollback < 5 min |

### 2.2. Diagrama de Contexto Geral

```plantuml
@startuml
title Diagrama de Contexto Geral - E-commerce na AWS

skinparam componentBackgroundColor #E3F2FD
skinparam actorBackgroundColor #FFF3E0

actor "Cliente" as Cliente
actor "Gestor /\nAdministrador" as Gestor
actor "Entregador\n(Operador Logístico)" as Entregador
actor "Engenheiro\nde DevOps" as DevOps
cloud "Gateway de\nPagamento (externo)" as PSP
cloud "GitHub" as GH

rectangle "AWS us-east-1 - VPC 10.0.0.0/16" {
  component "ALB" as ALB
  component "EC2 Django\n(Auto Scaling)" as EC2
  database "RDS PostgreSQL\nMulti-AZ" as RDS
  component "NAT Gateway" as NAT
  component "API Gateway" as APIGW
  component "Lambda\n(ingestão / comprovante)" as Lambda
  database "DynamoDB\n(eventos logísticos)" as DDB
  component "S3\n(imagens / comprovantes)" as S3
  component "Secrets Manager" as SM
  component "KMS" as KMS
  component "CloudWatch" as CW
  component "SNS" as SNS
  component "CodePipeline\nCodeBuild\nCodeDeploy" as CP
}

Cliente --> ALB : HTTPS
Gestor --> ALB : HTTPS + MFA
Entregador --> APIGW : HTTPS + API key
DevOps --> GH : git push
GH --> CP : webhook

ALB --> EC2
EC2 --> RDS : 5432/TLS
EC2 --> DDB : consulta rastreamento
EC2 --> S3 : URLs pré-assinadas
EC2 --> SM : credenciais
EC2 --> NAT
NAT --> PSP : HTTPS
APIGW --> Lambda
Lambda --> DDB : PutItem
Lambda --> S3 : URL de upload
Lambda --> SNS : alertas de exceção
CP --> EC2 : Blue/Green
RDS ..> KMS
DDB ..> KMS
S3 ..> KMS
EC2 ..> CW
Lambda ..> CW
RDS ..> CW
CW --> SNS : alarmes
@enduml
```

---

## 3. Especificação dos Fluxos

---

### 3.1. FLUXO 1: CHECKOUT (PEDIDO + PAGAMENTO)

#### 3.1.1. Descrição

O cliente confirma o carrinho. O Django, em uma **transação no RDS**, reserva o estoque e cria o pedido com status `AGUARDANDO_PAGAMENTO`. Em seguida, chama o **gateway de pagamento externo** (saída pela NAT Gateway) com o *token* do cartão gerado no navegador pelo próprio gateway. Assim, os dados completos do cartão **nunca passam pela plataforma** (RNF-SEG-06). Com a resposta, o pedido é atualizado para `PAGO` ou `PAGAMENTO_RECUSADO` e o estoque é liberado em caso de recusa.

#### 3.1.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Tempo de resposta | < 2 s (p95) | RNF-PER-02 |
| Usuários simultâneos | ≥ 1.000 | RNF-PER-03 |
| Dados de cartão | Não armazenados (token do gateway) | RNF-SEG-06 |
| Credenciais do gateway | Secrets Manager | RNF-SEG-03 |
| Criptografia em trânsito | TLS 1.2+ | RNF-SEG-01 |
| Persistência | RDS | RNF-DAD-01 |

#### 3.1.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 1: Checkout - E-commerce

actor "Cliente" as C
participant "ALB" as ALB
participant "EC2 Django" as EC2
participant "Secrets Manager" as SM
database "RDS PostgreSQL" as RDS
participant "NAT Gateway" as NAT
participant "Gateway de\nPagamento" as PSP
participant "CloudWatch" as CW

C -> PSP: Dados do cartão (formulário do gateway)
PSP --> C: card_token
C -> ALB: POST /checkout/\n{carrinho, endereço, card_token}\n(HTTPS, cookie de sessão)
activate ALB
ALB -> EC2: HTTP :8000
activate EC2

EC2 -> RDS: BEGIN\nSELECT ... FOR UPDATE (estoque)
activate RDS
alt Estoque insuficiente
  RDS --> EC2: quantidade < pedido
  EC2 -> RDS: ROLLBACK
  EC2 --> ALB: 409 Conflict
  ALB --> C: "Produto sem estoque"
else Estoque OK
  EC2 -> RDS: UPDATE estoque\nINSERT pedido (AGUARDANDO_PAGAMENTO)\nCOMMIT
  RDS --> EC2: pedido_id
  deactivate RDS

  opt Chave do gateway fora do cache (TTL 5 min)
    EC2 -> SM: GetSecretValue(ecommerce/pagamento)
    SM --> EC2: api_key
  end

  EC2 -> NAT: POST /charges {card_token, valor}
  NAT -> PSP: HTTPS (timeout 10 s)
  activate PSP
  PSP --> NAT: {status, transaction_id}
  deactivate PSP
  NAT --> EC2: resposta

  alt Pagamento aprovado
    EC2 -> RDS: UPDATE pedido SET status = PAGO,\ntransaction_id = ...
    EC2 --> ALB: 201 Created {pedido_id}
    ALB --> C: Página de confirmação
  else Recusado ou timeout
    EC2 -> RDS: UPDATE pedido SET status = PAGAMENTO_RECUSADO\nUPDATE estoque (devolve itens)
    EC2 --> ALB: 402 Payment Required
    ALB --> C: "Pagamento não aprovado"
  end
end
deactivate EC2
deactivate ALB

EC2 -> CW: Métrica PedidosPorMinuto\n(log estruturado)
@enduml
```

#### 3.1.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 1: Comunicação - Checkout

skinparam objectBackgroundColor #E3F2FD

object "Cliente" as C
object "ALB" as ALB
object "EC2 Django" as EC2
object "RDS" as RDS
object "Secrets Manager" as SM
object "NAT Gateway" as NAT
object "Gateway de Pagamento" as PSP
object "CloudWatch" as CW

C -right-> PSP : 1: tokenizar cartão
C -down-> ALB : 2: POST /checkout/
ALB -right-> EC2 : 3: HTTP :8000
EC2 -down-> RDS : 4: reservar estoque + criar pedido
EC2 -up-> SM : 5: GetSecretValue (opcional)
EC2 -right-> NAT : 6: POST /charges
NAT -up-> PSP : 7: HTTPS
EC2 -down-> RDS : 8: atualizar status
EC2 -right-> CW : 9: métrica de pedidos
ALB -left-> C : 10: confirmação
@enduml
```

#### 3.1.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Cliente | Gateway de pagamento | Tokenizar cartão | HTTPS | RNF-SEG-06 |
| 2 | Cliente | ALB | `POST /checkout/` | HTTPS (TLS 1.2+) | RNF-SEG-01 |
| 3 | ALB | EC2 | Encaminhar requisição | HTTP :8000 (rede privada) | RNF-PER-02 |
| 4 | EC2 | RDS | Transação: reservar estoque e inserir pedido | PostgreSQL/TLS :5432 | RNF-DAD-01 |
| 5 | EC2 | Secrets Manager | `GetSecretValue` (cache de 5 min) | HTTPS (VPC endpoint) | RNF-SEG-03 |
| 6-7 | EC2 | Gateway de pagamento | `POST /charges` via NAT | HTTPS | RNF-SEG-06 |
| 8 | EC2 | RDS | Atualizar status do pedido | PostgreSQL/TLS | RNF-DAD-01 |
| 9 | EC2 | CloudWatch | Métrica `PedidosPorMinuto` | HTTPS (agente) | RNF-OPS-01 |
| 10 | ALB | Cliente | `201 Created` / `402` / `409` | HTTPS | RNF-USA-03 |

#### 3.1.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| Gateway de pagamento lento ou fora do ar | Média | Alto | Timeout de 10 s, pedido fica `AGUARDANDO_PAGAMENTO` e é conciliado por webhook do gateway; alarme de taxa de recusa. |
| Venda do mesmo item duas vezes | Média | Alto | `SELECT ... FOR UPDATE` dentro da transação. |
| Cobrança duplicada por clique repetido | Média | Alto | Chave de idempotência (`pedido_id`) enviada ao gateway. |
| Falha de uma AZ da NAT Gateway | Baixa | Médio | Uma NAT Gateway por AZ (UC-ARQ-001). |
| Vazamento de dados de cartão | Baixa | Crítico | Tokenização no navegador; a plataforma guarda só `transaction_id` e status (escopo PCI-DSS reduzido). |

---

### 3.2. FLUXO 2: INGESTÃO DE EVENTO LOGÍSTICO (SERVERLESS)

#### 3.2.1. Descrição

O aplicativo do entregador envia eventos de status (coletado, em rota, entregue, tentativa frustrada) e de geolocalização. O **API Gateway** autentica pela *API key* e aplica *throttling*. A **Lambda** (associada às sub-redes privadas, UC-ARQ-004) valida o evento e grava no **DynamoDB** pelo VPC Gateway Endpoint, com TTL de 12 meses. Eventos de exceção geram alerta no **SNS** para o gestor (Sistema de Alertas do Documento de Visão). Esse fluxo **não toca o RDS** (RNF-ESC-03).

#### 3.2.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Latência da ingestão | < 80 ms (p95) | RNF-PER-01 |
| Vazão | 100 eventos/s contínuos, pico de 500 eventos/s | RNF-PER-04 |
| Sem servidores dedicados | API Gateway + Lambda + DynamoDB | RNF-ESC-02 / RNF-CUS-04 |
| Separação de cargas | Eventos só no DynamoDB | RNF-ESC-03 |
| Retenção | 12 meses (TTL) | RNF-DAD-02 |
| Criptografia em repouso | DynamoDB com KMS | RNF-SEG-02 |

#### 3.2.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 2: Ingestão de Evento Logístico - E-commerce

actor "App do\nEntregador" as App
participant "API Gateway\n(REST)" as APIGW
participant "Lambda\ningestao-eventos" as L
database "DynamoDB\neventos_entrega" as DDB
participant "SNS\nalertas-entrega" as SNS
participant "CloudWatch" as CW

App -> APIGW: POST /v1/eventos\nx-api-key\n{pedido_id, tipo, lat, lng, ts}
activate APIGW
APIGW -> APIGW: Validar API key\n+ usage plan (500 req/s, burst 1.000)

alt Limite excedido
  APIGW --> App: 429 Too Many Requests\n(app reenvia com backoff)
else Dentro do limite
  APIGW -> L: Invoke (síncrono)
  activate L
  L -> L: Validar schema\n(pedido_id, tipo, coordenadas)
  alt Payload inválido
    L --> APIGW: 400 Bad Request
  else Válido
    L -> DDB: PutItem\nPK = pedido_id, SK = ts#tipo\nexpira_em = ts + 12 meses
    activate DDB
    DDB --> L: OK (~5-10 ms)
    deactivate DDB
    opt tipo = TENTATIVA_FRUSTRADA ou ATRASO
      L -> SNS: Publish(alerta para o gestor)
    end
    L --> APIGW: 202 Accepted
  end
  deactivate L
  APIGW --> App: 202 Accepted
end
deactivate APIGW

L -> CW: Logs + métricas (Duration, Errors)
APIGW -> CW: Latency, 4XXError, 5XXError
@enduml
```

#### 3.2.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 2: Comunicação - Ingestão de Evento Logístico

skinparam objectBackgroundColor #E3F2FD

object "App do Entregador" as App
object "API Gateway" as APIGW
object "Lambda" as L
object "DynamoDB" as DDB
object "SNS" as SNS
object "CloudWatch" as CW

App -right-> APIGW : 1: POST /v1/eventos
APIGW -right-> L : 2: Invoke
L -right-> DDB : 3: PutItem
L -down-> SNS : 4: Publish (exceções)
L -down-> CW : 5: logs e métricas
L -left-> APIGW : 6: 202 Accepted
APIGW -left-> App : 7: 202 Accepted
@enduml
```

#### 3.2.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | App do entregador | API Gateway | `POST /v1/eventos` + `x-api-key` | HTTPS | RNF-PER-04, RNF-SEG-01 |
| 2 | API Gateway | Lambda | Invoke síncrono | Integração AWS | RNF-ESC-02 |
| 3 | Lambda | DynamoDB | `PutItem` com TTL | HTTPS (VPC Gateway Endpoint) | RNF-PER-01, RNF-DAD-02 |
| 4 | Lambda | SNS | `Publish` (somente exceções) | HTTPS | Visão: Sistema de Alertas |
| 5 | Lambda | CloudWatch | Logs e métricas | HTTPS | RNF-OPS-01/02 |
| 6-7 | Lambda → API Gateway → App | - | `202 Accepted` | HTTPS | RNF-PER-01 |

**Orçamento de latência (p95 < 80 ms):** API Gateway ~10 ms + Lambda aquecida ~15 ms + DynamoDB ~10 ms + rede ~20 ms ≈ **55 ms**.

#### 3.2.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| *Cold start* da Lambda na VPC ultrapassa 80 ms | Média | Médio | *Provisioned concurrency* de 5 instâncias (500 ev/s × 20 ms = 10 execuções simultâneas no pico; o restante escala sob demanda). |
| *Throttling* no pico | Baixa | Médio | Usage plan acima do pico (500 req/s); app guarda eventos offline e reenvia com backoff. |
| Evento duplicado (reenvio) | Média | Baixo | Chave `pedido_id + ts#tipo` torna o `PutItem` idempotente. |
| API key vazada | Baixa | Alto | Uma key por parceiro logístico, rotação e revogação no usage plan. |
| Crescimento ilimitado da tabela | Baixa | Médio | TTL de 12 meses (RNF-DAD-02); exportação para S3 antes da expiração (RNF-DAD-03). |

---

### 3.3. FLUXO 3: CONSULTA DE RASTREAMENTO DO PEDIDO

#### 3.3.1. Descrição

O cliente (ou o gestor) abre a página de rastreamento. O Django confirma no **RDS** que o pedido pertence ao usuário autenticado e busca no **DynamoDB** os eventos mais recentes daquele pedido. Os dois bancos ficam separados (RNF-ESC-03): o volume de eventos não afeta o desempenho do checkout.

#### 3.3.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Tempo de resposta | < 2 s (p95) | RNF-PER-02 |
| Separação de cargas | RDS para pedidos, DynamoDB para eventos | RNF-ESC-03 |
| Controle de acesso | Cliente só vê os próprios pedidos | RNF-SEG-04 / RNF-SEG-07 |
| Painel em tempo quase real | Eventos disponíveis segundos após a ingestão | Documento de Visão |

#### 3.3.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 3: Consulta de Rastreamento - E-commerce

actor "Cliente" as C
participant "ALB" as ALB
participant "EC2 Django" as EC2
database "RDS PostgreSQL" as RDS
database "DynamoDB\neventos_entrega" as DDB

C -> ALB: GET /pedidos/123/rastreamento/\n(cookie de sessão)
activate ALB
ALB -> EC2: HTTP :8000
activate EC2
EC2 -> RDS: SELECT pedido WHERE id = 123\nAND cliente_id = :usuario
activate RDS
RDS --> EC2: pedido (ou vazio)
deactivate RDS

alt Pedido não pertence ao usuário
  EC2 --> ALB: 404 Not Found
  ALB --> C: "Pedido não encontrado"
else Pedido do usuário
  EC2 -> DDB: Query PK = 123\nScanIndexForward = false, Limit = 20
  activate DDB
  DDB --> EC2: últimos eventos (status, lat, lng, ts)
  deactivate DDB
  EC2 -> EC2: Montar linha do tempo\ne posição atual
  EC2 --> ALB: 200 OK (HTML/JSON)
  ALB --> C: Página de rastreamento
end
deactivate EC2
deactivate ALB
@enduml
```

#### 3.3.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 3: Comunicação - Consulta de Rastreamento

skinparam objectBackgroundColor #E3F2FD

object "Cliente" as C
object "ALB" as ALB
object "EC2 Django" as EC2
object "RDS" as RDS
object "DynamoDB" as DDB

C -right-> ALB : 1: GET /pedidos/123/rastreamento/
ALB -right-> EC2 : 2: HTTP :8000
EC2 -down-> RDS : 3: SELECT pedido (dono)
EC2 -right-> DDB : 4: Query eventos (Limit 20)
EC2 -left-> ALB : 5: 200 OK
ALB -left-> C : 6: página de rastreamento
@enduml
```

#### 3.3.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Cliente | ALB | `GET /pedidos/{id}/rastreamento/` | HTTPS | RNF-SEG-01 |
| 2 | ALB | EC2 | Encaminhar requisição | HTTP :8000 | RNF-PER-02 |
| 3 | EC2 | RDS | Verificar dono do pedido | PostgreSQL/TLS | RNF-SEG-04 |
| 4 | EC2 | DynamoDB | `Query` por `pedido_id`, 20 itens mais recentes | HTTPS (VPC Gateway Endpoint) | RNF-ESC-03 |
| 5-6 | EC2 → ALB → Cliente | - | `200 OK` | HTTPS | RNF-PER-02 |

#### 3.3.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| Cliente acessar pedido de outro (IDOR) | Média | Alto | Filtro obrigatório por `cliente_id` na consulta ao RDS antes de ler o DynamoDB. |
| Atualização frequente da página gerar muitas leituras | Média | Baixo | `Limit = 20`, cache de 10 s no Django; DynamoDB on-demand. |
| DynamoDB indisponível | Baixa | Médio | Exibir o status do pedido do RDS com aviso "rastreamento temporariamente indisponível". |

---

### 3.4. FLUXO 4: AUTENTICAÇÃO E AUTORIZAÇÃO POR PERFIL

#### 3.4.1. Descrição

Clientes e gestores entram pelo portal. O Django valida a senha (hash Argon2 no RDS) e, para usuários do grupo **Gestor/Administrador**, exige um segundo fator **TOTP** (RNF-SEG-05). A sessão é gravada no RDS e o navegador recebe um cookie `Secure` e `HttpOnly`. A cada requisição, o Django verifica o **perfil** (grupos `Cliente`, `Gestor`, `OperadorLogistico`) antes de executar a view (RNF-SEG-04). O entregador não usa o portal: o aplicativo dele se autentica no API Gateway (Fluxo 2).

#### 3.4.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Perfis de acesso | Cliente, Gestor/Administrador, Operador Logístico | RNF-SEG-04 |
| MFA | Obrigatório para contas administrativas | RNF-SEG-05 |
| Criptografia em trânsito | TLS 1.2+ | RNF-SEG-01 |
| Dados pessoais protegidos | Senha com hash, sessão em cookie seguro | RNF-SEG-07 |
| Rastreabilidade | Log de login e falhas | RNF-OPS-04 |

#### 3.4.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 4: Autenticação e Autorização - E-commerce

actor "Gestor" as G
participant "ALB" as ALB
participant "EC2 Django\n(auth + django-otp)" as EC2
database "RDS PostgreSQL" as RDS
participant "CloudWatch Logs" as CW

G -> ALB: POST /login/ {email, senha}
ALB -> EC2: HTTP :8000
activate EC2
EC2 -> RDS: SELECT usuario, hash, grupos, tentativas
RDS --> EC2: dados do usuário
EC2 -> EC2: Verificar hash Argon2

alt Senha inválida
  EC2 -> RDS: Incrementar tentativas\n(bloqueio após 5 em 15 min)
  EC2 -> CW: log login_falhou
  EC2 --> ALB: 401
  ALB --> G: "Credenciais inválidas"
else Senha válida
  alt Usuário do grupo Gestor
    EC2 --> ALB: 200 (solicitar código TOTP)
    ALB --> G: Tela do segundo fator
    G -> ALB: POST /login/mfa/ {codigo}
    ALB -> EC2: HTTP :8000
    EC2 -> EC2: Validar TOTP (janela de 30 s)
  end
  EC2 -> RDS: INSERT sessão
  EC2 -> CW: log login_ok {usuario, perfil, ip}
  EC2 --> ALB: 302 + Set-Cookie (Secure, HttpOnly, SameSite=Lax)
  ALB --> G: Redirecionar para o painel
end
deactivate EC2

== Requisição autenticada ==
G -> ALB: GET /gestao/relatorios/ (cookie)
ALB -> EC2: HTTP :8000
activate EC2
EC2 -> RDS: Carregar sessão
EC2 -> EC2: Verificar permissão\n(grupo Gestor)
alt Sem permissão
  EC2 --> ALB: 403 Forbidden
else Autorizado
  EC2 --> ALB: 200 OK
end
deactivate EC2
ALB --> G: Resposta
@enduml
```

#### 3.4.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 4: Comunicação - Autenticação e Autorização

skinparam objectBackgroundColor #E3F2FD

object "Gestor" as G
object "ALB" as ALB
object "EC2 Django" as EC2
object "RDS" as RDS
object "CloudWatch Logs" as CW

G -right-> ALB : 1: POST /login/
ALB -right-> EC2 : 2: HTTP :8000
EC2 -down-> RDS : 3: buscar usuário e grupos
G -right-> ALB : 4: POST /login/mfa/ (gestor)
EC2 -down-> RDS : 5: criar sessão
EC2 -right-> CW : 6: log de login
ALB -left-> G : 7: Set-Cookie
G -right-> ALB : 8: requisição autenticada
EC2 -down-> RDS : 9: carregar sessão + verificar grupo
@enduml
```

#### 3.4.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1-2 | Gestor → ALB → EC2 | - | `POST /login/` | HTTPS → HTTP :8000 | RNF-SEG-01 |
| 3 | EC2 | RDS | Buscar usuário, hash e grupos | PostgreSQL/TLS | RNF-SEG-07 |
| 4 | Gestor | ALB | `POST /login/mfa/` (código TOTP) | HTTPS | RNF-SEG-05 |
| 5 | EC2 | RDS | Criar sessão | PostgreSQL/TLS | - |
| 6 | EC2 | CloudWatch Logs | Evento de login | HTTPS | RNF-OPS-04 |
| 7 | ALB | Gestor | `302` + cookie seguro | HTTPS | RNF-SEG-07 |
| 8-9 | Gestor → EC2 → RDS | - | Requisição com verificação de perfil | HTTPS / PostgreSQL | RNF-SEG-04 |

#### 3.4.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| Ataque de força bruta | Alta | Alto | Bloqueio após 5 tentativas em 15 min; alarme de `login_falhou` no CloudWatch. |
| Roubo de sessão | Baixa | Alto | Cookie `Secure`, `HttpOnly`, `SameSite`; sessão expira em 2 h para gestores. |
| Gestor perde o app autenticador | Média | Médio | Códigos de recuperação de uso único gerados no cadastro do MFA. |
| Escalada de privilégio | Baixa | Crítico | Permissões por grupo testadas automaticamente no CodeBuild. |

---

### 3.5. FLUXO 5: ENVIO DO COMPROVANTE DE ENTREGA (S3)

#### 3.5.1. Descrição

Ao concluir a entrega, o aplicativo do entregador pede ao API Gateway uma **URL pré-assinada** de upload. A Lambda gera a URL (válida por 5 minutos, restrita a um único objeto) e o aplicativo envia a foto ou assinatura **diretamente ao S3**. O arquivo é criptografado com KMS e o bucket bloqueia acesso público. O comprovante contém dados pessoais (nome e assinatura de quem recebeu), por isso o acesso é restrito (LGPD).

#### 3.5.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Armazenamento de arquivos | S3 | Documento de Visão / UC-ARQ-003 |
| Criptografia em repouso | SSE-KMS | RNF-SEG-02 |
| Criptografia em trânsito | HTTPS | RNF-SEG-01 |
| Acesso restrito a dados pessoais | Bucket privado, URL temporária | RNF-SEG-07 |
| Arquivamento | Lifecycle para classes mais baratas | RNF-DAD-03 |

#### 3.5.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 5: Envio do Comprovante de Entrega - E-commerce

actor "App do\nEntregador" as App
participant "API Gateway" as APIGW
participant "Lambda\ngerar-url-comprovante" as L
participant "S3\necommerce-comprovantes" as S3
participant "KMS" as KMS
database "DynamoDB" as DDB

App -> APIGW: POST /v1/comprovantes {pedido_id}\nx-api-key
activate APIGW
APIGW -> L: Invoke
activate L
L -> L: Validar pedido_id\ne tipo de arquivo (image/jpeg)
L -> S3: Gerar URL pré-assinada PUT\n(chave comprovantes/{pedido_id}.jpg,\nexpira em 300 s)
S3 --> L: URL assinada
L --> APIGW: 200 {upload_url}
deactivate L
APIGW --> App: 200 {upload_url}
deactivate APIGW

App -> S3: PUT upload_url (foto, até 5 MB)
activate S3
S3 -> KMS: GenerateDataKey (SSE-KMS)
KMS --> S3: chave de dados
S3 -> S3: Gravar objeto criptografado
S3 --> App: 200 OK
deactivate S3

App -> APIGW: POST /v1/eventos {tipo: ENTREGUE,\ncomprovante: chave}
note right: Segue o Fluxo 2\n(grava o evento no DynamoDB)
APIGW -> DDB: (via Lambda de ingestão)
@enduml
```

#### 3.5.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 5: Comunicação - Envio do Comprovante

skinparam objectBackgroundColor #E3F2FD

object "App do Entregador" as App
object "API Gateway" as APIGW
object "Lambda" as L
object "S3" as S3
object "KMS" as KMS
object "DynamoDB" as DDB

App -right-> APIGW : 1: POST /v1/comprovantes
APIGW -right-> L : 2: Invoke
L -down-> S3 : 3: gerar URL pré-assinada
App -down-> S3 : 4: PUT foto
S3 -right-> KMS : 5: GenerateDataKey
App -right-> APIGW : 6: POST /v1/eventos (ENTREGUE)
APIGW -down-> DDB : 7: PutItem (via Lambda)
@enduml
```

#### 3.5.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | App | API Gateway | `POST /v1/comprovantes` | HTTPS | RNF-SEG-01 |
| 2 | API Gateway | Lambda | Invoke | Integração AWS | RNF-ESC-02 |
| 3 | Lambda | S3 | Assinar URL de `PUT` (300 s) | Local (SDK) | RNF-SEG-07 |
| 4 | App | S3 | `PUT` do arquivo | HTTPS | RNF-SEG-01 |
| 5 | S3 | KMS | `GenerateDataKey` | Interno AWS | RNF-SEG-02 |
| 6-7 | App → API Gateway → DynamoDB | - | Evento `ENTREGUE` com referência ao arquivo | HTTPS | RNF-DAD-01 |

#### 3.5.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| URL pré-assinada reutilizada ou vazada | Baixa | Médio | Expira em 300 s, vale para uma única chave e tipo de arquivo. |
| Upload de arquivo malicioso ou grande | Média | Baixo | Tipo e tamanho fixados na assinatura; bucket sem execução de conteúdo. |
| Exposição pública de comprovantes | Baixa | Crítico | *Block Public Access* na conta, bucket policy exige TLS e KMS. |
| Custo de armazenamento crescente | Média | Baixo | Lifecycle: Standard-IA após 30 dias e Glacier após 180 dias. |

---

### 3.6. FLUXO 6: FAILOVER DO RDS (MULTI-AZ)

#### 3.6.1. Descrição

Se a instância primária ou a AZ `us-east-1a` falhar, o serviço RDS promove automaticamente a standby síncrona em `us-east-1b` e atualiza o DNS do endpoint. O Django reconecta usando o mesmo endpoint. O CloudWatch e o SNS **avisam** a equipe, mas não comandam o failover. Detalhes no documento de Dimensionamento do RDS (seção 5).

#### 3.6.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Disponibilidade | 99,95% | RNF-DIS-01 |
| Redundância | RDS Multi-AZ | RNF-DIS-02 |
| RPO | ≤ 15 min (Multi-AZ: 0) | RNF-BCP-01 |
| RTO | < 1 h (failover: 1-2 min) | RNF-BCP-02 |
| Alarmes | Notificação de indisponibilidade | RNF-OPS-02 |

#### 3.6.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 6: Failover do RDS - E-commerce

participant "EC2 Django" as EC2
participant "DNS do endpoint RDS" as DNS
database "RDS Primary\n(us-east-1a)" as P
database "RDS Standby\n(us-east-1b)" as S
participant "Serviço RDS" as RDS
participant "EventBridge /\nCloudWatch" as CW
participant "SNS" as SNS

EC2 -> P: Consultas (5432/TLS)
P -> S: Replicação síncrona
P -[#red]>x EC2: Falha da AZ us-east-1a
RDS -> P: Detectar falha
RDS -> S: Promover a primária
activate S
RDS -> DNS: Atualizar CNAME (TTL 5 s)
RDS -> CW: Evento "failover completed"
CW -> SNS: Publicar alerta
SNS -> SNS: E-mail para a equipe
EC2 -> EC2: Erro de conexão\nretry com backoff
EC2 -> DNS: Resolver endpoint
DNS --> EC2: IP da nova primária
EC2 -> S: Reconectar e retomar
deactivate S
RDS -> RDS: Criar nova standby\nem outra AZ
@enduml
```

#### 3.6.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 6: Comunicação - Failover do RDS

skinparam objectBackgroundColor #E3F2FD

object "Serviço RDS" as RDS
object "RDS Primary" as P
object "RDS Standby" as S
object "DNS do endpoint" as DNS
object "EventBridge/CloudWatch" as CW
object "SNS" as SNS
object "EC2 Django" as EC2

RDS -down-> P : 1: detectar falha
RDS -right-> S : 2: promover
RDS -down-> DNS : 3: atualizar CNAME
RDS -right-> CW : 4: evento de failover
CW -down-> SNS : 5: alerta
EC2 -up-> DNS : 6: resolver endpoint
EC2 -right-> S : 7: reconectar
@enduml
```

#### 3.6.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Serviço RDS | RDS Primary | Monitoramento de saúde | Interno AWS | RNF-DIS-02 |
| 2 | Serviço RDS | RDS Standby | Promover a primária | Interno AWS | RNF-BCP-02 |
| 3 | Serviço RDS | DNS | Atualizar CNAME do endpoint | Interno AWS | RNF-BCP-02 |
| 4 | Serviço RDS | EventBridge/CloudWatch | Evento de failover | Interno AWS | RNF-OPS-02 |
| 5 | CloudWatch | SNS | Alerta para a equipe | HTTPS | RNF-OPS-02 |
| 6 | EC2 | DNS | Resolver endpoint | DNS | - |
| 7 | EC2 | Nova primária | Reconexão | PostgreSQL/TLS | RNF-DIS-01 |

#### 3.6.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| Aplicação guarda o IP antigo em cache | Baixa | Alto | Conexões com `CONN_HEALTH_CHECKS = True` no Django; sem cache de DNS na instância. |
| Erros 5xx durante o failover (1-2 min) | Alta (durante o evento) | Médio | Retry com backoff no Django; página amigável no checkout. |
| Health check do ALB derrubar todas as EC2 | Baixa | Alto | `/health/` não consulta o banco (documento de EC2, seção 3.4). |

---

### 3.7. FLUXO 7: DEPLOY AUTOMATIZADO (CI/CD BLUE/GREEN)

#### 3.7.1. Descrição

Um merge na branch `main` do GitHub dispara o **CodePipeline**. O **CodeBuild** instala dependências e roda os testes. Após **aprovação manual** (UC-ARQ-006), o **CodeDeploy** cria uma cópia do Auto Scaling Group (ambiente *green*) com a nova versão. Quando ela passa no health check, o CodeDeploy troca o tráfego do ALB do *blue* para o *green*. O ambiente *blue* fica disponível por 15 minutos para rollback rápido. Detalhes no documento de Estratégias de Deploy.

#### 3.7.2. Requisitos Atendidos

| **Requisito** | **Valor** | **Fonte** |
| :--- | :--- | :--- |
| Pipeline integrado ao repositório | CodePipeline + GitHub | RNF-MAN-03 |
| Tempo de deploy | < 10 min | UC-ARQ-006 |
| Tempo de rollback | < 5 min | UC-ARQ-006 |
| Sem indisponibilidade no deploy | Blue/Green | RNF-DIS-01 |
| Falha de build notificada | SNS | UC-ARQ-006 (Alt 1) |

#### 3.7.3. Diagrama de Sequência

```plantuml
@startuml
title Fluxo 7: Deploy Blue/Green - E-commerce

actor "Engenheiro\nde DevOps" as Dev
participant "GitHub" as GH
participant "CodePipeline" as CP
participant "CodeBuild" as CB
participant "CodeDeploy" as CD
participant "ASG green\n(cópia)" as Green
participant "ALB / Target Group" as ALB
participant "ASG blue\n(atual)" as Blue
participant "SNS" as SNS

Dev -> GH: Merge na main
GH -> CP: Webhook
CP -> CB: Build + testes
activate CB
CB --> CP: Artefato (zip) no S3
deactivate CB
CP -> Dev: Solicitar aprovação manual
Dev -> CP: Aprovar
CP -> CD: CreateDeployment (Blue/Green)
activate CD
CD -> Green: Copiar ASG e lançar instâncias
Green -> Green: Instalar revisão (AppSpec hooks)
CD -> ALB: Registrar green no target group de teste
ALB -> Green: Health check /health/
Green --> ALB: 200 OK
CD -> ALB: Trocar tráfego (blue -> green)
CD -> CD: Aguardar 15 min\n(alarmes de 5xx e latência)
alt Alarmes OK
  CD -> Blue: Terminar instâncias blue
  CD -> SNS: Deploy concluído
else Alarme disparado
  CD -> ALB: Rollback (green -> blue)
  CD -> Green: Terminar green
  CD -> SNS: Rollback executado
end
deactivate CD
@enduml
```

#### 3.7.4. Diagrama de Comunicação

```plantuml
@startuml
title Fluxo 7: Comunicação - Deploy Blue/Green

skinparam objectBackgroundColor #E3F2FD

object "DevOps" as Dev
object "GitHub" as GH
object "CodePipeline" as CP
object "CodeBuild" as CB
object "CodeDeploy" as CD
object "ASG green" as Green
object "ALB" as ALB
object "ASG blue" as Blue
object "SNS" as SNS

Dev -right-> GH : 1: merge
GH -right-> CP : 2: webhook
CP -down-> CB : 3: build e testes
Dev -down-> CP : 4: aprovação manual
CP -right-> CD : 5: CreateDeployment
CD -down-> Green : 6: lançar e instalar
CD -right-> ALB : 7: trocar tráfego
CD -down-> Blue : 8: terminar (após 15 min)
CD -right-> SNS : 9: notificar
@enduml
```

#### 3.7.5. Tabela de Mensagens

| **#** | **De** | **Para** | **Mensagem** | **Protocolo** | **Requisito** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1-2 | DevOps → GitHub → CodePipeline | - | Merge e webhook | HTTPS | RNF-MAN-01/03 |
| 3 | CodePipeline | CodeBuild | Executar `buildspec.yml` | Interno AWS | UC-ARQ-006 |
| 4 | DevOps | CodePipeline | Aprovação manual | Console AWS | UC-ARQ-006 |
| 5 | CodePipeline | CodeDeploy | `CreateDeployment` | Interno AWS | UC-ARQ-006 |
| 6 | CodeDeploy | ASG green | Copiar ASG e instalar revisão | Interno AWS | RNF-DIS-01 |
| 7 | CodeDeploy | ALB | Trocar target group do listener | Interno AWS | Deploy < 10 min |
| 8 | CodeDeploy | ASG blue | Terminar instâncias antigas | Interno AWS | RNF-CUS-03 |
| 9 | CodeDeploy | SNS | Notificar resultado | HTTPS | UC-ARQ-006 (Alt 1/2) |

#### 3.7.6. Riscos e Mitigações

| **Risco** | **Probabilidade** | **Impacto** | **Mitigação** |
| :--- | :--- | :--- | :--- |
| Migração de banco incompatível com a versão anterior | Média | Alto | Migrações compatíveis com as duas versões (expandir, depois contrair) e snapshot manual antes. |
| Deploy durante pico sazonal | Baixa | Alto | Congelamento de deploys em dias de campanha. |
| Aprovação manual atrasar o deploy | Média | Baixo | Tempo de deploy medido a partir da aprovação. |

---

## 4. Diagrama de Classes Consolidado

```plantuml
@startuml
title Diagrama de Classes Consolidado - E-commerce na AWS

skinparam classAttributeIconSize 0
skinparam classBackgroundColor #F5F5F5
hide empty methods

package "Rede (UC-ARQ-001/002/003)" {
  class VPC {
    cidr: 10.0.0.0/16
  }
  class Subnet {
    tipo: pública | privada
    cidr: 10.0.x.0/24
    az: us-east-1a | us-east-1b
  }
  class SecurityGroup {
    nome: SG-ALB | SG-EC2-Django | SG-RDS
  }
  class NATGateway {
    quantidade: 1 por AZ
  }
  class VPCEndpoint {
    servico: DynamoDB | S3 | Secrets Manager
  }
}

package "Computação (Semana 6)" {
  class LoadBalancer {
    tipo: ALB
    listeners: 443, 80 -> 301
  }
  class TargetGroup {
    porta: 8000
    healthCheck: /health/
  }
  class AutoScalingGroup {
    min: 2
    max: 12
  }
  class LaunchTemplate {
    tipo: t3.medium
  }
  class ComputeInstance {
    app: Django + Gunicorn
  }
  class ScalingPolicy {
    alvo: CPU 50%
  }
}

package "Banco Transacional (Semana 5)" {
  class DatabaseInstance {
    classe: db.t3.medium
    multiAZ: true
  }
  class ReadReplica {
    classe: db.t3.small
  }
  class BackupPolicy {
    retencao: 14 dias
    pitr: true
  }
}

package "Ingestão Serverless" {
  class ApiGateway {
    tipo: REST
    usagePlan: 500 req/s
  }
  class LambdaFunction {
    nome: ingestao-eventos | gerar-url-comprovante
    memoria: 256 MB
  }
  class DynamoTable {
    nome: eventos_entrega
    ttl: 12 meses
    capacidade: on-demand
  }
}

package "Armazenamento" {
  class Bucket {
    nome: ecommerce-imagens | ecommerce-comprovantes
    criptografia: SSE-KMS
  }
}

package "Segurança e Operação (Semana 4)" {
  class KmsKey
  class Secret {
    rotacao: 30 dias
  }
  class Alarm
  class Topic {
    servico: SNS
  }
  class Pipeline {
    estrategia: Blue/Green
  }
}

VPC "1" *-- "4" Subnet
VPC "1" *-- "3" SecurityGroup
Subnet "1" o-- "0..1" NATGateway
VPC "1" o-- "3" VPCEndpoint

LoadBalancer "1" --> "1..2" TargetGroup
TargetGroup "1" o-- "2..12" ComputeInstance
AutoScalingGroup "1" o-- "2..12" ComputeInstance
AutoScalingGroup --> LaunchTemplate
AutoScalingGroup *-- ScalingPolicy
ComputeInstance --> DatabaseInstance : 5432/TLS
ComputeInstance ..> ReadReplica : relatórios
ComputeInstance --> DynamoTable : Query
ComputeInstance --> Bucket : URL pré-assinada
ComputeInstance --> Secret

DatabaseInstance "1" -- "0..*" ReadReplica
DatabaseInstance "1" -- "1" BackupPolicy

ApiGateway --> LambdaFunction
LambdaFunction --> DynamoTable : PutItem
LambdaFunction --> Bucket : URL de upload
LambdaFunction --> Topic : exceções

DatabaseInstance ..> KmsKey
DynamoTable ..> KmsKey
Bucket ..> KmsKey
Alarm --> Topic
Pipeline --> AutoScalingGroup : Blue/Green
LoadBalancer --> Subnet : públicas
ComputeInstance --> Subnet : privadas
DatabaseInstance --> Subnet : privadas
LambdaFunction --> Subnet : privadas
@enduml
```

---

## 5. Matriz de Rastreamento Consolidada

| **Fluxo** | **Requisito** | **Caso de Uso** | **Pacote** | **Classes** | **Serviços AWS** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Fluxo 1 - Checkout | RNF-PER-02/03, RNF-SEG-03/06 | UC-ARQ-004, UC-ARQ-007 | Secrets Management, Data Protection | `LoadBalancer`, `ComputeInstance`, `DatabaseInstance`, `Secret` | ALB, EC2, RDS, Secrets Manager, NAT Gateway |
| Fluxo 2 - Ingestão | RNF-PER-01/04, RNF-ESC-02/03, RNF-DAD-02 | UC-ARQ-003, UC-ARQ-004 | Data Protection, Monitoring & Detection | `ApiGateway`, `LambdaFunction`, `DynamoTable` | API Gateway, Lambda, DynamoDB, SNS |
| Fluxo 3 - Rastreamento | RNF-PER-02, RNF-ESC-03, RNF-SEG-04 | UC-ARQ-003, UC-ARQ-004 | Identity & Access | `ComputeInstance`, `DatabaseInstance`, `DynamoTable` | ALB, EC2, RDS, DynamoDB |
| Fluxo 4 - Autenticação | RNF-SEG-01/04/05/07, RNF-OPS-04 | UC-ARQ-002, UC-ARQ-007 | Identity & Access, Audit & Compliance | `ComputeInstance`, `DatabaseInstance` | ALB, EC2, RDS, CloudWatch Logs |
| Fluxo 5 - Comprovante | RNF-SEG-01/02/07, RNF-DAD-03 | UC-ARQ-003, UC-ARQ-007 | Data Protection | `LambdaFunction`, `Bucket`, `KmsKey` | API Gateway, Lambda, S3, KMS |
| Fluxo 6 - Failover RDS | RNF-DIS-01/02, RNF-BCP-01/02, RNF-OPS-02 | UC-ARQ-004, UC-ARQ-005 | Data Protection, Monitoring & Detection | `DatabaseInstance`, `BackupPolicy`, `Alarm` | RDS Multi-AZ, CloudWatch, SNS |
| Fluxo 7 - Deploy | RNF-MAN-01/03, RNF-DIS-01 | UC-ARQ-006 | Audit & Compliance | `Pipeline`, `AutoScalingGroup`, `TargetGroup` | CodePipeline, CodeBuild, CodeDeploy, ALB |

### 5.1. Orçamento Consolidado

Soma das estimativas dos documentos de RDS e EC2 com os demais serviços usados nos fluxos. Preços de referência sob demanda em us-east-1.

| **Componente** | **Base da estimativa** | **Custo Mensal** |
| :--- | :--- | :--- |
| RDS (primária Multi-AZ + réplica + backup) | Documento de RDS, seção 7.4 | US$ 150,78 |
| EC2 + ALB + saída de dados do portal | Documento de EC2, seção 8.4 | US$ 357,41 |
| NAT Gateway | 2 (1 por AZ) × US$ 0,045 × 730 h | US$ 65,70 |
| VPC Interface Endpoints | S3 e Secrets Manager, 2 AZs × US$ 0,01 × 730 h | US$ 29,20 |
| API Gateway (REST) | ~12,3 milhões de eventos/mês × US$ 3,50/milhão | US$ 43,05 |
| Lambda | Requisições + execução + 5 de *provisioned concurrency* | US$ 17,00 |
| DynamoDB (on-demand) | Escritas, leituras, armazenamento e PITR | US$ 25,00 |
| S3 | Imagens e comprovantes + saída de imagens (com cache no navegador) | US$ 110,00 |
| CloudWatch | Logs com retenção de 90 dias, alarmes e dashboard | US$ 25,00 |
| KMS | 3 chaves + requisições | US$ 4,00 |
| CodePipeline / CodeBuild / CodeDeploy | Documento de Deploy, seção 6 | US$ 2,20 |
| Route 53 | 1 zona hospedada + consultas | US$ 1,50 |
| Secrets Manager (chave do gateway) | 1 segredo adicional | US$ 0,40 |
| **TOTAL** | | **~US$ 831/mês** |

**Percentual do orçamento:** ~US$ 831 ÷ US$ 1.500 = **~55%**. A folga de ~US$ 670 cobre meses com mais campanhas sazonais e erros nas premissas de carga. Duas otimizações já identificadas: usar **Gateway Endpoint** (gratuito) para o S3 no lugar do Interface Endpoint (-US$ 14,60) e colocar o **CloudFront** à frente do ALB e do S3 (redução estimada de ~US$ 90 a US$ 150 na saída de dados).

---

## 6. Considerações Finais

### 6.1. Lições Aprendidas

- Os diagramas de sequência mostraram que **o RDS só é acessado pelo Django**: a ingestão logística (Fluxos 2 e 5) é totalmente serverless, cumprindo o RNF-ESC-03.
- O checkout depende de um **serviço externo**, o gateway de pagamento. Timeout, idempotência e conciliação por webhook são tão importantes quanto a infraestrutura AWS.
- A **disponibilidade composta** dos componentes em série (ALB 99,99% × EC2 em várias AZs 99,99% × RDS Multi-AZ 99,95%) é de cerca de **99,93%**, um pouco abaixo da meta de 99,95%. Os SLAs da AWS são valores mínimos contratuais e a disponibilidade real costuma ser maior, mas a meta deve ser **acompanhada por métricas** (RNF-DIS-01) e não apenas presumida.
- Em vários fluxos o CloudWatch e o SNS **observam e avisam**, mas quem age é o serviço gerenciado (RDS no failover, ASG na substituição de instâncias, CodeDeploy no rollback).
- O custo total estimado (~55% do orçamento) é dominado pela **transferência de dados**, não pelos servidores.

### 6.2. Próximos Passos

- **Semana 10:** Modelo de Design (Atividades) - estratégias de deploy (Blue/Green, Canary e Rolling).
- Implementar o pipeline do Fluxo 7 e o teste de carga do Fluxo 1 com 1.000 usuários simultâneos.
- Avaliar a adoção do CloudFront e a troca do Interface Endpoint do S3 por Gateway Endpoint.
- Corrigir a matriz de rastreamento do Modelo de Pacotes, que cita casos de uso inexistentes (UC-ARQ-008 a 010).

---

## 7. Aprovações

| **Função** | **Nome** | **Data** | **Assinatura** |
| :--- | :--- | :--- | :--- |
| Arquiteto de Soluções | | | |
| Arquiteto de Design | | | |
| Professor Responsável | | | |
| Coordenador do Curso | | | |

---

## 8. Histórico de Versões

| **Versão** | **Data** | **Autor** | **Descrição das Alterações** |
| :--- | :--- | :--- | :--- |
| 0.1 | 29/10/2026 | Grupo E-commerce | Criação do documento a partir do modelo SwiftTrack. |
| 1.0 | 29/10/2026 | Grupo E-commerce | Sete fluxos do e-commerce com diagramas, diagrama de classes consolidado, matriz e orçamento consolidado. |
