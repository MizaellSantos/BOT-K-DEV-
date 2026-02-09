# BOT-K-DEV-
Infraestrutura para gestão de pontos no Discord pela KDEV. Focado em organização, equilíbrio operacional e controle de engajamento para moderadores.
# 👮‍♂️ Bot de Gestão de Polícia - Discord.py

Este é um bot multifuncional desenvolvido em Python para servidores de Discord focado em simulações de polícia (RP) ou gestão de equipes. Ele oferece um sistema completo de pontuação (PP), ranking, logs de staff e uma dashboard interativa para anúncios.

## 🚀 Funcionalidades

-   **📊 Sistema de Pontuação (PP):**
    -   `/setpp`: Adiciona pontos a um oficial (com sistema de prova via imagem).
    -   `/retirarpp`: Remove pontos em caso de erro ou punição.
    -   `/perfil`: Mostra o saldo de pontos atual do usuário.
    -   `/ranking`: Exibe o Top 10 oficiais com mais pontos.
-   **📢 Dashboard de Anúncios:**
    -   `/anunciar`: Sistema inteligente em **duas etapas** (via Modais) para criar embeds profissionais.
    -   Suporte a Título, Autor, Thumbnail, Imagem Grande e Rodapé.
    -   Inclusão de **Botões de Link** externos de forma dinâmica.
-   **📜 Sistema de Logs:**
    -   Registro automático de todas as ações da Staff em um canal privado.
    -   Logs de atribuição/remoção de pontos e anúncios realizados.

## 🛠️ Tecnologias Utilizadas

* [Python 3.14+](https://www.python.org/)
* [Discord.py](https://discordpy.readthedocs.io/en/stable/)
* JSON (Armazenamento de dados local)

## 📋 Pré-requisitos

Antes de começar, você vai precisar do Python instalado e das seguintes bibliotecas:

```bash
pip install discord.py  
  
