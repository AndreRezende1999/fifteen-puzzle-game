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

Opcional:
- `--moves 20` define quantos movimentos aleatorios geram o estado inicial.

## Comparacao

```bash
python main.py --compare
```

Opcional:
- `--trials 10` quantidade de estados iniciais na comparacao.
- `--moves 20` dificuldade dos estados.

## Observacao

O limite fixo e alto de busca esta no proprio codigo (`MAX_NODES`), conforme recomendacao do enunciado.
