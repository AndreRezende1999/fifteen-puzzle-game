# TP1 - Jogo do 15

Projeto em **arquivo unico**: `main.py`.

Implementa exatamente as tarefas do trabalho:
1. verificacao de solucionabilidade;
2. geracao aleatoria de estado inicial solucionavel;
3. BFS e DFS com evitacao de ciclos;
4. A* com custo `g(n)` e heuristica de Manhattan `h(n)`;
5. comparacao por medias de nos expandidos, movimentos e tempo.

## Execucao

```bash
python main.py
```

## Observacao

Sem argumentos de linha de comando.

Ao executar, o programa mostra:
1. uma execucao unica (estado inicial + BFS/DFS/A*);
2. a comparacao dos metodos em varios estados.

## Notebook Jupyter

Arquivo criado: `analise_jogo_15.ipynb`.

Ele esta separado por partes e inclui:
- execucoes repetidas de BFS, DFS e A* em `N_GAMES` (padrao: 100);
- configuracao explicita das variaveis principais (`N_GAMES`, `SAMPLE_STATES`, `NODE_LIMIT`, `DEPTH_LIMIT`, `SEED`);
- tabelas de resumo;
- grafico de movimentos por sequencia (linha por algoritmo e ponto por jogo);
- regras mapeadas e graficos adicionais (solucionabilidade x desempenho, eficiencia e boxplot de tempos);
- exportacao de dados para:
  - `resultados_execucoes_tp1.csv`
  - `resumo_geral_algoritmos.csv`
  - `movimentos_por_sequencia.csv`
  - `resumo_solucionabilidade.csv`
  - `eficiencia_algoritmos.csv`
