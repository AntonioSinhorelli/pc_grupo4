# Modelo de Análise (Pacotes/Subsistemas)

## E-COMMERCE — ARQUITETURA DE SEGURANÇA EM NUVEM AWS

### Informação do Documento

| Campo | Valor |
|---|---|
| Projeto | Plataforma de E-commerce e Marketplace |
| Documento | Modelo de Análise (Pacotes/Subsistemas) - Segurança |
| Versão | 1.0 |
| Data | 23/09/2026 |
| Status | Em Desenvolvimento |
| Responsável | Grupo E-commerce |
| Disciplina | Projeto de Cloud |
| Fase RUP/UP | Elaboration |

---

## 1. INTRODUÇÃO

### 1.1. Propósito

Este documento apresenta o Modelo de Análise (Pacotes/Subsistemas) para a arquitetura de segurança da plataforma de e-commerce na AWS. O modelo organiza os componentes de segurança em pacotes coesos, facilitando a compreensão, manutenção e evolução da arquitetura, além de permitir a rastreabilidade entre requisitos de segurança e elementos técnicos.

O modelo é derivado diretamente dos seguintes artefatos:
- Documento de Visão (Semana 1) — Seção "Segurança e Privacidade"
- Documento de Requisitos Suplementares (Semana 2) — Seção "Requisitos de Segurança"
- Modelo de Casos de Uso Arquiteturais (Semana 3) — UC-ARQ-002 e UC-ARQ-007

### 1.2. Escopo

O modelo abrange os subsistemas de segurança necessários para proteger:
- Dados pessoais de clientes e vendedores (LGPD)
- Dados de pagamento e cartão de crédito (PCI-DSS)
- Credenciais de banco de dados e integrações de pagamento
- Carrinho de compras e sessões de checkout
- Catálogo de produtos e imagens
- Pedidos, notas fiscais eletrônicas (NF-e) e histórico de compras
- Logs de auditoria e transações

### 1.3. Definições e Siglas

| Sigla | Definição |
|---|---|
| IAM | Identity and Access Management |
| KMS | Key Management Service |
| CMK | Customer Managed Key |
| SG | Security Group |
| NACL | Network Access Control List |
| WAF | Web Application Firewall |
| RBAC | Role-Based Access Control |
| MFA | Multi-Factor Authentication |
| LGPD | Lei Geral de Proteção de Dados |
| PCI-DSS | Payment Card Industry Data Security Standard |
| TLS | Transport Layer Security |
| SSE | Server-Side Encryption |
| PITR | Point-In-Time Recovery |
| NF-e | Nota Fiscal Eletrônica |

### 1.4. Referências

- Documento de Visão — E-commerce (v1.0)
- Documento de Requisitos Suplementares — E-commerce (v1.0)
- Modelo de Casos de Uso Arquiteturais — E-commerce (v1.0)
- AWS Well-Architected Framework — Security Pillar
- AWS IAM Best Practices
- Lei Geral de Proteção de Dados (LGPD)
- PCI Security Standards Council — PCI-DSS v4.0

---

## 2. VISÃO GERAL DOS PACOTES DE SEGURANÇA

### 2.1. Diagrama de Pacotes

```plantuml
@startuml
title Diagrama de Pacotes - E-commerce (Segurança)
skinparam packageStyle rectangle
skinparam shadowing false
skinparam defaultTextAlignment center

package "E-commerce — Segurança" as SS {
  package "Identity & Access\n<i>Identidade e Acesso</i>" as IAM #E3F2FD
  package "Network Security\n<i>Segurança de Rede</i>" as NET #FFF3E0
  package "Data Protection\n<i>Proteção de Dados</i>" as DATA #E8F5E9
  package "Secrets Management\n<i>Gestão de Segredos</i>" as SEC #FCE4EC
  package "Audit & Compliance\n<i>Auditoria e Conformidade</i>" as AUD #EDE7F6
  package "Monitoring & Detection\n<i>Monitoramento e Detecção</i>" as MON #FFF8E1
}

NET ..> IAM : <<use>>
IAM ..> DATA : <<use>>
DATA ..> SEC : <<use>>
AUD ..> IAM : <<use>>
MON ..> AUD : <<use>>
MON ..> NET : <<use>>
MON ..> DATA : <<use>>
@enduml
```

### 2.2. Descrição dos Pacotes

| Pacote | Responsabilidade | Serviços AWS | Requisitos Atendidos |
|---|---|---|---|
| Identity & Access | Gerenciar identidades, autenticação e autorização. | IAM, MFA, RBAC | Segurança (LGPD/PCI-DSS), Manutenibilidade |
| Network Security | Controlar tráfego de rede (firewall). | Security Groups, NACLs, WAF | Segurança (PCI-DSS), Disponibilidade |
| Data Protection | Criptografar dados em repouso e em trânsito. | KMS, ACM, S3/RDS/DynamoDB Encryption | Segurança (LGPD/PCI-DSS), Compliance |
| Secrets Management | Proteger credenciais e chaves de gateways de pagamento. | Secrets Manager, Parameter Store | Segurança (PCI-DSS), Manutenibilidade |
| Audit & Compliance | Rastrear ações e garantir conformidade. | CloudTrail, AWS Config | Segurança (LGPD/PCI-DSS), Compliance |
| Monitoring & Detection | Detectar fraude, anomalias e ameaças. | CloudWatch, GuardDuty, Security Hub | Manutenibilidade, Disponibilidade |

### 2.3. Matriz de Rastreamento

| Requisito (Doc. Suplementar) | Pacote Responsável | Serviço AWS | Controle |
|---|---|---|---|
| Criptografia em repouso (AES-256) | Data Protection | KMS, RDS, S3, DynamoDB | SSE-KMS, RDS Encryption |
| Criptografia em trânsito (TLS 1.3) | Data Protection | ACM, ALB, API Gateway | Certificados SSL |
| Autenticação MFA para admins | Identity & Access | IAM | MFA obrigatório |
| Autorização RBAC | Identity & Access | IAM Groups, Policies | Roles granulares |
| Isolamento de credenciais de pagamento | Secrets Management | Secrets Manager | Rotação automática |
| Auditoria de acessos e transações | Audit & Compliance | CloudTrail | Logs imutáveis |
| Detecção de fraude e anomalias | Monitoring & Detection | GuardDuty, CloudWatch | Alarmes, ML |
| Conformidade LGPD / PCI-DSS | Audit & Compliance | AWS Config | Config Rules |

---

## 3. ESPECIFICAÇÃO DOS PACOTES

### 3.1. PACOTE: IDENTITY & ACCESS

#### 3.1.1. Responsabilidade

Gerenciar identidades (humanos e serviços), autenticação, autorização e permissões de acesso a todos os recursos da plataforma de e-commerce na AWS.

#### 3.1.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| IAM Users | Usuários humanos (admins, operadores, suporte, financeiro). | IAM |
| IAM Groups | Agrupamento de usuários por função (RBAC). | IAM Groups |
| IAM Roles | Identidades para serviços (EC2, Lambda, RDS). | IAM Roles |
| IAM Policies | Permissões granulares (JSON). | IAM Policies |
| MFA | Autenticação multifator. | IAM MFA |
| RBAC | Controle baseado em papéis. | IAM Groups + Policies |

#### 3.1.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Identity & Access
skinparam classAttributeIconSize 0
hide circle

class IAMUser {
  -username : String
  -email : String
  -mfaEnabled : Boolean
  -groups : List<Group>
  +authenticate() : Token
  +enableMFA() : void
}
class IAMGroup {
  -name : String
  -policies : List<Policy>
  +addUser(user : IAMUser) : void
  +attachPolicy(policy : Policy) : void
}
class IAMRole {
  -name : String
  -trustPolicy : JSON
  -permissions : List<Policy>
  +assumeRole(service : Service) : Credentials
}
class IAMPolicy {
  -name : String
  -document : JSON
  -effect : AllowDeny
  +validate() : Boolean
}
class MFADevice {
  -type : VirtualHardware
  -serialNumber : String
  +generateCode() : String
  +validateCode(code : String) : Boolean
}

IAMUser "1" --> "*" IAMGroup : pertence
IAMGroup "1" --> "*" IAMPolicy : possui
IAMRole "1" --> "*" IAMPolicy : possui
IAMUser "1" --> "0..1" MFADevice : usa
@enduml
```

#### 3.1.4. Roles e Permissões (E-commerce)

| Role | Tipo | Serviços Acessados | Permissões | Justificativa |
|---|---|---|---|---|
| Admin-Role | Humano | Todos | `*:*` (com MFA) | Emergências e gestão da plataforma. |
| DevOps-Role | Humano | EC2, RDS, S3, CodePipeline | Deploy, operação | CI/CD e operações. |
| Financeiro-Role | Humano | Payment Gateway, S3 (notas fiscais) | Somente leitura + emissão de NF-e | Conciliação financeira. |
| Auditor-Role | Humano | CloudTrail, Config | Somente leitura | Auditoria e compliance. |
| EC2-API-Role | Serviço | S3, Secrets, DynamoDB, RDS | Get/Put específicos | API de e-commerce (produtos, pedidos). |
| Lambda-Checkout-Role | Serviço | DynamoDB, SQS, Payment Gateway | Put/Write | Processamento de checkout e pagamento. |
| RDS-Role | Serviço | KMS | Encrypt/Decrypt | Criptografia de dados de pedidos e clientes. |

#### 3.1.5. Política IAM (Exemplo — EC2-API-Role)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::ecommerce-product-images/*"
    },
    {
      "Sid": "SecretsAccess",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds-credentials-*"
    },
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/carrinho"
    }
  ]
}
```

#### 3.1.6. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Credenciais hardcoded | Usar IAM Roles para serviços. |
| Permissões excessivas | Aplicar princípio de menor privilégio. |
| Acesso não autorizado ao painel financeiro | MFA obrigatório para admins e financeiro. |
| Rotação de credenciais | Rotação automática via Secrets Manager. |

---

### 3.2. PACOTE: NETWORK SECURITY

#### 3.2.1. Responsabilidade

Controlar e filtrar o tráfego de rede entre as camadas da aplicação (loja virtual, API de checkout, banco de dados), garantindo isolamento e proteção contra acessos não autorizados e ataques automatizados (bots, scraping, DDoS).

#### 3.2.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| Security Groups | Firewall de instâncias (stateful). | VPC |
| NACLs | Firewall de sub-redes (stateless). | VPC |
| WAF | Firewall de aplicação (L7). | WAF |
| VPC Flow Logs | Logs de tráfego de rede. | VPC |
| Private Subnets | Sub-redes sem acesso à Internet. | VPC |

#### 3.2.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Network Security
skinparam classAttributeIconSize 0
hide circle

class SecurityGroup {
  -name : String
  -vpcId : String
  -inboundRules : List<Rule>
  -outboundRules : List<Rule>
  +addInboundRule(rule : Rule) : void
  +addOutboundRule(rule : Rule) : void
}
class NACL {
  -name : String
  -subnetId : String
  -rules : List<NACLRule>
  +addRule(rule : NACLRule) : void
}
class Rule {
  -protocol : TCPUDPICMP
  -portRange : String
  -source : String
  -action : AllowDeny
}
class WAFRule {
  -name : String
  -type : SQLiXSSRateLimitBot
  -action : BlockAllowCount
}
class FlowLog {
  -logGroup : String
  -trafficType : ALLACCEPTREJECT
  +enable() : void
}
class NACLRule

SecurityGroup "1" --> "*" Rule : contém
NACL "1" --> "*" NACLRule : contém
SecurityGroup "1" --> "0..1" FlowLog : monitora
@enduml
```

#### 3.2.4. Matriz de Security Groups (E-commerce)

| Security Group | Regra de Entrada | Origem | Regra de Saída | Destino | Justificativa |
|---|---|---|---|---|---|
| SG-ALB | 80, 443 | 0.0.0.0/0 | 8000 | SG-EC2-API | Exposição pública da loja via HTTPS. |
| SG-EC2-API | 8000 | SG-ALB | 5432 | SG-RDS | API acessada apenas pelo ALB. |
| | | | 443 | VPC Endpoints | Acesso a DynamoDB, S3, Secrets, Payment Gateway. |
| SG-RDS | 5432 | SG-EC2-API | - | - | Banco acessível apenas pela API. |
| SG-Lambda-Checkout | - | - | 443 | VPC Endpoints / Payment Gateway | Checkout acessa gateway de pagamento via endpoint. |

#### 3.2.5. Matriz de NACLs (E-commerce)

| NACL | Regra | Protocolo | Porta | Origem/Destino | Ação |
|---|---|---|---|---|---|
| NACL-Public | 100 | TCP | 80, 443 | 0.0.0.0/0 | Allow |
| | 200 | TCP | 1024-65535 | 0.0.0.0/0 | Allow (efêmeras) |
| | * | All | All | 0.0.0.0/0 | Deny |
| NACL-Private | 100 | TCP | 5432 | 10.0.1.0/24 | Allow |
| | 200 | TCP | 8000 | 10.0.1.0/24 | Allow |
| | * | All | All | 0.0.0.0/0 | Deny |

#### 3.2.6. WAF Rules (E-commerce)

| Regra | Tipo | Ação | Justificativa |
|---|---|---|---|
| SQLi Protection | SQL Injection | Block | Proteger API de produtos e pedidos. |
| XSS Protection | Cross-Site Scripting | Block | Proteger vitrine e área do cliente. |
| Rate Limiting | Rate-based | Block (1000 req/5min) | Evitar DDoS e abuso no checkout. |
| Bot Control | Bot Detection | Block/Challenge | Evitar scraping de preços e compra automatizada (sneaker bots). |
| Geo-blocking | Geolocation | Allow (Brasil) | Reduzir fraude internacional em cartões. |

#### 3.2.7. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Security Groups permissivos | Revisão periódica das regras. |
| Portas expostas | Usar apenas portas necessárias. |
| Ataques DDoS em datas de pico (Black Friday) | WAF + Shield Standard + Auto Scaling. |
| Tráfego não monitorado | VPC Flow Logs habilitados. |

---

### 3.3. PACOTE: DATA PROTECTION

#### 3.3.1. Responsabilidade

Garantir a criptografia de dados em repouso e em trânsito, além de políticas de backup e recuperação, assegurando conformidade com a LGPD e PCI-DSS.

#### 3.3.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| KMS Keys | Chaves de criptografia gerenciadas. | KMS |
| S3 Encryption | Criptografia de objetos (imagens, notas fiscais). | S3 + KMS |
| RDS Encryption | Criptografia de banco relacional (clientes, pedidos). | RDS + KMS |
| DynamoDB Encryption | Criptografia de tabelas NoSQL (carrinho, sessão). | DynamoDB + KMS |
| TLS/ACM | Certificados SSL/TLS. | ACM |
| Backup Policies | Políticas de backup e retenção. | AWS Backup |

#### 3.3.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Data Protection
skinparam classAttributeIconSize 0
hide circle

class KMSKey {
  -keyId : String
  -alias : String
  -rotationEnabled : Boolean
  -keyPolicy : JSON
  +encrypt(data : Bytes) : Bytes
  +decrypt(data : Bytes) : Bytes
  +rotate() : void
}
class EncryptionConfig {
  -service : String
  -type : SSEKMSSSES3
  -kmsKey : KMSKey
  +apply() : void
}
class TLSCertificate {
  -domain : String
  -issuer : ACM
  -expirationDate : Date
  +validate() : Boolean
  +renew() : void
}
class BackupPolicy {
  -frequency : DailyWeekly
  -retentionDays : Integer
  -targetServices : List<String>
  +execute() : void
}

EncryptionConfig "1" --> "1" KMSKey : usa
BackupPolicy "1" --> "*" EncryptionConfig : protege
@enduml
```

#### 3.3.4. Matriz de Criptografia (E-commerce)

| Serviço | Criptografia em Repouso | Criptografia em Trânsito | Chave | Justificativa |
|---|---|---|---|---|
| RDS | AES-256 | TLS 1.3 | KMS CMK | LGPD: dados de clientes e vendedores. |
| S3 | SSE-KMS | TLS 1.3 | KMS CMK | LGPD: notas fiscais e comprovantes. |
| DynamoDB | AES-256 | TLS 1.3 | AWS Managed | Carrinho de compras e sessão. |
| Secrets Manager | AES-256 | TLS 1.3 | AWS Managed | Credenciais e chaves de gateway de pagamento. |
| ALB | - | TLS 1.3 | ACM Certificate | Loja e API pública. |
| EBS (EC2) | AES-256 | - | KMS CMK | Disco da API. |

> **Nota PCI-DSS:** o e-commerce **não armazena** número completo de cartão de crédito (PAN) em seus próprios bancos — o processamento de pagamento é tokenizado via gateway externo certificado PCI-DSS Nível 1, reduzindo o escopo de conformidade da plataforma.

#### 3.3.5. Políticas de Backup (E-commerce)

| Serviço | Frequência | Retenção | RPO | RTO |
|---|---|---|---|---|
| RDS | Diário (snapshot) | 30 dias | 15 min (PITR) | 1 hora |
| DynamoDB | Contínuo (PITR) | 35 dias | 5 min | 30 min |
| S3 | Versionamento | 90 dias | 0 | 0 |
| EBS | Diário (snapshot) | 7 dias | 24 horas | 2 horas |

#### 3.3.6. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Chaves comprometidas | Rotação automática (90 dias). |
| Dados de cliente não criptografados | Criptografia obrigatória em todos os serviços. |
| Backup não testado antes de eventos de pico | Testes de recuperação trimestrais. |
| Perda de dados de pedidos | PITR + Multi-AZ. |

---

### 3.4. PACOTE: SECRETS MANAGEMENT

#### 3.4.1. Responsabilidade

Proteger credenciais, chaves de API de gateways de pagamento, tokens e outros segredos, garantindo que não sejam expostos em código ou configurações.

#### 3.4.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| Secrets Manager | Armazenamento de segredos com rotação. | Secrets Manager |
| Parameter Store | Armazenamento de configurações. | Systems Manager |
| Rotation Policies | Políticas de rotação automática. | Lambda + Secrets Manager |
| IAM Policies for Secrets | Controle de acesso aos segredos. | IAM |

#### 3.4.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Secrets Management
skinparam classAttributeIconSize 0
hide circle

class Secret {
  -name : String
  -rotationEnabled : Boolean
  -rotationLambda : String
  -value : String
  +getValue() : String
  +rotate() : void
}
class Parameter {
  -name : String
  -value : String
  -type : StringListSecureString
  +getValue() : String
}
class RotationPolicy {
  -frequency : Days
  -lambdaArn : String
  +execute() : void
}
class AccessPolicy {
  -secretArn : String
  -principals : List<String>
  -actions : List<String>
  +validate() : Boolean
}

Secret "1" --> "0..1" RotationPolicy : usa
Secret "1" --> "*" AccessPolicy : protegido por
@enduml
```

#### 3.4.4. Segredos Gerenciados (E-commerce)

| Segredo | Serviço | Rotação | Acesso | Justificativa |
|---|---|---|---|---|
| rds-credentials | RDS PostgreSQL | 90 dias | EC2-API-Role | Evitar hardcoded. |
| payment-gateway-api-key | Gateway de Pagamento | 60 dias | Lambda-Checkout-Role | Chave de integração de pagamento (alto risco). |
| jwt-secret | API de Autenticação | 90 dias | EC2-API-Role | Tokens de sessão do cliente. |
| nfe-certificate | Emissor de NF-e | 365 dias (certificado A1) | Lambda-Faturamento-Role | Assinatura digital de nota fiscal. |
| s3-access | S3 (imagens/produtos) | 90 dias | EC2-API-Role | Acesso a buckets. |

#### 3.4.5. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Chave de gateway de pagamento em código | Usar Secrets Manager. |
| Rotação manual | Rotação automática via Lambda. |
| Acesso não autorizado a segredos financeiros | IAM Policies restritivas + MFA. |
| Vazamento de segredos | Auditoria via CloudTrail. |

---

### 3.5. PACOTE: AUDIT & COMPLIANCE

#### 3.5.1. Responsabilidade

Rastrear todas as ações realizadas na conta AWS, garantir conformidade com regulamentações (LGPD, PCI-DSS) e fornecer evidências para auditorias, incluindo transações financeiras.

#### 3.5.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| CloudTrail | Registro de todas as ações na conta. | CloudTrail |
| AWS Config | Avaliação de conformidade. | AWS Config |
| Config Rules | Regras de conformidade. | AWS Config |
| Compliance Reports | Relatórios de conformidade. | AWS Artifact |
| S3 Log Bucket | Armazenamento de logs. | S3 |

#### 3.5.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Audit & Compliance
skinparam classAttributeIconSize 0
hide circle

class Trail {
  -name : String
  -s3Bucket : String
  -regions : List<String>
  -logFileValidation : Boolean
  +enable() : void
  +getEvents(filter : Filter) : List<Event>
}
class ConfigRule {
  -name : String
  -source : AWSManaged
  -compliance : CompliantNonCompliant
  +evaluate() : Compliance
}
class ComplianceReport {
  -framework : LGPDPCIDSS
  -period : DateRange
  -findings : List<Finding>
  +generate() : Report
}
class AuditEvent {
  -eventId : String
  -eventTime : DateTime
  -userIdentity : String
  -eventName : String
  -resourceArn : String
}

Trail "1" --> "*" AuditEvent : registra
ConfigRule "1" --> "*" ComplianceReport : gera
@enduml
```

#### 3.5.4. Config Rules (E-commerce)

| Regra | Descrição | Serviço Alvo | Conformidade |
|---|---|---|---|
| encrypted-volumes | Volumes EBS criptografados. | EC2 | LGPD |
| rds-storage-encrypted | RDS criptografado. | RDS | LGPD / PCI-DSS |
| s3-bucket-ssl-requests-only | S3 exige HTTPS. | S3 | LGPD |
| iam-password-policy | Política de senhas forte. | IAM | PCI-DSS |
| mfa-enabled-for-iam-console-access | MFA para admins. | IAM | PCI-DSS |
| cloudtrail-enabled | CloudTrail ativo. | CloudTrail | Auditoria |
| no-full-access-to-payment-secrets | Bloqueia policies com acesso irrestrito a segredos de pagamento. | Secrets Manager | PCI-DSS |

#### 3.5.5. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Logs não imutáveis | S3 com Object Lock. |
| Auditoria incompleta de transações | CloudTrail em todas as regiões. |
| Conformidade PCI-DSS não verificada | AWS Config Rules + relatório trimestral. |
| Perda de logs | Replicação para outra região. |

---

### 3.6. PACOTE: MONITORING & DETECTION

#### 3.6.1. Responsabilidade

Monitorar a saúde dos recursos, detectar fraude, anomalias e ameaças (especialmente durante picos de tráfego como Black Friday), e emitir alertas para a equipe de operações e antifraude.

#### 3.6.2. Elementos do Pacote

| Elemento | Descrição | Serviço AWS |
|---|---|---|
| CloudWatch | Métricas, logs e alarmes. | CloudWatch |
| GuardDuty | Detecção de ameaças com ML. | GuardDuty |
| Security Hub | Visão centralizada de segurança. | Security Hub |
| Alarms | Alarmes baseados em métricas. | CloudWatch |
| SNS Notifications | Notificações de incidentes. | SNS |

#### 3.6.3. Diagrama de Classes de Análise

```plantuml
@startuml
title Classes de Análise - Monitoring & Detection
skinparam classAttributeIconSize 0
hide circle

class Metric {
  -namespace : String
  -name : String
  -value : Double
  -unit : String
  -timestamp : DateTime
  +publish() : void
}
class Alarm {
  -name : String
  -metric : Metric
  -threshold : Double
  -comparison : GreaterThanLessThan
  -actions : List<Action>
  +evaluate() : State
}
class Dashboard {
  -name : String
  -widgets : List<Widget>
  +addWidget(widget : Widget) : void
}
class Threat {
  -type : String
  -severity : LowMediumHigh
  -resource : String
  -detectedAt : DateTime
}
class Notification {
  -topic : String
  -recipients : List<String>
  -channel : EmailSMSSlack
  +send() : void
}

Alarm "1" --> "*" Metric : monitora
Alarm "1" --> "*" Notification : dispara
Dashboard "1" --> "*" Metric : exibe
@enduml
```

#### 3.6.4. Alarmes Configurados (E-commerce)

| Alarme | Métrica | Threshold | Ação | Justificativa |
|---|---|---|---|---|
| CPU-High | CPUUtilization | > 80% (5 min) | Auto Scaling + SNS | Escalar API durante picos de vendas. |
| Latency-High | TargetResponseTime | > 80ms (5 min) | SNS | SLA de latência no checkout. |
| RDS-Storage-Low | FreeStorageSpace | < 10 GB | SNS | Evitar falha no banco de pedidos. |
| Checkout-Errors | Errors (Lambda-Checkout) | > 10 (5 min) | SNS | Falha no processamento de pagamento. |
| Fraud-Score-High | Payment Gateway Webhook | Score > limite | SNS + bloqueio automático | Suspeita de fraude em cartão. |
| Unauthorized-API-Calls | CloudTrail | > 5 (5 min) | SNS + GuardDuty | Detecção de ataque à API. |
| Root-Account-Usage | CloudTrail | > 0 | SNS | Alerta crítico. |

#### 3.6.5. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Alarmes não configurados para picos sazonais | Cobertura de 100% dos recursos críticos. |
| Notificações ignoradas | Escalonamento para múltiplos canais (e-mail, SMS, Slack). |
| Detecção tardia de fraude | GuardDuty + Security Hub + score de fraude do gateway. |
| Falsos positivos em Black Friday | Ajuste fino de thresholds sazonais. |

---

## 4. DIAGRAMA DE DEPENDÊNCIAS ENTRE PACOTES

```plantuml
@startuml
title Dependências entre Pacotes de Segurança
skinparam packageStyle rectangle
skinparam shadowing false
skinparam defaultTextAlignment center

package "IAM\nIdentity & Access" as IAM #E3F2FD
package "NetSec\nNetwork Security" as NET #FFF3E0
package "DataProt\nData Protection" as DATA #E8F5E9
package "Secrets\nSecrets Management" as SEC #FCE4EC
package "Audit\nAudit & Compliance" as AUD #EDE7F6
package "Monitor\nMonitoring & Detection" as MON #FFF8E1

IAM --> DATA : IAM define quem\nacessa chaves KMS
NET --> IAM : Security Groups\nusam roles IAM
DATA --> SEC : Chaves gerenciadas\nno Secrets Manager
AUD --> IAM : CloudTrail registra\nações IAM
MON --> AUD : CloudWatch consome\nlogs CloudTrail
MON --> NET : GuardDuty analisa\nVPC Flow Logs
MON --> DATA : Detecta fraude e\nanomalias de acesso
@enduml
```

| De | Para | Motivo |
|---|---|---|
| Identity & Access | Data Protection | IAM define quem pode acessar chaves KMS. |
| Network Security | Identity & Access | Security Groups usam roles IAM. |
| Data Protection | Secrets Management | Chaves de integração de pagamento são gerenciadas no Secrets Manager. |
| Audit & Compliance | Identity & Access | CloudTrail registra ações de usuários IAM. |
| Monitoring & Detection | Audit & Compliance | CloudWatch consome logs do CloudTrail. |
| Monitoring & Detection | Network Security | GuardDuty analisa VPC Flow Logs. |
| Monitoring & Detection | Data Protection | Detecta fraude e anomalias de acesso a dados de clientes/pedidos. |

---

## 5. MATRIZ DE RASTREAMENTO COMPLETA

| Requisito (Doc. Suplementar) | Caso de Uso (Semana 3) | Pacote | Serviço AWS | Controle |
|---|---|---|---|---|
| Criptografia em repouso | UC-ARQ-007 | Data Protection | KMS, RDS, S3, DynamoDB | SSE-KMS |
| Criptografia em trânsito | UC-ARQ-004 | Data Protection | ACM, ALB | TLS 1.3 |
| MFA para admins e financeiro | UC-ARQ-002 | Identity & Access | IAM | MFA |
| RBAC | UC-ARQ-002 | Identity & Access | IAM Groups | Roles |
| Isolamento de credenciais de pagamento | UC-ARQ-005 | Secrets Management | Secrets Manager | Rotação automática |
| Tokenização de dados de cartão (PCI-DSS) | UC-ARQ-006 | Data Protection / Secrets Management | Payment Gateway externo | Escopo PCI reduzido |
| Auditoria de acessos e transações | UC-ARQ-003 | Audit & Compliance | CloudTrail | Logs imutáveis |
| Detecção de fraude e anomalias | UC-ARQ-008 | Monitoring & Detection | GuardDuty, CloudWatch | Alarmes, ML, score de fraude |
| Conformidade LGPD / PCI-DSS | UC-ARQ-009 | Audit & Compliance | AWS Config | Config Rules |
| Proteção contra bots e scraping | UC-ARQ-010 | Network Security | WAF | Bot Control |

---

*Documento gerado com base no modelo de referência SwiftTrack IoT, adaptado para o domínio de e-commerce.*
