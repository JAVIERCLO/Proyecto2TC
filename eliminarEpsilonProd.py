# Eliminación de producciones epsilon

from typing import Set, Dict, List
from itertools import combinations
from gramatica import Gramatica, Symbol, Production

#Encontrar no terminales anulables
def encontrar_anulables(gramatica: Gramatica) -> Set[Symbol]:
    anulables: Set[Symbol] = set()
    cambio = True

    while cambio:
        cambio = False
        for no_terminal, producciones in gramatica.P.items():
            if no_terminal in anulables:
                continue

            # Caso 1: A -> ε
            if any(len(p) == 0 for p in producciones):
                anulables.add(no_terminal)
                cambio = True
                continue

            # Caso 2: A -> X1 X2 ... Xn, cuando todos los X son anulables
            for produccion in producciones:
                if len(produccion) == 0:
                    continue
                todos_anulables = True
                for simbolo in produccion:
                    if simbolo not in gramatica.NT or simbolo not in anulables:
                        todos_anulables = False
                        break
                if todos_anulables:
                    anulables.add(no_terminal)
                    cambio = True
                    break

    return anulables



# 2)eliminar producciones epsilon
def eliminar_epsilon(gramatica: Gramatica) -> Gramatica:

    #Crear la nueva gramática
    nueva = Gramatica()
    nueva.NT = set(gramatica.NT)
    nueva.T  = set(gramatica.T)
    nueva.S  = gramatica.S
    nueva.P  = {A: set(prods) for A, prods in gramatica.P.items()}

    anulables = encontrar_anulables(nueva)

    #Para símbolo inicial anulable
    if nueva.S in anulables:
        s0 = _nueva_variable(nueva, base="S0")
        nueva.NT.add(s0)
        nueva.P.setdefault(s0, set()).add((nueva.S,))  # S0 -> S
        nueva.P[s0].add(tuple())                       # S0 -> ε
        nueva.S = s0

    #Construir nuevas producciones sin epsion
    nuevoP: Dict[Symbol, Set[Production]] = {A: set() for A in nueva.P.keys()}

    for A, producciones in nueva.P.items():
        for produccion in producciones:
            if len(produccion) == 0:
                continue

            #Posiciones donde el símbolo es no terminal anulable
            pos_anulables: List[int] = [
                i for i, simbolo in enumerate(produccion)
                if (simbolo in nueva.NT and simbolo in anulables)
            ]

            variantes: Set[Production] = set()
            variantes.add(produccion)

            for r in range(1, len(pos_anulables) + 1):
                for combo in combinations(pos_anulables, r):
                    combo_set = set(combo)
                    nueva_produccion = tuple(
                        s for i, s in enumerate(produccion) if i not in combo_set
                    )
                    if len(nueva_produccion) > 0:
                        variantes.add(nueva_produccion)
                    # Si queda vacía, no se agrega

            nuevoP[A] |= variantes

    nueva.P = nuevoP
    return nueva


#Crear el nuevo no terminal
def _nueva_variable(gramatica: Gramatica, base: str = "X") -> Symbol:
    k = 1
    nuevo_simbolo = base
    usados = set(gramatica.NT) | set(gramatica.T) | set(gramatica.P.keys())
    while nuevo_simbolo in usados:
        k += 1
        nuevo_simbolo = f"{base}_{k}"
    return nuevo_simbolo
