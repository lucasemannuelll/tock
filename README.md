# Time Tracker

Um rastreador de tempo pessoal que roda localmente. Backend em FastAPI com SQLite, frontend em HTML/JS puro sem estilização.

## Funcionalidades

- Iniciar e parar um timer com um clique.
- Registrar entradas manualmente com data e hora de início e fim.
- Associar cada entrada a um projeto.
- Adicionar tags livres a cada entrada, criadas sob demanda.
- Listar entradas de um período, filtrando por projeto ou tag.
- Editar e deletar entradas existentes.
- Gerenciar projetos: criar, renomear e deletar (bloqueado para o projeto padrão e para projetos com entradas).
- Gerenciar tags: listar e deletar.
- Gerar relatórios agregados por dia, semana, mês, projeto ou tag.
- Fatiar entradas que cruzam a meia-noite no relatório diário, mantendo o registro intacto no banco.
- Detectar entradas em andamento ao reabrir a página.
- Sincronizar o estado entre abas abertas via polling.
