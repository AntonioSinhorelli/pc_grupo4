| id    | documento_de_visao       |
|-------|--------------------------|
| title | Documento de Visão       |

# Documento de Visão

## Plataforma de E-commerce com Arquitetura de Nuvem Híbrida e Logística Last-Mile Inteligente

*Elaborado conforme o padrão RUP/UP — Fase de Concepção (Inception)*

---

## 1. Introdução

### 1.1 Propósito

O propósito deste documento é reunir, consolidar e comunicar a visão do projeto de uma plataforma de e-commerce com foco no processo de entrega "last-mile" (última milha), estabelecendo as necessidades e características de alto nível do sistema sob a ótica dos principais stakeholders. Este Documento de Visão serve como base para o entendimento comum entre a equipe de desenvolvimento, os gestores acadêmicos e demais interessados a respeito do problema a ser resolvido, das restrições do projeto e dos atributos de qualidade que a solução deverá atender, orientando as decisões técnicas e arquiteturais tomadas ao longo do ciclo de vida do trabalho.

### 1.2 Escopo

O escopo deste projeto de cloud engloba os seguintes componentes e serviços AWS:

1. **Portal de E-commerce e API Transacional**: desenvolvido em Python com Django, para catálogo de produtos, carrinho de compras, gestão de pedidos, pagamentos e emissão de relatórios consolidados.
2. **Pipeline Serverless de Ingestão de Eventos Logísticos**: endpoint HTTP leve para receber atualizações de status de entrega e geolocalização de entregadores de forma assíncrona.
3. **Persistência de Dados Híbrida**: armazenamento relacional para as operações de negócio (pedidos, clientes, catálogo) e NoSQL para o histórico contínuo de rastreamento logístico.
4. **Infraestrutura de Rede e Segurança**: isolamento lógico dos servidores de aplicação e banco de dados, firewall rígido e gerenciamento seguro de variáveis de ambiente e credenciais.
5. **Automação CI/CD**: pipeline de integração e entrega contínua para garantir atualizações automáticas e seguras no ambiente de produção.

Não fazem parte do escopo deste documento o detalhamento de casos de uso, o desenho de interfaces gráficas ou a especificação de testes, que serão tratados em artefatos complementares.

### 1.3 Definições, Acrônimos e Abreviações

| Termo | Definição |
|---|---|
| API (Application Programming Interface) | Interface de Programação de Aplicações; conjunto de rotinas que permite a comunicação entre o portal web/mobile e o núcleo transacional do e-commerce. |
| VPC (Virtual Private Cloud) | Rede virtual isolada logicamente dentro da nuvem AWS, na qual os recursos do projeto (instâncias, bancos de dados, funções) são provisionados de forma segregada e controlada. |
| RDS (Relational Database Service) | Serviço gerenciado de banco de dados relacional da AWS, utilizado para persistir os dados transacionais estruturados do e-commerce (pedidos, clientes, catálogo). |
| NoSQL (Not Only SQL) | Modelo de banco de dados não relacional, utilizado no projeto (via DynamoDB) para armazenar dados semiestruturados de alto volume e alta velocidade de escrita, como eventos de rastreamento logístico. |
| DynamoDB | Banco de dados NoSQL, gerenciado e serverless, da AWS, utilizado para o histórico contínuo de rastreamento de última milha. |
| SLA (Service Level Agreement) | Acordo de Nível de Serviço; conjunto de metas mensuráveis (por exemplo, disponibilidade percentual) que definem o padrão de qualidade esperado da aplicação. |
| SLO (Service Level Objective) | Objetivo de Nível de Serviço; meta interna e específica (por exemplo, latência máxima) que suporta o cumprimento do SLA global. |
| RTO (Recovery Time Objective) | Tempo máximo tolerável para restabelecer a operação do sistema após um incidente de indisponibilidade. |
| RPO (Recovery Point Objective) | Intervalo máximo de dados que a organização aceita perder em caso de falha, medido em tempo desde o último backup ou ponto de recuperação válido. |
| IaC (Infrastructure as Code) | Infraestrutura como Código; prática de provisionar e gerenciar a infraestrutura de nuvem por meio de scripts e templates versionados, em vez de configuração manual. |
| Last-mile | Etapa final do processo logístico, correspondente ao trajeto entre o centro de distribuição e o endereço final do consumidor; historicamente a etapa mais custosa e sujeita a falhas da cadeia de entrega. |
| LGPD | Lei Geral de Proteção de Dados (Lei nº 13.709/2018), legislação brasileira que rege o tratamento de dados pessoais. |

### 1.4 Referências

- AWS Well-Architected Framework (pilares de Excelência Operacional, Segurança, Confiabilidade, Eficiência de Performance, Otimização de Custos e Sustentabilidade).
- Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018).
- Plano de Ensino da disciplina de Cloud Computing / Engenharia de Software.

---

## 2. Posicionamento

### 2.1 Oportunidade de Negócio

O mercado de e-commerce brasileiro convive com desafios estruturais na etapa de "última milha" (last-mile) da cadeia logística, etapa que concentra a maior parcela dos custos de entrega e a maior incidência de falhas percebidas pelo consumidor final. Lojistas e operadores de médio porte frequentemente não possuem capital para investir em infraestrutura física robusta capaz de absorver a volumetria e a oscilação de acessos geradas por picos sazonais de vendas (datas comemorativas, promoções) e pela ingestão contínua de eventos logísticos. Oferecer uma plataforma escalável, hospedada em nuvem, que combine um núcleo transacional robusto com um pipeline de eventos capaz de escalar de forma independente, representa uma oportunidade de capturar um mercado de comércio eletrônico em expansão constante, reduzindo custos operacionais fixos e elevando a confiabilidade da experiência de compra.

### 2.2 Descrição do Problema

| | |
|---|---|
| **O problema de...** | Lentidão sistêmica, ausência de rastreamento em tempo real dos pedidos e quedas do portal de e-commerce durante picos de acesso (promoções e datas sazonais). |
| **Afeta...** | Lojistas, operadores logísticos responsáveis pela entrega e, em última instância, os consumidores finais, que não conseguem acompanhar o status real de seus pedidos. |
| **Cujo impacto é...** | Aumento de chamados no suporte, queda na satisfação do cliente (NPS), perda direta de vendas durante indisponibilidades e exposição a riscos de não conformidade com a LGPD. |
| **Uma solução bem-sucedida incluiria...** | Uma arquitetura desacoplada na AWS que separe o fluxo de alta frequência de escrita (eventos logísticos de rastreamento) do fluxo administrativo transacional (catálogo, carrinho e pedidos), garantindo que o portal de e-commerce não seja afetado mesmo sob grande volume de eventos de rastreamento. |

### 2.3 Posicionamento do Produto

Para lojistas e operadores de e-commerce de médio e grande porte, a plataforma proposta é uma solução de comércio eletrônico com rastreamento logístico inteligente, que provê ingestão de eventos de última milha com latência inferior a 80ms e SLA global de disponibilidade de 99,95%. Diferente das plataformas tradicionais on-premises (caras e inflexíveis) ou de arquiteturas monolíticas legadas que utilizam um único banco relacional tanto para dados transacionais quanto para eventos de rastreamento — degradando a performance sob carga — a nossa solução combina o poder do framework Django para o núcleo transacional com uma arquitetura serverless orientada a eventos na AWS para o rastreamento logístico, garantindo elasticidade, segurança e custo previsível.

---

## 3. Descrição dos Stakeholders e Usuários

| Stakeholder (Perfil) | Necessidade Primária | Expectativa na Nuvem (AWS) |
|---|---|---|
| Gestores Logísticos | Acompanhar pedidos e entregas em tempo quase real, identificando gargalos operacionais e exceções na cadeia de última milha. | Painel ágil, com dados de rastreamento atualizados sem atrasos visuais ou travamentos, mesmo sob alto volume de eventos. |
| Diretores Financeiros (CFOs) | Manter o custo operacional da nuvem dentro do orçamento restrito, preservando a margem operacional. | Configuração com custos previsíveis, alertas de faturamento e uso de recursos dimensionados corretamente (elasticidade sem desperdício). |
| Profissionais de Segurança (CISOs) | Garantir que dados de clientes, pedidos e pagamentos estejam protegidos e em conformidade com a legislação nacional. | Criptografia integral de dados em trânsito e em repouso, gestão segura de segredos, rede segmentada (VPC) e rastreabilidade de acessos. |
| Corpo Docente de TI (avaliadores acadêmicos) | Validar a qualidade técnica e a coerência arquitetural do projeto de infraestrutura proposto pelos estudantes. | Solução justificada à luz do AWS Well-Architected Framework, documentada de forma clara e objetiva no Documento de Visão. |

---

## 4. Visão Geral do Produto/Solução

### 4.1 Perspectiva do Produto

A plataforma de e-commerce operará como um ecossistema nativo na nuvem AWS, de formato híbrido. A aplicação principal, construída sobre o framework Django, servirá os canais web e mobile do e-commerce (catálogo, carrinho, pedidos e pagamentos) via protocolo HTTPS. Em paralelo, um fluxo de ingestão serverless autônomo receberá dados de eventos logísticos — atualizações de status de entrega, geolocalização de entregadores e eventos de exceção — enviados pelos aplicativos de rastreamento da operação de última milha.

### 4.2 Funcionalidades Principais

- **Portal do E-commerce**: catálogo de produtos, carrinho de compras, gestão de pedidos e integração com gateways de pagamento.
- **Ingestão Contínua de Eventos Logísticos**: processador assíncrono de eventos de rastreamento (status da entrega, geolocalização, ocorrências).
- **Painel de Rastreamento**: acompanhamento em tempo quase real do status e da localização dos pedidos em trânsito.
- **Sistema de Alertas**: notificações automáticas em caso de anormalidades na entrega (atrasos, desvios de rota, tentativas de entrega frustradas).

### 4.3 Suposições e Dependências

**Suposições:** a equipe do projeto possui conhecimento prévio (ou em desenvolvimento) em Python/Django e nos serviços gerenciados da AWS utilizados; o ambiente de desenvolvimento e homologação replica, em escala reduzida, a arquitetura de produção proposta.

**Dependências:** integrações de pagamento e de frete são tratadas como serviços de terceiros (gateways externos), fora do escopo de desenvolvimento interno; a conformidade com a LGPD é tratada como requisito transversal a todos os componentes que armazenam dados pessoais.

---

## 5. Recursos do Produto (Arquitetura AWS)

Para implementar a visão proposta, a arquitetura AWS foi desenhada com os seguintes serviços fundamentais:

| Serviço AWS | Papel na Arquitetura | Justificativa Técnica (Por que usar?) |
|---|---|---|
| VPC | Isolamento e segmentação de rede de todos os recursos do projeto. | Garante que bancos de dados e serviços internos não fiquem expostos diretamente à internet, atendendo às exigências de segurança dos CISOs e à conformidade com a LGPD. |
| EC2 | Hospedagem das instâncias da aplicação Django (núcleo transacional). | Oferece controle granular sobre o ambiente de execução do framework, permitindo configuração de Auto Scaling para absorver picos de demanda do e-commerce. |
| RDS | Banco de dados relacional gerenciado para pedidos, clientes e catálogo. | Reduz a carga operacional de administração de banco (patches, backups) e oferece implantação Multi-AZ, suportando a meta de disponibilidade de 99,95%. |
| S3 | Armazenamento de objetos estáticos (imagens de produtos, documentos, backups de aplicação). | Armazenamento durável, de baixo custo e altamente disponível, alinhado à necessidade de previsibilidade de custo dos CFOs. |
| DynamoDB | Persistência dos eventos de rastreamento logístico de última milha. | Modelo NoSQL escalável horizontalmente, com latência de leitura/escrita em milissegundos, essencial para atender a meta de latência de ingestão abaixo de 80 ms. |
| API Gateway | Porta de entrada gerenciada para os eventos logísticos enviados por aplicativos de entregadores e parceiros. | Desacopla os produtores de eventos da lógica de processamento, oferecendo throttling, autenticação e monitoramento nativos, sem necessidade de servidores dedicados. |
| Lambda | Processamento serverless dos eventos de ingestão logística. | Elimina custo de infraestrutura ociosa: a cobrança ocorre apenas pelo tempo de execução, atendendo diretamente à restrição orçamentária de US$ 1.500,00/mês. |
| Secrets Manager | Armazenamento e rotação segura de credenciais (banco de dados, chaves de API de terceiros). | Elimina credenciais em texto claro no código-fonte, atendendo aos requisitos de segurança corporativa e de auditoria dos CISOs. |
| CloudWatch | Monitoramento, métricas e alarmes de toda a infraestrutura. | Permite observabilidade em tempo quase real do SLA de disponibilidade e da performance de ingestão, além de acionar respostas automatizadas a incidentes. |
| CodePipeline | Automação do processo de integração e entrega contínua (CI/CD). | Reduz o tempo entre o desenvolvimento e a disponibilização de novas funcionalidades, mitigando a restrição de prazo acadêmico de 20 semanas e a restrição de pessoal reduzido. |

---

## 6. Restrições do Projeto

- **Orçamentária:** o orçamento operacional total para hospedagem do protótipo funcional e simulação está fixado em no máximo US$ 1.500,00 por mês, exigindo o uso preferencial de serviços serverless e de dimensionamento automático para evitar custos fixos desnecessários.
- **Prazo:** o cronograma acadêmico impõe uma restrição de 20 (vinte) semanas para conclusão de todas as fases, desde a Concepção (Inception), Elaboração, até a Construção e a apresentação final do trabalho.
- **Tecnológica:** a aplicação web principal deve obrigatoriamente utilizar Django (Python) para o núcleo transacional, e todo o deploy produtivo deve ser feito exclusivamente dentro de uma conta AWS aplicando serviços gerenciados.
- **Segurança e Compliance:** em atendimento às normas de privacidade nacionais, nenhum dado de pedidos, pagamentos ou dados de identificação pessoal (CPF, dados cadastrais) pode ser trafegado sem criptografia em trânsito e em repouso. O sistema deve atender às exigências básicas da LGPD.
- **Pessoal:** o projeto será executado por uma equipe acadêmica reduzida, dividindo papéis de desenvolvimento backend e administração de infraestrutura (DevOps), o que reforça a necessidade de automação (CI/CD) e de serviços gerenciados que reduzam o esforço operacional manual.

---

## 7. Atributos de Qualidade (SLAs e SLOs)

**Disponibilidade:** a plataforma de e-commerce e o endpoint de ingestão de eventos logísticos devem manter um SLA global de uptime de 99,95% de disponibilidade (aproximadamente 4,3 horas de indisponibilidade permitidas por ano). Isso é alcançado usando sub-redes distribuídas em pelo menos 2 Zonas de Disponibilidade (Multi-AZ), instâncias EC2 sob Auto Scaling e RDS Multi-AZ.

**Performance (Latência):** o endpoint de ingestão serverless deve responder com latência inferior a 80ms para 95% das escritas (p95). A leitura de dashboards e páginas do portal de e-commerce deve carregar rapidamente, usando o caching eficiente do Amazon S3, consultas otimizadas ao DynamoDB e, quando aplicável, CDN para ativos estáticos.

**Segurança (Criptografia):** todas as comunicações públicas devem ser feitas exclusivamente sob protocolo criptografado HTTPS/TLS (porta 443). Os dados confidenciais armazenados no RDS e no DynamoDB devem ser criptografados em repouso usando o AWS KMS, com credenciais geridas via Secrets Manager.

**Continuidade de Negócio (Backup & DR):**
- RPO (Recovery Point Objective): máximo de 15 minutos de perda de dados transacionais, alcançado através de rotinas automáticas de backup e Point-In-Time Recovery habilitados no Amazon RDS e no DynamoDB.
- RTO (Recovery Time Objective): tempo máximo de recuperação total de indisponibilidade sistêmica catastrófica em menos de 1 hora, auxiliado pelo uso de infraestrutura configurada sob templates ou scripts de automação (IaC).

**Custo-eficiência:** reduzir desperdícios aplicando dimensionamento automático (Auto Scaling) nas instâncias EC2, escalando horizontalmente apenas quando o uso agregado de CPU ultrapassar um limiar definido e escalando para baixo (mínimo de instâncias em standby) durante períodos de baixa demanda, além do uso de recursos serverless (Lambda, API Gateway, DynamoDB) cobrados por execução.

---

## 8. Versionamento

| Versão | Data | Descrição da Alteração | Autor(es) |
|---|---|---|---|
| 0.1 | [04/09/2026] | Criação da estrutura inicial do documento, com base no padrão RUP/UP e no modelo de referência da disciplina. | [Ricardo] |
| 0.2 | [dd/mm/aaaa] | Inclusão do posicionamento de mercado e da descrição dos stakeholders. | [Nome] |
| 0.3 | [dd/mm/aaaa] | Detalhamento da arquitetura AWS e dos atributos de qualidade (SLAs/SLOs). | [Nome] |
| 1.0 | [dd/mm/aaaa] | Versão final revisada para entrega acadêmica. | [Nome] |
