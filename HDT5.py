import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42

def proceso(nombre, env, ram, cpu, velocidad_cpu, tiempo_totales):
    tiempo_llegada = env.now
    memoria_necesaria = random.randint(1, 10)
    instrucciones = random.randint(1, 10)

    with ram.get(memoria_necesaria) as req_ram:
        yield req_ram

        while instrucciones > 0:
            with cpu.request() as req_cpu:
                yield req_cpu

                yield env.timeout(1)
                instrucciones -= velocidad_cpu
                
                if instrucciones > 0:
                    suerte = random.randit(1, 21)
                    if suerte == 1:
                        yield env.timeout(1)

                        ram.put(memoria_necesaria)
                        tiempo_total = env.now - tiempo_llegada
                        tiempos_totales.append(tiempo_total)

def correr_simulacion(num_procesos, intervalo, ram_cap, cpu_cap, velocidad_cpu):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_cap, capacity=ram_cap)
    cpu = simpy.Resource(env, capacity=cpu_cap)
    tiempos_totales = []

    def generador_procesos(env, ram, cpu, velocidad_cpu, tiempos_totales):
        for i in range(num_procesos):
            env.process(proceso(env, f'Proceso-{i}', ram, cpu, velocidad_cpu, tiempos_totales))
            t = random.expovariate(1.0 / intervalo)
            yield env.timeout(t)
            env.process(generador_procesos())
            env.run()

            return np.mean(tiempos_totales), np.std(tiempos_totales)
def ejecutar_experimentos_y_graficar(nombre_experimento, ram_cap, cpu_cap, velocidad_cpu, archivo_salida):
    cantidades_procesos = [25, 50, 100, 150, 200]
    intervalos = [10, 5, 1]

    plt.figure(figsize=(10, 6))

    