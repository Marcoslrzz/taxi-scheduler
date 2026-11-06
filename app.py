from flask import Flask, render_template, request, jsonify
import pulp

app = Flask(__name__)

@app.route('/')
def home():
    # Esto carga la página web que yo he diseñado
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    # 1. Recibimos los conductores desde la web
    datos = request.json
    conductores = datos.get('conductores', [])
    
    if len(conductores) < 4:
        return jsonify({"error": "Matemáticamente imposible. Necesitas al menos 4 conductores."}), 400

    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    turnos = ['Mañana', 'Noche']

    # 2. Inicializar el problema de Pulp
    prob = pulp.LpProblem("Optimizacion_Turnos", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("Turno", ((c, d, t) for c in conductores for d in dias for t in turnos), cat='Binary')
    prob += 0, "Funcion_Objetivo_Arbitraria"

    # 3. Restricciones
    for d in dias:
        for t in turnos:
            if (d == 'Viernes' and t == 'Noche') or (d == 'Sábado' and t == 'Noche'):
                prob += pulp.lpSum([x[(c, d, t)] for c in conductores]) == 2
            else:
                prob += pulp.lpSum([x[(c, d, t)] for c in conductores]) >= 1

    for c in conductores:
        prob += pulp.lpSum([x[(c, d, t)] for d in dias for t in turnos]) <= 5

    for c in conductores:
        for i in range(len(dias) - 1):
            prob += x[(c, dias[i], 'Noche')] + x[(c, dias[i+1], 'Mañana')] <= 1

    # 4. Resolver
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        return jsonify({"error": "No hay solución factible con estos datos."}), 400

    # 5. Formatear el resultado para enviarlo de vuelta a la web
    cuadrante = {}
    for d in dias:
        cuadrante[d] = {}
        for t in turnos:
            asignados = [c for c in conductores if pulp.value(x[(c, d, t)]) == 1.0]
            cuadrante[d][t] = ", ".join(asignados)

    return jsonify({"cuadrante": cuadrante})

if __name__ == '__main__':
    app.run(debug=True)