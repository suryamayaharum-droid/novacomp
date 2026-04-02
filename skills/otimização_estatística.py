
# Auto-generated Skill by NovaComp Evolution Engine
# Date: 2026-04-02T21:24:38.230544
# Author: NovaComp-Auto
# Description: Calcula variância para otimização de processos internos
# Safety Hash: a11325ac0fc59df0


def calculate_optimization_score(data_points):
    import math
    if not data_points:
        return 0.0
    avg = sum(data_points) / len(data_points)
    variance = sum((x - avg) ** 2 for x in data_points) / len(data_points)
    return math.sqrt(variance)

