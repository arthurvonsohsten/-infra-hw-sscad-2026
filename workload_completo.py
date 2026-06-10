"""
workload_completo.py
====================
Benchmark integrado com quatro fases sequenciais:

  Fase 1 — CPU-bound    : multiplicações FP64 em todos os núcleos (30 s)
  Fase 2 — Memory-bound : leitura sequencial de buffer grande (> L3)
  Fase 3 — I/O-bound    : leitura aleatória simulada em arquivo temporário
  Fase 4 — Saturação    : todas as fases simultaneamente

Ao final, o script infere o gargalo dominante com base nos resultados.

Uso:
    python3 workload_completo.py

Requisitos:
    Python 3.8+  —  sem dependências externas
"""

import multiprocessing
import time
import os
import math
import struct
import tempfile
import random
import array

# ── Parâmetros ──────────────────────────────────────────────────────────────
CPU_DURATION   = 30       # segundos para a fase CPU-bound
MEM_SIZE_MB    = 512      # tamanho do buffer memory-bound (MiB)
IO_FILE_MB     = 256      # tamanho do arquivo de I/O (MiB)
IO_READS       = 5_000    # número de leituras aleatórias de 4 KB
BLOCK_4K       = 4096     # tamanho do bloco de leitura aleatória (bytes)


# ── Fase 1: CPU-bound ────────────────────────────────────────────────────────
def _cpu_worker(args):
    """Worker: multiplica floats por duration segundos e conta operações."""
    duration, seed = args
    x = float(seed)
    ops = 0
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < duration:
        x = x * 1.0000001 + 0.0000001
        ops += 1
    return ops


def fase_cpu(duration: int) -> dict:
    """Executa carga CPU-bound em todos os núcleos por duration segundos."""
    n = multiprocessing.cpu_count()
    t0 = time.perf_counter()
    with multiprocessing.Pool(n) as pool:
        resultados = pool.map(_cpu_worker, [(duration, i) for i in range(n)])
    elapsed = time.perf_counter() - t0
    total_ops = sum(resultados)
    return {
        "workers": n,
        "elapsed": elapsed,
        "total_ops": total_ops,
        "ops_per_sec": total_ops / elapsed,
    }


# ── Fase 2: Memory-bound ─────────────────────────────────────────────────────
def fase_memoria(size_mb: int) -> dict:
    """Lê sequencialmente um buffer maior que o L3 para forçar acesso à RAM."""
    n_floats = (size_mb * 1024 * 1024) // 8  # float64 = 8 bytes
    buf = array.array('d', [float(i) for i in range(n_floats)])

    t0 = time.perf_counter()
    total = 0.0
    for v in buf:
        total += v
    elapsed = time.perf_counter() - t0

    bytes_lidos = n_floats * 8
    banda_gbs = bytes_lidos / elapsed / 1e9
    return {
        "size_mb": size_mb,
        "elapsed": elapsed,
        "banda_gbs": banda_gbs,
        "checksum": total,
    }


# ── Fase 3: I/O-bound ────────────────────────────────────────────────────────
def fase_io(file_mb: int, n_reads: int) -> dict:
    """Escreve arquivo temporário e realiza leituras aleatórias de 4 KB."""
    tamanho = file_mb * 1024 * 1024
    dados = os.urandom(tamanho)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        fname = f.name
        f.write(dados)

    try:
        posicoes = [random.randint(0, tamanho - BLOCK_4K)
                    for _ in range(n_reads)]
        t0 = time.perf_counter()
        with open(fname, "rb") as f:
            for pos in posicoes:
                f.seek(pos)
                f.read(BLOCK_4K)
        elapsed = time.perf_counter() - t0
    finally:
        os.unlink(fname)

    bytes_lidos = n_reads * BLOCK_4K
    throughput_mbs = bytes_lidos / elapsed / 1e6
    iops = n_reads / elapsed
    lat_us = elapsed / n_reads * 1e6

    return {
        "file_mb": file_mb,
        "n_reads": n_reads,
        "elapsed": elapsed,
        "throughput_mbs": throughput_mbs,
        "iops": iops,
        "lat_us": lat_us,
    }


# ── Fase 4: Saturação ────────────────────────────────────────────────────────
def fase_saturacao() -> dict:
    """Executa CPU + memória + I/O simultaneamente por 15 segundos."""
    import threading

    resultados = {}
    stop_event = threading.Event()

    def cpu_thread():
        ops = 0
        x = 1.0
        t0 = time.perf_counter()
        while not stop_event.is_set():
            x = x * 1.0000001 + 0.0000001
            ops += 1
        resultados["cpu_ops"] = ops
        resultados["cpu_elapsed"] = time.perf_counter() - t0

    def mem_thread():
        n = (64 * 1024 * 1024) // 8
        buf = array.array('d', [float(i % 1000) for i in range(n)])
        total = 0.0
        while not stop_event.is_set():
            for v in buf:
                total += v
                if stop_event.is_set():
                    break
        resultados["mem_checksum"] = total

    threads = [
        threading.Thread(target=cpu_thread),
        threading.Thread(target=mem_thread),
    ]
    for t in threads:
        t.start()

    time.sleep(15)
    stop_event.set()

    for t in threads:
        t.join()

    return resultados


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    ncpus = multiprocessing.cpu_count()
    print("=" * 65)
    print("  BENCHMARK INTEGRADO — Infraestrutura de Hardware")
    print(f"  CPUs: {ncpus} | Python {__import__('sys').version.split()[0]}")
    print("=" * 65)

    # Fase 1
    print(f"\n  [1/4] FASE CPU-BOUND ({CPU_DURATION} s, {ncpus} workers)...")
    r1 = fase_cpu(CPU_DURATION)
    print(f"        Throughput : {r1['ops_per_sec']:.2e} ops/s")
    print(f"        Total ops  : {r1['total_ops']:,}")

    # Fase 2
    print(f"\n  [2/4] FASE MEMORY-BOUND (buffer {MEM_SIZE_MB} MiB)...")
    r2 = fase_memoria(MEM_SIZE_MB)
    print(f"        Largura de banda : {r2['banda_gbs']:.2f} GB/s")
    print(f"        Tempo            : {r2['elapsed']:.2f} s")

    # Fase 3
    print(f"\n  [3/4] FASE I/O-BOUND ({IO_READS:,} leituras aleatórias 4 KB)...")
    r3 = fase_io(IO_FILE_MB, IO_READS)
    print(f"        Throughput : {r3['throughput_mbs']:.1f} MB/s")
    print(f"        IOPS       : {r3['iops']:,.0f}")
    print(f"        Latência   : {r3['lat_us']:.1f} µs")

    # Fase 4
    print(f"\n  [4/4] FASE SATURAÇÃO (CPU + Mem simultâneos, 15 s)...")
    r4 = fase_saturacao()
    print(f"        CPU ops durante saturação: {r4.get('cpu_ops', 0):,}")

    # Diagnóstico
    print("\n" + "=" * 65)
    print("  DIAGNÓSTICO:")

    ops_ratio = r1["ops_per_sec"] / (r4.get("cpu_ops", 1) / 15)
    if ops_ratio > 1.3:
        gargalo = "Thermal Throttling (CPU-bound)"
    elif r2["banda_gbs"] < 5.0:
        gargalo = "Memory-bound (banda de RAM limitada)"
    else:
        gargalo = "I/O-bound (latência de armazenamento)"

    print(f"  >> GARGALO IDENTIFICADO: {gargalo}")
    print("=" * 65)


if __name__ == "__main__":
    main()
