#Eliminación de producciones unarias tipo A -> B

from typing import Set, Tuple
from gramatica import Gramatica, Symbol, Production, es_no_terminal

def es_produccion_unitaria(produccion: Production, gramatica: Gramatica) -> bool:
    return (len(produccion) == 1) and es_no_terminal(produccion[0])

def encontrar_pares_unitarios(gramatica: Gramatica) -> Set[Tuple[Symbol, Symbol]]:
    pares: Set[Tuple[Symbol, Symbol]] = set()
    for A in gramatica.NT:
        pares.add((A, A))

    cambio = True
    while cambio:
        cambio = False
        #Si tenemos (A, B) y B -> C es una producción unaria, agregamos (A, C)
        for A, B in list(pares):
            for produccion in gramatica.P.get(B, ()):
                if es_produccion_unitaria(produccion, gramatica):
                    C = produccion[0]
                    if (A, C) not in pares:
                        pares.add((A, C))
                        cambio = True
    return pares

def eliminar_unarias(gramatica: Gramatica) -> Gramatica:

    #nueva gramática
    gramatica_sin_unarias = Gramatica()
    gramatica_sin_unarias.NT = set(gramatica.NT)
    gramatica_sin_unarias.T  = set(gramatica.T)
    gramatica_sin_unarias.S  = gramatica.S
    gramatica_sin_unarias.P  = {A: set() for A in gramatica.P.keys()}

    clausura = encontrar_pares_unitarios(gramatica)

    for A, B in clausura:
        for produccion in gramatica.P.get(B, ()):
            if not es_produccion_unitaria(produccion, gramatica):
                gramatica_sin_unarias.P.setdefault(A, set()).add(produccion)

    for A in gramatica_sin_unarias.NT:
        gramatica_sin_unarias.P.setdefault(A, set())

    return gramatica_sin_unarias