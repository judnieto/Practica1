# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 13:11:44 2023

@author: jc
"""

from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
from random import random, randint

N = 10
NPROD = 3

def delay(factor = 3):
    sleep(random()/factor)
    
def producer(storage, index, empty, non_empty): 
    pid=int(current_process().name.split('_')[1]) #Productor
    for v in range(N):
        empty[pid].acquire()  # empty(productor).wait()
        print (f"Producer {current_process().name} produciendo")
        delay(6)
        storage[pid] += randint(0,10) # Producimos enteros aleatorios positivos
        non_empty[pid].release()  # non_empty(productor).signal()
        print (f"Producer {current_process().name} almacenado {storage[pid]}")
    # Se produce el elemento especial -1 para indicar el final de producción
    empty[pid].acquire()
    storage[pid] = -1
    non_empty[pid].release()
        
        
# minimo busca el índice del productor con el valor mínimo en storage 
# y que todavía está activo
def minimo (storage, activo):
    index_value = activo.index(True) # buscamos el índice del primero que esté 
                                     # activo para descartar los primeros que
                                     # no lo estén 
    for i in range (index_value, NPROD):
        if storage[i]<storage[index_value] and activo[i]:
            index_value=i
    min_arg = storage[index_value]
    return min_arg, index_value


def consumer (storage, empty, non_empty):
    for v in range(NPROD):
        non_empty[v].acquire()   
    elem_consumidos=[] # lista con los elementos que hemos consumido
    prod_activo=[True]*NPROD # iniciamos una lista poniendo que todos los 
                             # productores están activos (True) y si nos 
                             # encontramos un -1 los ponemos como 
                             # inactivos (False)
    while (True in prod_activo):   
        min_value, index = minimo (storage, prod_activo) # tomamos el mínimo
        if min_value == -1:
            prod_activo[index]=False
        else:  
            empty[index].release()  # empty(minimo).signal()
            elem_consumidos.append(min_value) 
            print (f"Consumer {current_process().name} consumiendo {min_value}")
            non_empty[index].acquire() # non_empty(minimo).wait()
    print(f"Elementos consumidos = {elem_consumidos}")
    

def main():
    storage = Array('i', NPROD)
    index = Array('i', NPROD)
    for i in range(NPROD):
        storage[i] = 0
        
    print ("Almacen inicial", storage[:], "indice", index) 
    
    # Lista de semáforos
    non_empty_array = [Semaphore(0) for i in range(NPROD)]
    empty_array = [Lock() for i in range(NPROD)]
    
    # Procesos de los productores
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage,index, empty_array, non_empty_array))
                for i in range(NPROD) ]
    
    # Proceso del consumidor
    conslst = [Process(target=consumer,
                      name=f'cons_{i}',
                      args=(storage, empty_array, non_empty_array))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()
  

if __name__ == '__main__':
    main()
