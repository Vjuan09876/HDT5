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
                suerte = random.randint(1, 21)
                if suerte == 1:
                    yield env.timeout(1) 

        ram.put(memoria_necesaria)
        tiempo_total = env.now - tiempo_llegada
        tiempo_totales.append(tiempo_total)

def correr_simulacion(num_procesos, intervalo, ram_cap, cpu_cap, velocidad_cpu):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_cap, capacity=ram_cap)
    cpu = simpy.Resource(env, capacity=cpu_cap)
    tiempos_totales = []

    def generador_procesos(env, ram, cpu, velocidad_cpu, tiempos_totales):
        for i in range(num_procesos):
            env.process(proceso(f'Proceso-{i}', env, ram, cpu, velocidad_cpu, tiempos_totales))
            t = random.expovariate(1.0 / intervalo)
            yield env.timeout(t)

    env.process(generador_procesos(env, ram, cpu, velocidad_cpu, tiempos_totales))
    
    env.run() 
    
    if not tiempos_totales:
        return 0, 0
    return np.mean(tiempos_totales), np.std(tiempos_totales)

def ejecutar_experimentos_y_graficar(nombre_experimento, ram_cap, cpu_cap, velocidad_cpu, archivo_salida):
    cantidades_procesos = [25, 50, 100, 150, 200]
    intervalos = [10, 5, 1]

    plt.figure(figsize=(10, 6))
    print(f"\n{nombre_experimento}")
    print(f"(ram: {ram_cap}, cpu: {cpu_cap}, velocidad cpu {velocidad_cpu})")
    print(f"{'Procesos':<10} | {'Intervalo':<10} | {'Promedio':<10} | {'Desviación':<10}")
    print("-" * 65)

    for intervalo in intervalos:
        promedios = []
        for num in cantidades_procesos:
            prom, dev = correr_simulacion(num, intervalo, ram_cap, cpu_cap, velocidad_cpu)
            promedios.append(prom)
            print(f"{num:<10} | {intervalo:<10} | {prom:<10.2f} | {dev:<10.2f}")
        
        plt.plot(cantidades_procesos, promedios, marker='o', label=f'intervalo {intervalo}')

    plt.title(f'analisis de tiempos {nombre_experimento}')
    plt.xlabel('numero de procesos')
    plt.ylabel('tiempo promedio en el sistema')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(archivo_salida)
    print(f"resultados guardados en {archivo_salida}")

if __name__ == "__main__":

    ejecutar_experimentos_y_graficar("Sistema Base", 100, 1, 3, "1_sistema_base.png")
    ejecutar_experimentos_y_graficar("Estrategia A ram 200", 200, 1, 3, "2_estrategia_A_ram200.png")
    ejecutar_experimentos_y_graficar("Estrategia B CPU velocidad 6", 100, 1, 6, "3_estrategia_B_cpu_rapido.png")
    ejecutar_experimentos_y_graficar("Estrategia C 2 cpu", 100, 2, 3, "4_estrategia_C_dos_cpus.png")