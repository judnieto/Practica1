# -*- coding: utf-8 -*-
"""
@author: Judit Nieto
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
from random import random, randint

N = 10
NPROD = 3
K=5

def delay(factor = 3):
    sleep(random()/factor)
    
def producer(storage, index, empty, non_empty): 
    prod=int(current_process().name.split('_')[1]) #Productor
    for v in range(N):
        empty[prod].acquire()  # empty(productor).wait()
        print (f"Producer {current_process().name} produciendo")
        delay(6)
        storage[index[prod]] += randint(0,10) # Producimos enteros aleatorios positivos
        index[prod]+=1
        non_empty[prod].release()  # non_empty(productor).signal()
        print (f"Producer {current_process().name} almacenado {storage[prod]}")
    # Se produce el elemento especial -1 para indicar el final de producción
    empty[prod].acquire()
    storage[K*prod+K-1] = -1
    non_empty[prod].release()
        
        
# minimo busca el índice del productor con el valor mínimo en storage 
# y que todavía está activo
def minimo (storage, activo, index):
    minprod = activo.index(True) # buscamos el índice del primero que esté 
                                 # activo para descartar los primeros que
                                 # no lo estén 
    for i in range (minprod, NPROD):
        if storage[i*K]<storage[minprod*K] and activo[i]:
            minprod=i
    min_arg = storage[minprod*K]
    for i in range (index[minprod]-1): # cuando obtenemos el mínimo movemos 
                                       # todos los elementos una posición 
                                       # hacia atrás
        storage[minprod*K+i]=storage[minprod*K+i+1]
    return min_arg, minprod


def consumer (storage, empty, non_empty, index):
    for v in range(NPROD):
        non_empty[v].acquire()   
    elem_consumidos=[] # lista con los elementos que hemos consumido
    prod_activo=[True]*NPROD # iniciamos una lista poniendo que todos los 
                             # productores están activos (True) y si nos 
                             # encontramos un -1 los ponemos como 
                             # inactivos (False)
    while (True in prod_activo):   
        min_value, minprod = minimo (storage, prod_activo, index) # tomamos el mínimo
        if min_value == -1:
            prod_activo[minprod]=False
        else:  
            empty[minprod].release()  # empty(minimo).signal()
            index[minprod]=index[minprod]-1 # consumimos un elemento y disminuímos en uno la posición 
            elem_consumidos.append(min_value) 
            print (f"Consumer {current_process().name} consumiendo {min_value}")
            non_empty[minprod].acquire() # non_empty(minimo).wait()
    print(f"Elementos consumidos = {elem_consumidos}")
    

def main():
    storage = Array('i', NPROD*K) 
    index = Array('i', NPROD)  # posición en la que va a almacenar
    for i in range (NPROD):
        index[i] = 0
    for i in range(NPROD*K):
        storage[i] = 0
        
    print ("Almacen inicial", storage[:], "indice", index) 
    
    # Lista de semáforos
    non_empty_array = [Semaphore(0) for i in range(NPROD)]
    empty_array = [BoundedSemaphore(K) for i in range(NPROD)]
    
    # Procesos de los productores
    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage,index, empty_array, non_empty_array))
                for i in range(NPROD) ]
    
    # Proceso del consumidor
    conslst = [Process(target=consumer,
                      name=f'cons_{i}',
                      args=(storage, empty_array, non_empty_array,index))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()
  

if __name__ == '__main__':
    main()
