import pulp

# 1. Definir datos básicos
conductores = ['Alberto', 'Bruno', 'Carlos']
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
turnos = ['Mañana', 'Noche']

# 2. Inicializar el problema
prob = pulp.LpProblem("Optimizacion_Turnos", pulp.LpMinimize)

# 3. Crear variables binarias (Ahora sí funcionará en la versión estable)
x = pulp.LpVariable.dicts("Turno",
                          ((c, d, t) for c in conductores for d in dias for t in turnos),
                          cat='Binary')

prob += 0, "Funcion_Objetivo_Arbitraria"

# 5. RESTRICCIONES
# A. Cobertura mínima: Al menos 1 taxi por turno ordinario
for d in dias:
    for t in turnos:
        if (d == 'Viernes' and t == 'Noche') or (d == 'Sábado' and t == 'Noche'):
            prob += pulp.lpSum([x[(c, d, t)] for c in conductores]) == 2
        else:
            prob += pulp.lpSum([x[(c, d, t)] for c in conductores]) >= 1

# B. Límite de fatiga: Máximo 5 turnos a la semana por conductor
for c in conductores:
    prob += pulp.lpSum([x[(c, d, t)] for d in dias for t in turnos]) <= 5

# C. Descanso entre jornadas: Si hace noche, no puede hacer la mañana siguiente
for c in conductores:
    for i in range(len(dias) - 1):
        prob += x[(c, dias[i], 'Noche')] + x[(c, dias[i+1], 'Mañana')] <= 1

# 6. Resolver
prob.solve()

# 7. Imprimir el cuadrante
print("Estado del Solver:", pulp.LpStatus[prob.status])
print("-" * 30)
for d in dias:
    print(f"--- {d} ---")
    for t in turnos:
        asignados = [c for c in conductores if pulp.value(x[(c, d, t)]) == 1.0]
        print(f"  {t}: {', '.join(asignados)}")