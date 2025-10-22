# Eliminación de símbolos inútiles

from typing import Set, Dict
from gramatica import Gramatica, Symbol, Production, es_no_terminal

#Símbolos que no producen
def encontrar_no_terminales_productivos(gramatica: Gramatica) -> Set[Symbol]:
    productivos: Set[Symbol] = set()
    cambio = True
    while cambio:
        cambio = False
        for A, producciones in gramatica.P.items():
            if A in productivos:
                continue
            for produccion in producciones:
                es_productiva = True
                for simbolo in produccion:
                    if es_no_terminal(simbolo):
                        if simbolo not in productivos:
                            es_productiva = False
                            break
                    # si es terminal: ok
                if es_productiva:
                    productivos.add(A)
                    cambio = True
                    break
    return productivos

def eliminar_no_productivos(gramatica: Gramatica) -> Gramatica:

    gramatica_sin_productivos = Gramatica()
    gramatica_sin_productivos.NT = set(gramatica.NT)
    gramatica_sin_productivos.T  = set(gramatica.T)
    gramatica_sin_productivos.S  = gramatica.S
    gramatica_sin_productivos.P  = {A: set(prods) for A, prods in gramatica.P.items()}

    productivos = encontrar_no_terminales_productivos(gramatica_sin_productivos)

    # Conservar solo NT productivos
    gramatica_sin_productivos.NT = {A for A in gramatica_sin_productivos.NT if A in productivos}

    # Filtrar P (quitar reglas con NT no productivos)
    nuevoP: Dict[Symbol, set[Production]] = {}
    for A, prods in gramatica_sin_productivos.P.items():
        if A not in gramatica_sin_productivos.NT:
            continue
        filtradas = set()
        for p in prods:
            if all((not es_no_terminal(s)) or (s in gramatica_sin_productivos.NT) for s in p):
                filtradas.add(p)
        nuevoP[A] = filtradas
    gramatica_sin_productivos.P = nuevoP

    # Recalcular T
    gramatica_sin_productivos.T = set()
    for prods in gramatica_sin_productivos.P.values():
        for p in prods:
            for s in p:
                if not es_no_terminal(s):
                    gramatica_sin_productivos.T.add(s)

    # Asegurar S sin meter None
    if gramatica_sin_productivos.S is not None and gramatica_sin_productivos.S not in gramatica_sin_productivos.NT:
        gramatica_sin_productivos.NT.add(gramatica_sin_productivos.S)
        gramatica_sin_productivos.P.setdefault(gramatica_sin_productivos.S, set())

    return gramatica_sin_productivos

# --- alcanzables ---
def encontrar_no_terminales_alcanzables(gramatica: Gramatica) -> Set[Symbol]:
    if gramatica.S is None:
        return set()
    alcanzables: Set[Symbol] = {gramatica.S}
    cambio = True
    while cambio:
        cambio = False
        for A in list(alcanzables):
            for produccion in gramatica.P.get(A, ()):
                for simbolo in produccion:
                    if es_no_terminal(simbolo) and simbolo not in alcanzables:
                        alcanzables.add(simbolo)
                        cambio = True
    return alcanzables

def eliminar_no_alcanzables(gramatica: Gramatica) -> Gramatica:
    
    gramatica_sin_inalcanzables = Gramatica()
    gramatica_sin_inalcanzables.NT = set(gramatica.NT)
    gramatica_sin_inalcanzables.T  = set(gramatica.T)
    gramatica_sin_inalcanzables.S  = gramatica.S
    gramatica_sin_inalcanzables.P  = {A: set(prods) for A, prods in gramatica.P.items()}

    alcanzables = encontrar_no_terminales_alcanzables(gramatica_sin_inalcanzables)

    # Conservar solo alcanzables
    gramatica_sin_inalcanzables.NT = {A for A in gramatica_sin_inalcanzables.NT if A in alcanzables}

    nuevoP: Dict[Symbol, set[Production]] = {}
    for A, prods in gramatica_sin_inalcanzables.P.items():
        if A not in gramatica_sin_inalcanzables.NT:
            continue
        filtradas = set()
        for p in prods:
            if all((not es_no_terminal(s)) or (s in gramatica_sin_inalcanzables.NT) for s in p):
                filtradas.add(p)
        nuevoP[A] = filtradas
    gramatica_sin_inalcanzables.P = nuevoP

    # Recalcular T
    gramatica_sin_inalcanzables.T = set()
    for prods in gramatica_sin_inalcanzables.P.values():
        for p in prods:
            for s in p:
                if not es_no_terminal(s):
                    gramatica_sin_inalcanzables.T.add(s)

    # Asegurar que halla simbolo inicial
    if gramatica_sin_inalcanzables.S is not None and gramatica_sin_inalcanzables.S not in gramatica_sin_inalcanzables.NT:
        gramatica_sin_inalcanzables.NT.add(gramatica_sin_inalcanzables.S)
        gramatica_sin_inalcanzables.P.setdefault(gramatica_sin_inalcanzables.S, set())

    return gramatica_sin_inalcanzables

def eliminar_simbolos_inutiles(gramatica: Gramatica) -> Gramatica:
    sin_no_productivos = eliminar_no_productivos(gramatica)
    sin_no_alcanzables = eliminar_no_alcanzables(sin_no_productivos)
    return sin_no_alcanzables