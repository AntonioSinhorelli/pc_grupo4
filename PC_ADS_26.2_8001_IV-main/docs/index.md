---
hide:
    - navigation
    - toc
---  

# PC_ADS_26.2_8001_IV { style="display:none" }
<div class="module-cards grid four-cols">

 <!-- Grupo IV -->
    <div class="card module-card" data-module-id="PC_ADS_26.2_8001_IV">
        <div class="card-header">
            PC_ADS_26.2_8001_IV
        </div>
        <div class="card-content">
            <p><strong>Plataforma de E-commerce com Arquitetura de Nuvem Híbrida e Logística Last-Mile Inteligente</strong></p>
            <p class="contributors">Ricardo França, Antonio Sinhorelli, Caio Araujo</p>
            <a href="https://github.com/Projetos-de-Extensao/PC_ADS_26.2_8001_IV" class="button primary-btn">
                <span class="octicon-arrow-right-24:"></span> Ver Repositório
            </a>
        </div>
    </div>

</div>

## Documentos do projeto

| Fase | Documento |
| :--- | :--- |
| Iniciação | [Documento de Visão](Iniciacao/dv.md) |
| Iniciação | [Requisitos Suplementares](Iniciacao/rs.md) |
| Elaboração | [Casos de Uso Arquiteturais](Elaboracao/cua.md) |
| Elaboração | [Modelo de Análise (Pacotes/Subsistemas)](Elaboracao/maps.md) |
| Elaboração | [Modelo de Análise (Dimensionamento BD)](Elaboracao/dimrbd.md) |
| Elaboração | [Modelo de Análise (Modelo de Computação)](Elaboracao/dim_comp.md) |
| Elaboração | [Sequência e Comunicação](Elaboracao/seq_com.md) |
| Elaboração | [Modelo de Design (Consolidação Arquitetural)](Elaboracao/consolidacao_arquitetural.md) |
| Transição | [Modelo de Design (Atividades - Deploy)](Transicao/ativ_deploy.md) |

## Solução implantada (AP2)

| Item | Onde |
| :--- | :--- |
| API Django REST em Docker na EC2 | <http://77.112.118.58:8000/api/> |
| Health check | <http://77.112.118.58:8000/health/> |
| Código, Dockerfile, docker-compose e evidências | <https://github.com/AntonioSinhorelli/pc_grupo4> |
| Arquitetura | EC2 `c7i-flex.large` (us-east-2) + Docker Compose (`web`: Django + gunicorn; `db`: PostgreSQL 16 com volume `pgdata`) |

Cada documento das fases abaixo tem um **Adendo AP2** com o que foi efetivamente implantado; os demais conteúdos descrevem a arquitetura-alvo de longo prazo.

