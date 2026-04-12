# fifteen-puzzle-game

Implementação do Jogo do 15 com:
- Verificação de solucionabilidade do estado inicial;
- Geração aleatória de estados solucionáveis;
- Agentes de busca: BFS, DFS (IDDFS) e A* (distância de Manhattan);
- Evitação de ciclos;
- Comparação dos métodos por médias de nós expandidos, movimentos e tempo.

## Execução

```bash
python main.py --moves 20
```

## Comparação automática (Tarefa 5)

```bash
python main.py --compare --trials 10 --moves 20 --max-nodes 200000 --dfs-limit 50
```

Parâmetros principais:
- `--max-nodes`: limite de nós expandidos por execução (interrompe busca ao atingir o limite);
- `--compare`: executa comparação em múltiplos estados iniciais aleatórios;
- `--trials`: quantidade de estados aleatórios para cálculo das médias.
