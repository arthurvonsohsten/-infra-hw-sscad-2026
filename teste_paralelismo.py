"""
teste_paralelismo.py
====================
Mede o speedup e a eficiência paralela de uma tarefa CPU-bound
(soma de quadrados) variando o número de workers via multiprocessing.

Uso:
    python3 teste_paralelismo.py

Requisitos:
    Python 3.8+  —  sem dependências externas
"""

import multiprocessing
import time
import math

# ── Parâmetros ──────────────────────────────────────────────────────────────
N          = 10_000_000   # tamanho total da tarefa (elementos)
WORKERS    = [1, 2, 4, multiprocessing.cpu_count()]  # configurações testadas
REPETICOES = 3            # médias de N repetições por configuração


def soma_quadrados(args):
    """Soma os quadrados de um intervalo [inicio, fim)."""
    inicio, fim = args
    total = 0
    for i in range(inicio, fim):
        total += i * i
    return total


def executar(num_workers: int) -> float:
    """Executa a tarefa com num_workers e retorna o tempo médio (s)."""
    chunk = N // num_workers
    intervalos = [
        (i * chunk, (i + 1) * chunk if i < num_workers - 1 else N)
        for i in range(num_workers)
    ]

    tempos = []
    for _ in range(REPETICOES):
        t0 = time.perf_counter()
        with multiprocessing.Pool(num_workers) as pool:
            pool.map(soma_quadrados, intervalos)
        tempos.append(time.perf_counter() - t0)

    return sum(tempos) / len(tempos)


def main():
    print("=" * 57)
    print(f"  Teste de Paralelismo — {multiprocessing.cpu_count()} CPUs lógicas")
    print(f"  Tarefa: soma de quadrados de {N:,} elementos")
    print(f"  Média de {REPETICOES} repetições por configuração")
    print("=" * 57)
    print(f"  {'Workers':>7} | {'Tempo (s)':>9} | {'Speedup':>8} | {'Eficiência':>11}")
    print(f"  {'-'*7}-+-{'-'*9}-+-{'-'*8}-+-{'-'*11}")

    tempo_base = None
    resultados = []

    for w in WORKERS:
        t = executar(w)
        if tempo_base is None:
            tempo_base = t
        speedup = tempo_base / t
        eficiencia = speedup / w * 100
        resultados.append((w, t, speedup, eficiencia))
        print(f"  {w:>7} | {t:>9.3f} | {speedup:>7.2f}x | {eficiencia:>10.1f}%")

    print("=" * 57)

    # Diagnóstico
    _, _, _, eff_max = resultados[-1]
    if eff_max < 50:
        print(f"  [WARN] Eficiência < 50% com {WORKERS[-1]} workers.")
        print("         Causas prováveis: thermal throttling,")
        print("         overhead P-Core/E-Core, frações seriais.")
    print("=" * 57)


if __name__ == "__main__":
    main()
