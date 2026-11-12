# Elaboração

> Objetivo: refinar os requisitos, resolver os riscos críticos e definir a arquitetura base da Plataforma de E-commerce com Logística Last-Mile.

## Documentos da fase

| Documento | Arquivo | O que contém | Adendo AP2 |
| :--- | :--- | :--- | :--- |
| [Casos de Uso Arquiteturais](cua.md) | `cua.md` | Casos de uso que guiam a arquitetura e sua matriz | §7: casos de uso da API implantada ligados aos testes |
| [Modelo de Análise — Pacotes/Subsistemas](maps.md) | `maps.md` | Pacotes, subsistemas e dependências | Mapa dos módulos do projeto `lastmile` / app `loja` |
| [Dimensionamento de Computação](dim_comp.md) | `dim_comp.md` | Dimensionamento das instâncias EC2 | §14: tipo escolhido, custo, rede e consumo medido |
| [Dimensionamento de Banco de Dados](dimrbd.md) | `dimrbd.md` | Volumetria e escolha do banco | §13: medições reais, índice GIN, Docker × RDS, backup |
| [Sequência e Comunicação](seq_com.md) | `seq_com.md` | Fluxos críticos e matriz de rastreamento | Documento inteiro dedicado à solução implantada |
| [Consolidação Arquitetural](consolidacao_arquitetural.md) | `consolidacao_arquitetural.md` | Visão consolidada da arquitetura | §9: sequência do checkout e componentes implantados |

## Decisão arquitetural da AP2

A arquitetura-alvo (ALB, Auto Scaling, RDS Multi-AZ) continua descrita como evolução. Para a AP2 foi implantada uma versão mínima e verificável: **uma EC2 com Docker Compose**, contêiner `web` (Django REST + gunicorn) e contêiner `db` (PostgreSQL 16 relacional + JSONB com índice GIN, volume `pgdata`). A justificativa de custo e capacidade está em [Dimensionamento de Computação](dim_comp.md) e [Dimensionamento de Banco de Dados](dimrbd.md).
