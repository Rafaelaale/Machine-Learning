# E-mail recebido — DAG de Vendas

**De:** Mariana Ferreira <mariana.ferreira@vendemais.com.br>
**Para:** Time de Dados <dados@vendemais.com.br>
**Assunto:** Relatório diário de vendas por categoria — automação
**Data:** Segunda-feira, 13 de janeiro de 2025

---

Oi pessoal, tudo bem?

Estou enviando esse e-mail porque precisamos resolver um problema que está consumindo bastante tempo do meu time todo dia de manhã.

Hoje a gente recebe da equipe comercial um arquivo CSV com todos os pedidos do dia anterior. Esse arquivo cai numa pasta de rede que o pessoal do TI configurou pra gente. O nome do arquivo segue sempre o mesmo padrão: `vendas_YYYY-MM-DD.csv` (com a data do dia anterior).

O que a gente faz manualmente hoje:

1. Abre o CSV no Excel
2. Faz um pivot por categoria de produto
3. Calcula o total vendido em reais e a quantidade de pedidos
4. Salva uma planilha de resumo numa pasta compartilhada
5. Envia o link pro time de gestão

O problema é que isso toma uns 40 minutos toda manhã, e às vezes a pessoa responsável fica doente ou de férias e ninguém faz. A diretoria reclama quando o relatório atrasa.

Queria que isso virasse automático. O ideal seria ter o resumo pronto até as 8h da manhã todo dia, sem ninguém precisar fazer nada.

Algumas observações importantes:

- O arquivo nem sempre chega no mesmo horário. Geralmente entre 5h e 7h da manhã, mas já teve dia que chegou só às 7h30
- Se o arquivo não chegar até as 8h, alguém precisa ser avisado pra investigar
- Já aconteceu de chegar arquivo corrompido ou vazio. Quando isso acontece a gente precisa saber pra cobrar a equipe comercial
- O resumo precisa ter: categoria, total de pedidos, valor total em reais, ticket médio

Não precisa ser nada sofisticado. Só queremos que o processo aconteça sozinho e que a gente seja avisado quando der problema.

Qualquer dúvida me chama no Slack.

Abraço,
Mariana
Gerente de Operações Comerciais
Vende+
