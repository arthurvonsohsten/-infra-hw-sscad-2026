"""
teste_localidade.py
===================
Demonstra o impacto da localidade espacial de cache comparando
dois padrões de acesso a uma matriz 2D:

  Loop A — row-major (linha por linha): stride de 4 bytes
            → hardware prefetcher ativo, alta reutilização de cache line

  Loop B — col-major (coluna por coluna): stride de N*4 bytes
            → L3 cache miss por acesso, 93% da cache line desperdiçada

Uso:
    python3 teste_localidade.py

Requisitos:
    Python 3.8+  —  sem dependências externas
    (versão com numpy opcional para comparação)
"""

import time
import array

# ── Parâmetros ──────────────────────────────────────────────────────────────
N = 4096   # dimensão da matriz quadrada NxN
           # tamanho total: 4096 * 4096 * 4 bytes = 64 MiB


def criar_matriz(n: int):
    """Cria uma matriz NxN como lista de arrays de float (32 bits)."""
    return [array.array('f', [float(i * n + j) for j in range(n)])
            for i in range(n)]


def loop_a_row_major(matriz, n: int) -> float:
    """Percorre a matriz linha por linha (row-major). Retorna tempo (s)."""
    t0 = time.perf_counter()
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += matriz[i][j]
    return time.perf_counter() - t0


def loop_b_col_major(matriz, n: int) -> float:
    """Percorre a matriz coluna por coluna (col-major). Retorna tempo (s)."""
    t0 = time.perf_counter()
    total = 0.0
    for j in range(n):
        for i in range(n):
            total += matriz[i][j]
    return time.perf_counter() - t0


def main():
    tamanho_mib = N * N * 4 / (1024 ** 2)
    stride_b_bytes = N * 4

    print("=" * 60)
    print("  Teste de Localidade Espacial de Cache")
    print(f"  Matriz: {N} x {N} x float32  =>  {tamanho_mib:.0f} MiB")
    print("=" * 60)
    print("  Alocando matriz...")

    matriz = criar_matriz(N)

    print(f"  Cache line = 64 bytes (16 floats)")
    print(f"  Loop A stride =  4 bytes  (row-major)")
    print(f"  Loop B stride = {stride_b_bytes:,} bytes  (col-major, {stride_b_bytes/1024:.0f} KiB)")
    print()

    print("  Executando Loop A (row-major)...", end=" ", flush=True)
    tempo_a = loop_a_row_major(matriz, N)
    print(f"{tempo_a:.3f} s")

    print("  Executando Loop B (col-major)...", end=" ", flush=True)
    tempo_b = loop_b_col_major(matriz, N)
    print(f"{tempo_b:.3f} s")

    razao = tempo_b / tempo_a
    desperdicio = (1 - 1/16) * 100  # 1 float útil de 16 por cache line

    print()
    print(f"  Razao B/A                         : {razao:.2f}x")
    print(f"  Desperdicio de banda (Loop B)     : {desperdicio:.1f}%")
    print("=" * 60)
    print(f"  [INFO] Loop A: prefetcher HW ativo; alta reutilizacao.")
    print(f"         Loop B: L3 miss em cada acesso;")
    print(f"                 apenas 1 float util por cache line carregada.")
    print("=" * 60)


if __name__ == "__main__":
    main()
