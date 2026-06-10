# infra-hw-sscad-2026

Scripts e dados dos experimentos utilizados no artigo científico submetido ao **SSCAD-WIC 2026** (Workshop de Iniciação Científica do Simpósio em Sistemas Computacionais de Alto Desempenho).

---

## 📄 Artigo

**Título:** Análise Empírica da Hierarquia de Memória e do Impacto de *Thermal Throttling* em Processadores Híbridos de Baixo TDP: Um Estudo de Caso com Intel Core i5-1235U

**Autores:** Arthur de Lima von Sohsten, Eduardo Henrique de Sá, Miguel Andrade

**Instituição:** CESAR School — Centro de Estudos e Sistemas Avançados do Recife

**Evento:** SSCAD-WIC 2026 — Natal/RN, novembro de 2026

---

## 🖥️ Ambiente experimental

| Componente | Especificação |
|---|---|
| Processador | Intel Core i5-1235U (10 núcleos, 12 threads) |
| TDP | PL1: 15 W / PL2: 28 W |
| Cache L3 | 12 MiB (LLC compartilhado) |
| RAM | 16 GB DDR4-3200 |
| Armazenamento | Samsung SSD 980 256 GB (NVMe PCIe Gen3 x4) |
| SO | Ubuntu 22.04.3 LTS via WSL2 (Windows 11 22H2) |

---

## 📁 Estrutura do repositório

```
infra-hw-sscad-2026/
├── scripts/
│   ├── teste_paralelismo.py     # Experimento de escalabilidade paralela
│   ├── teste_localidade.py      # Experimento de localidade espacial de cache
│   └── workload_completo.py     # Benchmark integrado (CPU + memória + I/O)
├── resultados/
│   ├── saida_paralelismo.txt    # Saída do teste de paralelismo
│   ├── saida_localidade.txt     # Saída do teste de localidade
│   └── saida_workload.txt       # Saída do benchmark integrado
└── README.md
```

---

## 🚀 Como executar

### Requisitos

- Python 3.8 ou superior
- Sem dependências externas (apenas biblioteca padrão)

### Instalação

```bash
git clone https://github.com/arthursohsten/infra-hw-sscad-2026.git
cd infra-hw-sscad-2026
```

### Experimento 1 — Paralelismo

```bash
python3 scripts/teste_paralelismo.py
```

Mede o *speedup* e a eficiência paralela variando o número de *workers* em {1, 2, 4, N} onde N é o número de CPUs lógicas da máquina.

**Saída esperada:**
```
=========================================================
  Teste de Paralelismo — 12 CPUs lógicas
  Tarefa: soma de quadrados de 10.000.000 elementos
  Média de 3 repetições por configuração
=========================================================
  Workers | Tempo (s) |  Speedup | Eficiência
  --------+-----------+----------+-----------
        1 |    12.847 |   1.00x  |    100.0%
        2 |     6.623 |   1.94x  |     97.0%
        4 |     3.581 |   3.59x  |     89.7%
       12 |     2.389 |   5.38x  |     44.8%
=========================================================
```

### Experimento 2 — Localidade Espacial

```bash
python3 scripts/teste_localidade.py
```

Compara o tempo de acesso a uma matriz 4096×4096 float32 (64 MiB) em ordem *row-major* vs *col-major*.

**Saída esperada:**
```
============================================================
  Teste de Localidade Espacial de Cache
  Matriz: 4096 x 4096 x float32  =>  64 MiB
============================================================
  Loop A  (row-major, stride  4 B)  : 0.347 s
  Loop B  (col-major, stride 16 KiB): 2.514 s
  Razao B/A                         : 7.25x
============================================================
```

### Experimento 3 — Benchmark Integrado

```bash
python3 scripts/workload_completo.py
```

Executa quatro fases sequenciais (CPU-bound, memory-bound, I/O-bound e saturação simultânea) e infere o gargalo dominante da plataforma.

---

## 📊 Resultados principais

| Experimento | Métrica | Valor |
|---|---|---|
| Cinebench R23 Single Core | Pontuação | 1.487 pts |
| Cinebench R23 Multi Core | Pontuação | 7.312 pts |
| Fator de escala real vs teórico | Speedup | 4,92× / 12× |
| mbw L3 (16 MiB) | Banda | 31.204 MiB/s |
| mbw RAM (1.024 MiB) | Banda | 12.148 MiB/s |
| Localidade espacial (razão B/A) | Tempo | 7,25× |
| fio randread 4K | IOPS | 38.147 |

---

## 📝 Licença

Este repositório é de uso acadêmico. Os scripts são distribuídos livremente para fins de reprodução dos experimentos.

---

## 📬 Contato

- **Arthur Von Sohsten** -  [alvs@cesar.school](mailto:alvs@cesar.school)
- **Eduardo Henrique** - [ehsnl@cesar.school](mailto:ehsnl@cesar.school)
- **Miguel Andrade** - [mjfa@cesar.school](mailto:mjfa@cesar.school)
