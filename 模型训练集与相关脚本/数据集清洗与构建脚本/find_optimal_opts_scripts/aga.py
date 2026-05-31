#FIXME:自适应公式中的系数(k1/k2/k3)缺乏理论依据，建议添加注释说明取值依据
import random
import os
import subprocess
import re
import argparse
# import numpy as np

# 参数配置
POP_SIZE = 40  # 种群大小，自适应调整
NUM_GENERATIONS = 30  # 最大迭代次数，
# CROSSOVER_RATE = 0.8  # 交叉概率，自适应调整
# MUTATION_RATE = 0.01  # 变异概率（每bit），自适应调整
NUM_OPTIONS = 85  # 编译选项数 去除-fbranch-probabilities -mmemory-latency=high/medium/low -flto -fdelayed-branch -fassociative-math "-fsw-hardware-prefetch-clt=5","-fsw-hardware-prefetch-cnt-l1=10","-fsw-hardware-prefetch-cnt-l2=100","-fsw-hardware-prefetch-cnt-l3=1000","-fsw-hardware-prefetch-clt=10","-fsw-hardware-prefetch-cnt-l1=100","-fsw-hardware-prefetch-cnt-l2=200","-fsw-hardware-prefetch-cnt-l3=300"
ELITE_COUNT = 2  # 精英保留数量（防止退化）
# TEST_PROGRAM = "tester.cpp"  # 待编译的程序，编译时参数指定
option=["-fsw-auto-inc-dec","-fsw-branch-combination","-fsw-fast-math","-fsw-fprnd","-fsw-fselect","-fsw-hardware-prefetch -fsw-hardware-prefetch-exit","-fsw-int-div-opt","-fsw-non-temporal","-fsw-prefetch-sc","-fsw-prefetch-tc","-fsw-prefetch-unroll","-fsw-recip","-fsw-recip-precision","-fsw-rsqrt","-fsw-sdsame","-fsw-sf-cmpsel","-fsw-unalign-byte","-mbwx","-mcix","-mexplicit-relocs","-mfix","-mfloat-ieee","-mfp-regs","-mieee","-mieee-conformant","-mieee-main","-mieee-with-inexact","-mlarge-data","-mlarge-text","-mlong-double-128","-mlong-double-64","-mlra","-mmax","-msimd","-msmall-data","-msmall-text","-msw-use-32align","-msw8a","-mtls-kernel","-mcpu=sw8a","-mtune=sw8a","-fallow-store-data-races","-fcx-fortran-rules","-fcx-limited-range","-fdelete-dead-exceptions","-fdelete-null-pointer-checks","-ffinite-loops","-ffinite-math-only","-ffloat-store","-fgcse-las","-fgcse-sm","-fipa-pta","-fipa-struct-reorg","-fira-loop-pressure","-fkeep-gc-roots-live","-flive-range-shrinkage","-fmodulo-sched","-fmodulo-sched-allow-regmoves","-freciprocal-math","-freg-struct-return","-frename-registers","-freorder-blocks-and-partition","-freschedule-modulo-scheduled-loops","-fsched-pressure","-fsched-spec-load","-fsched-spec-load-dangerous","-fsched-stalled-insns","-fsched2-use-superblocks","-fsection-anchors","-fsel-sched-pipelining","-fsel-sched-pipelining-outer-loops","-fsel-sched-reschedule-pipelined","-fselective-scheduling","-fselective-scheduling2","-fsingle-precision-constant","-fsplit-wide-types-early","-ftracer","-ftree-cselim","-ftree-loop-if-convert","-ftree-lrs","-ftree-vectorize","-funroll-all-loops","-funroll-loops","-fvariable-expansion-in-unroller","-fweb"]

# pre.0 种群多样性
def population_diversity(f_avg, parents_fitnesses):
    """计算种群多样性"""
    return sum(abs(fit - f_avg) for fit in parents_fitnesses) / len(parents_fitnesses) / f_avg

# pre.1 收敛程度
def convergence_degree(f_avg, f_max):
    """计算收敛程度"""
    return (f_max - f_avg) / f_max

# pre.2 自适应交叉率（根据个体适应度和种群多样性调整）
def adaptive_crossover_rate(f_parent1, f_parent2, f_avg, parents_fitnesses, base_pc=0.8):
    """自适应交叉概率"""
    f_max = max(f_parent1, f_parent2)
    # 优秀个体保护：适应度高的个体降低交叉概率
    if f_max > f_avg:
        k1 = 0.8  # 衰减系数
        pc = base_pc * k1 * (f_avg / f_max)
    else:
        pc = base_pc

    # 种群多样性调节
    diversity = population_diversity(f_avg, parents_fitnesses)
    k2 = 0.3  # 多样性调节系数
    pc *= (1 + k2 * diversity)

    return min(max(pc, 0.6), 0.95)  # 限制在合理范围

# pre.3 自适应变异率(根据个体适应度和收敛程度调整)
def adaptive_mutation_rate(f_ind, f_avg, f_max, base_pm=0.01):
    """自适应变异概率"""
    # 基础变异概率
    if f_ind > f_avg:
        k1 = 0.8  # 优秀个体保护系数
        pm = base_pm * k1 * (f_avg / f_ind)
    else:
        k2 = 1.2  # 弱势个体增强系数
        pm = base_pm * k2

    # 收敛程度调节
    conv = convergence_degree(f_avg, f_max)
    k3 = 0.5  # 收敛调节系数
    pm *= (1 + k3 * conv)

    return min(max(pm, 0.001), 0.1)  # 限制在合理范围

# pre.4 自适应种群大小（根据迭代次数调整）
def adaptive_population_size(gen, min_size=20, max_size=40):
    """自适应种群大小"""
    # 早期：大种群增加多样性
    if gen < NUM_GENERATIONS * 0.3:
        return max_size
    # 中期：中等种群平衡探索开发
    elif gen < NUM_GENERATIONS * 0.7:
        return (max_size + min_size) // 2
    # 后期：小种群加速收敛
    else:
        return min_size

# 1. 初始化种群
def initialize_population():
    return [[random.randint(0, 1) for _ in range(NUM_OPTIONS)] for _ in range(POP_SIZE)]


# 2. 适应度函数：编译并运行程序，测量执行时间
def fitness(individual):
    # 解码个体为编译选项：例如，位[i]对应具体选项名称（需要预定义映射）
    options = []
    for i, bit in enumerate(individual):
        if bit == 1:
            options.append(f"{option[i]}")  # 假设选项有唯一名称（实际需映射）
    compile_cmd = f"sw_64-sunway-linux-gnu-g++ -O3 -static -std=c++11 {' '.join(options)} {TEST_PROGRAM} -o {BINARY_PROGRAM}"  # 编译命令
    print(compile_cmd)
    # 执行编译
    if os.system(compile_cmd) != 0: #返回值为0，代表命令执行成功
        return 0.0  # 编译失败：适应度=0

    # 运行程序并测量时间（运行多次取平均）
    run_times = []
    for _ in range(3):   # 运行3次减少噪音
        result = subprocess.run([BINARY_PROGRAM, PROGRAM_INPUT], capture_output=True, text=True)
        if result.returncode !=0:
            return 0.0 #运行失败：适应度=0
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Time:"):
                match = re.search(r'Time: ([0-9]+)', line)
                time_value = float(match.group(1))
                run_times.append(time_value)
    os.remove(BINARY_PROGRAM)
    avg_time = sum(run_times) / len(run_times)

    return 1.0 / (avg_time + 1e-6)  # 适应度：执行时间倒数


# 3. 选择操作：锦标赛选择
def selection(population, fitnesses, num_parents):
    selected = []
    for _ in range(num_parents):
        contestants = random.sample(list(zip(population, fitnesses)), 3)  # 锦标赛大小=3
        winner = max(contestants, key=lambda x: x[1])[0]  # 选适应度最高
        selected.append(winner)
    return selected


# 4. 交叉操作：单点交叉
def crossover(parent1, parent2, base_pc=0.8):
    if random.random() < base_pc:
        crossover_point = random.randint(1, NUM_OPTIONS - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    return parent1, parent2  # 不发生交叉


# 5. 变异操作
def mutate(individual, base_pm=0.01):
    for i in range(len(individual)):
        if random.random() < base_pm:
            individual[i] = 1 - individual[i]  # 翻转位
    return individual


# 主GA循环
population = initialize_population()
for i in range(len(population[0])):
    population[0][i] = 0

best_fitness = -float('inf')
best_individual = None

parser = argparse.ArgumentParser(description="src_path")
parser.add_argument('test_program', type=str, help="path to the test program")
args=parser.parse_args()
TEST_PROGRAM=args.test_program
PROGRAM_INPUT=os.path.join(os.path.dirname(TEST_PROGRAM), "input.json")

BINARY_PROGRAM=os.path.join(os.path.dirname(TEST_PROGRAM), "a.out")
PROGRAM_OUTPUT=os.path.join(os.path.dirname(TEST_PROGRAM), "output.log")


for gen in range(NUM_GENERATIONS):

    # 评估所有个体适应度
    fitnesses = []
    for ind in population:
        fit = fitness(ind)
        fitnesses.append(fit)
        if fit > best_fitness:  # 更新全局最佳
            best_fitness = fit
            best_individual = ind

    # 输出当前代信息
    print(f"Generation {gen}: Best Fitness = {best_fitness:.4f}")

    # 选择父代（保留精英）
    elite = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)[:ELITE_COUNT]
    elite_individuals = [ind for ind, fit in elite]
    parents = selection(population, fitnesses, POP_SIZE - ELITE_COUNT)  # 选择剩余父代

    # 生成子代：交叉和变异
    new_population = elite_individuals  # 精英直接保留
    random.shuffle(parents)  # 随机打乱增加多样性

    # 为每个父代个体存储适应度
    parents_fitnesses = [fitnesses[population.index(ind)] for ind in parents]

    # 计算种群适应度统计量
    f_avg = sum(fit for fit in parents_fitnesses) / len(parents_fitnesses)
    f_max = max(parents_fitnesses)
    f_min = min(parents_fitnesses)

    for i in range(0, len(parents), 2):
        if i + 1 < len(parents):
            # 获取两个父代的适应度
            f_parent1 = parents_fitnesses[i]
            f_parent2 = parents_fitnesses[i+1]

            # 自适应交叉率
            child1, child2 = crossover(parents[i], parents[i + 1], adaptive_crossover_rate(f_parent1, f_parent2, f_avg, parents_fitnesses))

            # 自适应变异率
            new_population.append(mutate(child1, adaptive_mutation_rate(f_parent1, f_avg, f_max)))
            new_population.append(mutate(child2, adaptive_mutation_rate(f_parent2, f_avg, f_max)))

    POP_SIZE = adaptive_population_size(gen)
    population = new_population[:POP_SIZE]  # 确保种群大小不变

# 输出结果
print(f"Optimization Complete. Best Fitness: {best_fitness:.4f}")
print(f"Best Compiler Options: {best_individual}")
best_options = []
for i, bit in enumerate(best_individual):
    if bit == 1:
        best_options.append(option[i])
print(f"Best Compiler Options: {' '.join(best_options)}\n")
with open(PROGRAM_OUTPUT, 'w') as f:
    f.write(f"Optimization Complete. Best Fitness: {best_fitness:.4f}\nBest Compiler Options: {best_individual}\nBest Compiler Options: {' '.join(best_options)}")

