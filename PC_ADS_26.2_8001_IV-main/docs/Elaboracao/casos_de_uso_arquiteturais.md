| id    | casos_de_uso_arquiteturais |
|-------|------------------------------|
| title | Casos de Uso Arquiteturais   |

# Casos de Uso Arquiteturais

## Plataforma de E-commerce com Arquitetura de Nuvem Híbrida e Logística Last-Mile Inteligente

*Modelo de Casos de Uso Arquiteturais — Projeto de Cloud*

| Informações | |
|---|---|
| **Projeto** | Plataforma de E-commerce com Logística Last-Mile Inteligente |
| **Documento** | Modelo de Casos de Uso Arquiteturais |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Em Desenvolvimento |
| **Responsável** | [Grupo E-commerce] |
| **Disciplina** | Projeto de Cloud |

---

## 1. Introdução

### 1.1. Propósito

Este documento descreve os Casos de Uso Arquiteturais para a infraestrutura em nuvem AWS da plataforma de e-commerce. Os casos de uso arquiteturais focam em requisitos de infraestrutura, segurança, operações e governança, diferentemente dos casos de uso funcionais, que descrevem interações de usuários finais (compradores, lojistas) com o sistema.

### 1.2. Escopo

Os casos de uso arquiteturais abrangem a configuração, operação e manutenção da infraestrutura AWS, incluindo:

- Rede (VPC, sub-redes, rotas, endpoints)
- Segurança (Security Groups, NACLs, IAM)
- Conectividade entre camadas (ALB, EC2, RDS, Lambda)
- Integração com serviços gerenciados (DynamoDB, S3, Secrets Manager)
- Automação e deploy (CI/CD)

### 1.3. Referências

- Documento de Visão — Plataforma de E-commerce (v1.0)
- Documento de Requisitos Suplementares — Plataforma de E-commerce (v1.0)
- AWS Well-Architected Framework
- Amazon VPC Documentation

---

## 2. Visão Geral dos Casos de Uso

### 2.1. Atores

| Ator | Descrição | Responsabilidades |
|---|---|---|
| Administrador de Infraestrutura | Profissional responsável por configurar e gerenciar a infraestrutura AWS. | Criar VPC, sub-redes, security groups, endpoints. |
| Engenheiro de DevOps | Profissional responsável por automação e CI/CD. | Configurar pipelines, deploys, rollbacks. |
| Sistema AWS | Serviços gerenciados da AWS (DynamoDB, S3, etc.). | Prover serviços, endpoints, logs. |
| Arquiteto de Segurança | Profissional responsável por políticas de segurança e compliance. | Definir políticas IAM, criptografia, auditoria. |

### 2.2. Diagrama de Casos de Uso

![Diagrama de Casos de Uso Arquiteturais](casos_uso_diagrama.png)

---

## 3. Especificação dos Casos de Uso

### UC-ARQ-001: Configurar VPC e Rede do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-001 |
| **Nome** | Configurar VPC e Rede do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Administrador de Infraestrutura |
| **Ator Secundário** | Sistema AWS |
| **Pré-condição** | 1. Conta AWS ativa.<br>2. Permissões IAM para criar VPC, sub-redes, IGW, NAT Gateway, Route Tables. |
| **Pós-condição** | 1. VPC criada com CIDR 10.0.0.0/16.<br>2. 4 sub-redes criadas (2 públicas, 2 privadas) em 2 AZs.<br>3. Internet Gateway anexado.<br>4. NAT Gateways configurados.<br>5. Route Tables configuradas. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Administrador acessa o Console AWS. |
| 2 | Navega até o serviço VPC. |
| 3 | Cria VPC com CIDR 10.0.0.0/16 e habilita DNS hostnames. |
| 4 | Cria 2 sub-redes públicas (uma por AZ) com CIDR 10.0.1.0/24 e 10.0.2.0/24, para o Load Balancer. |
| 5 | Cria 2 sub-redes privadas (uma por AZ) com CIDR 10.0.3.0/24 e 10.0.4.0/24, para EC2 (Django) e RDS. |
| 6 | Cria e anexa Internet Gateway à VPC. |
| 7 | Cria NAT Gateways (um por AZ) nas sub-redes públicas. |
| 8 | Configura Route Table pública: 10.0.0.0/16 → local, 0.0.0.0/0 → IGW. |
| 9 | Configura Route Table privada: 10.0.0.0/16 → local, 0.0.0.0/0 → NAT Gateway. |
| 10 | Associa sub-redes públicas à Route Table pública. |
| 11 | Associa sub-redes privadas à Route Table privada. |
| 12 | Valida conectividade: instância pública → Internet, instância privada → NAT. |

**Fluxos Alternativos**

| Alt. | Descrição |
|---|---|
| Alt 1 | CIDR da VPC conflita com outra VPC ou rede on-premises (erro de criação). |
| Alt 2 | Limite de VPCs por região é atingido (5 VPCs por região). |
| Alt 3 | Permissões IAM insuficientes (erro de autorização). |
| Alt 4 | NAT Gateway falha (instância privada perde acesso à Internet). |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Desempenho | VPC criada e configurada em < 15 min. |
| Disponibilidade | Multi-AZ com 2 AZs (redundância). |
| Segurança | Sub-redes privadas sem rota direta para Internet. |
| Custo | NAT Gateway: ~US$ 0,045/hora por AZ (~US$ 64/mês para 2 AZs). |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Endereçamento conflitante | Planejar CIDR com folga (10.0.0.0/16). |
| Custo elevado do NAT Gateway | Avaliar uso de NAT Instance (mais barato, menos gerenciado). |
| Erro de roteamento | Testar conectividade com ping ou traceroute. |

---

### UC-ARQ-002: Configurar Segurança de Rede do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-002 |
| **Nome** | Configurar Segurança de Rede do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Administrador de Infraestrutura |
| **Ator Secundário** | Arquiteto de Segurança, Sistema AWS |
| **Pré-condição** | 1. VPC e sub-redes criadas (UC-ARQ-001).<br>2. IAM configurado. |
| **Pós-condição** | 1. Security Groups configurados para cada camada.<br>2. NACLs configuradas.<br>3. IAM roles definidas para serviços. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Administrador acessa o Console AWS. |
| 2 | Navega até Security Groups. |
| 3 | Cria SG-ALB com regras de entrada: portas 80, 443 (0.0.0.0/0). |
| 4 | Cria SG-EC2-Django com regras de entrada: porta 8000 (origem: SG-ALB). |
| 5 | Cria SG-RDS com regras de entrada: porta 5432 (origem: SG-EC2-Django). |
| 6 | Cria SG-Lambda com regras de saída: DynamoDB, S3, Secrets Manager. |
| 7 | Cria NACLs para sub-redes públicas e privadas (camada extra de segurança). |
| 8 | Define IAM roles para EC2, Lambda e RDS. |

**Fluxos Alternativos**

| Alt. | Descrição |
|---|---|
| Alt 1 | Porta 8000 exposta acidentalmente → revisão das regras. |
| Alt 2 | IAM role com permissões excessivas → aplicar princípio de menor privilégio. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Segurança | Princípio de menor privilégio implementado. |
| Segurança | Criptografia em trânsito (TLS 1.3). |
| Compliance | Conformidade com a LGPD. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Security Groups permissivos | Revisão periódica das regras. |
| Acesso não autorizado | MFA obrigatório para administradores. |

---

### UC-ARQ-003: Configurar VPC Endpoints do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-003 |
| **Nome** | Configurar VPC Endpoints do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Administrador de Infraestrutura |
| **Ator Secundário** | Sistema AWS (DynamoDB, S3, Secrets Manager) |
| **Pré-condição** | 1. VPC e sub-redes privadas criadas (UC-ARQ-001).<br>2. IAM configurado. |
| **Pós-condição** | 1. DynamoDB Gateway Endpoint configurado.<br>2. S3 Interface Endpoint configurado.<br>3. Secrets Manager Interface Endpoint configurado.<br>4. Políticas de endpoint restritivas aplicadas. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Administrador acessa o Console AWS. |
| 2 | Navega até VPC Endpoints. |
| 3 | Cria Gateway Endpoint para DynamoDB (tipo: Gateway), usado para os eventos de rastreamento logístico. |
| 4 | Associa às sub-redes privadas (10.0.3.0/24, 10.0.4.0/24). |
| 5 | Atualiza Route Table privada com rota para o DynamoDB. |
| 6 | Cria Interface Endpoint para S3 (tipo: Interface), usado para imagens de produtos e canhotos de entrega. |
| 7 | Cria Interface Endpoint para Secrets Manager (tipo: Interface). |
| 8 | Aplica políticas de endpoint para restringir acesso a buckets/segredos específicos. |
| 9 | Valida conectividade: EC2 → DynamoDB, Lambda → S3. |

**Fluxos Alternativos**

| Alt. | Descrição |
|---|---|
| Alt 1 | Serviço não suporta Gateway Endpoint (ex.: Secrets Manager) → usar Interface Endpoint. |
| Alt 2 | Política de endpoint bloqueia acesso → revisar e ajustar. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Segurança | Tráfego não sai da VPC. |
| Custo | Interface Endpoints: US$ 0,01/hora cada (~US$ 14/mês). |
| Desempenho | Latência reduzida em comparação ao acesso via Internet. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Custo elevado | Usar Gateway Endpoint para serviços suportados (DynamoDB, S3). |
| Políticas restritivas | Testar políticas com usuários específicos antes de aplicar. |

---

### UC-ARQ-004: Configurar Conectividade entre Camadas do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-004 |
| **Nome** | Configurar Conectividade entre Camadas do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Administrador de Infraestrutura |
| **Ator Secundário** | Engenheiro de DevOps |
| **Pré-condição** | 1. VPC e sub-redes criadas (UC-ARQ-001).<br>2. Security Groups configurados (UC-ARQ-002).<br>3. VPC Endpoints configurados (UC-ARQ-003). |
| **Pós-condição** | 1. Application Load Balancer (ALB) configurado.<br>2. EC2 (portal de e-commerce) configurada e comunicando com o ALB.<br>3. RDS acessível apenas pela EC2.<br>4. Lambda acessando DynamoDB e S3 via endpoints, para os eventos de rastreamento logístico. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Administrador acessa o Console AWS. |
| 2 | Configura Application Load Balancer (ALB) na sub-rede pública. |
| 3 | Configura listener: porta 443 (HTTPS) → porta 8000 (EC2). |
| 4 | Configura Target Group com EC2 do portal de e-commerce (porta 8000). |
| 5 | Cria Launch Template para a EC2 com User Data (Gunicorn, Nginx, Django). |
| 6 | Configura Auto Scaling Group com mínimo de 2 instâncias (Multi-AZ). |
| 7 | Configura RDS PostgreSQL em Multi-AZ com Security Group SG-RDS. |
| 8 | Configura API Gateway + Lambda, com Lambda associada à VPC (sub-redes privadas) e aos VPC Endpoints, para receber os eventos logísticos. |
| 9 | Testa fluxo completo: ALB → EC2 → RDS (pedidos/catálogo), API Gateway → Lambda → DynamoDB (rastreamento). |

**Fluxos Alternativos**

| Alt. | Descrição |
|---|---|
| Alt 1 | EC2 não alcança o RDS (erro de Security Group) → revisar regras. |
| Alt 2 | Lambda não acessa o DynamoDB (erro de endpoint) → revisar IAM. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Disponibilidade | 99,95% (Multi-AZ + ALB + Auto Scaling). |
| Desempenho | Latência < 80ms para a ingestão de eventos logísticos. |
| Segurança | Comunicação entre camadas via rede privada. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| ALB como ponto único de falha | ALB é um serviço gerenciado e altamente disponível. |
| Auto Scaling mal configurado | Definir alarmes no CloudWatch para o escalonamento. |

---

### UC-ARQ-005: Configurar Monitoramento do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-005 |
| **Nome** | Configurar Monitoramento do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Administrador de Infraestrutura |
| **Ator Secundário** | Engenheiro de DevOps |
| **Pré-condição** | 1. VPC e recursos configurados. |
| **Pós-condição** | 1. Dashboards do CloudWatch configurados.<br>2. Alarmes definidos.<br>3. Logs centralizados. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Administrador acessa o Console AWS. |
| 2 | Navega até o CloudWatch. |
| 3 | Cria Dashboard com métricas: CPU, memória, latência, número de pedidos por minuto. |
| 4 | Configura alarmes: CPU > 80%, latência de ingestão > 80ms, quedas no volume de pedidos. |
| 5 | Configura CloudWatch Logs para EC2, RDS e Lambda. |
| 6 | Cria Log Groups centralizados. |
| 7 | Define métricas customizadas para a ingestão de eventos de rastreamento logístico. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Observabilidade | 100% de cobertura de logs. |
| Resposta a incidentes | Tempo de resposta < 15 min. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Alarmes mal calibrados (ruído excessivo) | Ajustar limiares com base no histórico de uso. |
| Falta de correlação entre logs | Centralizar logs em Log Groups e usar métricas customizadas. |

---

### UC-ARQ-006: Configurar Pipeline de CI/CD do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-006 |
| **Nome** | Configurar Pipeline de CI/CD do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Engenheiro de DevOps |
| **Ator Secundário** | Sistema AWS (CodePipeline, CodeBuild, CodeDeploy) |
| **Pré-condição** | 1. Código do portal de e-commerce no repositório GitHub.<br>2. EC2 e RDS configurados. |
| **Pós-condição** | 1. Pipeline automatizado funcionando.<br>2. Deploy < 10 minutos.<br>3. Rollback < 5 minutos. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Engenheiro acessa o Console AWS. |
| 2 | Configura o CodePipeline com Source (GitHub), Build (CodeBuild) e Deploy (CodeDeploy). |
| 3 | Configura o CodeBuild com buildspec.yml (instalação de dependências, testes automatizados). |
| 4 | Configura o CodeDeploy com AppSpec.yml (deploy do portal de e-commerce na EC2). |
| 5 | Configura rollback automático em caso de falha. |
| 6 | Testa o pipeline com um commit no branch main. |
| 7 | Configura aprovação manual para o ambiente de produção. |

**Fluxos Alternativos**

| Alt. | Descrição |
|---|---|
| Alt 1 | Build falha → notificação via SNS. |
| Alt 2 | Deploy falha → rollback automático. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Desempenho | Deploy < 10 minutos. |
| Confiabilidade | Rollback < 5 minutos. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Deploy com falha silenciosa | Testes automatizados obrigatórios antes do deploy. |
| Divergência entre ambientes | Uso de Infraestrutura como Código (IaC) para homologação e produção. |

---

### UC-ARQ-007: Definir Políticas de Segurança do E-commerce

| Elemento | Especificação |
|---|---|
| **Identificador** | UC-ARQ-007 |
| **Nome** | Definir Políticas de Segurança do E-commerce |
| **Versão** | 1.0 |
| **Data** | [23/09/2026] |
| **Status** | Aprovado |
| **Ator Principal** | Arquiteto de Segurança |
| **Ator Secundário** | Administrador de Infraestrutura |
| **Pré-condição** | 1. Conta AWS configurada.<br>2. IAM configurado. |
| **Pós-condição** | 1. Políticas IAM definidas.<br>2. Criptografia configurada.<br>3. Conformidade com a LGPD. |

**Fluxo Principal**

| # | Passo |
|---|---|
| 1 | Arquiteto de Segurança define políticas IAM (princípio de menor privilégio). |
| 2 | Configura MFA obrigatório para todos os usuários. |
| 3 | Configura criptografia em repouso: RDS (AES-256), S3 (AES-256), DynamoDB (AES-256). |
| 4 | Configura criptografia em trânsito: TLS 1.3 (ALB), API Gateway. |
| 5 | Configura o Secrets Manager para as credenciais do banco de dados e de gateways de pagamento. |
| 6 | Define políticas de rotação de chaves (a cada 90 dias). |
| 7 | Configura o CloudTrail para auditoria de acessos. |
| 8 | Valida a conformidade com a LGPD, especialmente para dados de clientes e pedidos. |

**Requisitos Não-Funcionais**

| Dimensão | Métrica |
|---|---|
| Segurança | Criptografia AES-256 em repouso. |
| Segurança | TLS 1.3 em trânsito. |
| Compliance | Conformidade com a LGPD. |

**Riscos e Mitigação**

| Risco | Mitigação |
|---|---|
| Chaves comprometidas | Rotação a cada 90 dias. |
| Acesso não autorizado | MFA e auditoria via CloudTrail. |

---

## 4. Matriz de Rastreamento

| Caso de Uso | Requisitos Suplementares | Documento de Visão | Serviços AWS |
|---|---|---|---|
| UC-ARQ-001 | Confiabilidade (Multi-AZ), Custo | Infraestrutura Híbrida | VPC, Sub-redes, IGW, NAT, Route Tables |
| UC-ARQ-002 | Segurança (LGPD), Manutenibilidade | Segurança e Privacidade | Security Groups, NACLs, IAM |
| UC-ARQ-003 | Segurança (LGPD), Custo | Arquitetura Híbrida | VPC Endpoints (DynamoDB, S3, Secrets Manager) |
| UC-ARQ-004 | Desempenho (Latência), Disponibilidade (99,95%) | Portal de E-commerce + Ingestão | ALB, EC2, RDS, API Gateway, Lambda |
| UC-ARQ-005 | Manutenibilidade, Disponibilidade | Monitoramento | CloudWatch, Logs, Alarms |
| UC-ARQ-006 | Manutenibilidade (Deploy/Rollback) | Automação | CodePipeline, CodeBuild, CodeDeploy |
| UC-ARQ-007 | Segurança (LGPD), Compliance | Segurança e Privacidade | IAM, KMS, Secrets Manager, CloudTrail |

---

## 5. Aprovações

| Função | Nome | Data | Assinatura |
|---|---|---|---|
| Arquiteto de Soluções | | | |
| Professor Responsável | | | |
| Coordenador do Curso | | | |

---

## 6. Histórico de Versões

| Versão | Data | Autor | Descrição das Alterações |
|---|---|---|---|
| 0.1 | [23/09/2026] | [Grupo E-commerce] | Criação inicial do documento. |
| 1.0 | [23/09/2026] | [Grupo E-commerce] | Versão completa com todos os casos de uso. |
