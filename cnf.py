# Conversión a Forma Normal de Chomsky (CNF)
import re
from typing import Dict, Set, List

from gramatica import Gramatica, Symbol, Production, es_no_terminal
#Cambiar nombre de terminales especiales para mejor lectura
def cambiar_nombre_terminal(t: str) -> str:
    especiales = {
        '+': 'plus', '-': 'minus', '*': 'mul', '/': 'div',
        '(': 'lpar', ')': 'rpar', '[': 'lbrack', ']': 'rbrack',
        '{': 'lbrace', '}': 'rbrace', '=': 'eq', '<': 'lt', '>': 'gt',
        '|': 'bar', '&': 'and', '^': 'xor', '%': 'mod', '!': 'bang',
        '?': 'q', ':': 'colon', ';': 'semi', ',': 'comma', '.': 'dot',
        "'": 'apos', '"': 'quot', '\\': 'bslash', '#': 'hash', '@': 'at',
        '$': 'dollar', '~': 'tilde'
    }
    if t in especiales:
        s = especiales[t]
    else:
        s = re.sub(r'[^A-Za-z0-9_]', '_', t)
        if s and s[0].isdigit():
            s = f"tok_{s}"
        if not s:
            s = "tok"
    return s

def _nueva_variable(gramatica: Gramatica, base: str = "X") -> Symbol:
    k = 1
    nuevo_simbolo = base if base and base[0].isupper() else ("X_" + str(k))
    usados = set(gramatica.NT) | set(gramatica.T) | set(gramatica.P.keys())
    while nuevo_simbolo in usados:
        k += 1
        nuevo_simbolo = f"{base}_{k}"
    return nuevo_simbolo

def _variable_para_terminal(gramatica: Gramatica, t: Symbol, memo: Dict[Symbol, Symbol]) -> Symbol:
    if t in memo:
        return memo[t]
    nombre_seguro = cambiar_nombre_terminal(t)
    base = f"T_{nombre_seguro}"
    if not base[0].isupper():
        base = "T_" + base
    var = _nueva_variable(gramatica, base)
    gramatica.NT.add(var)
    gramatica.P.setdefault(var, set()).add((t,))
    memo[t] = var
    return var

def convertir_a_cnf(gramatica: Gramatica) -> Gramatica:
    #gramática final
    gramatica_final = Gramatica()
    gramatica_final.NT = set(gramatica.NT)
    gramatica_final.T  = set(gramatica.T)
    gramatica_final.S  = gramatica.S
    gramatica_final.P  = {A: set(prods) for A, prods in gramatica.P.items()}

    # S0 -> S
    s0 = _nueva_variable(gramatica_final, base="S0")
    gramatica_final.NT.add(s0)
    gramatica_final.P.setdefault(s0, set()).add((gramatica_final.S,))
    gramatica_final.S = s0

    # sustituir terminales en reglas de longitud >= 2
    mapa_terminales: Dict[Symbol, Symbol] = {}
    producciones_transformadas: Dict[Symbol, Set[Production]] = {A: set() for A in gramatica_final.P}

    for A, producciones in list(gramatica_final.P.items()):
        for produccion in producciones:
            if len(produccion) == 1 and not es_no_terminal(produccion[0]):
                producciones_transformadas.setdefault(A, set()).add(produccion)
                continue
            if len(produccion) == 1 and es_no_terminal(produccion[0]):
                producciones_transformadas.setdefault(A, set()).add(produccion)
                continue

            nueva: List[Symbol] = []
            for simbolo in produccion:
                if es_no_terminal(simbolo):
                    nueva.append(simbolo)
                else:
                    v = _variable_para_terminal(gramatica_final, simbolo, mapa_terminales)
                    nueva.append(v)
            producciones_transformadas.setdefault(A, set()).add(tuple(nueva))

    gramatica_final.P = producciones_transformadas

    # binarizar reglas con longitud > 2
    finales: Dict[Symbol, Set[Production]] = {A: set() for A in gramatica_final.P}

    for A, producciones in gramatica_final.P.items():
        for produccion in producciones:
            n = len(produccion)
            if n <= 2:
                finales.setdefault(A, set()).add(produccion)
                continue

            simbolos = list(produccion)
            izquierda_actual = A
            while len(simbolos) > 2:
                Z = _nueva_variable(gramatica_final, base="X")
                gramatica_final.NT.add(Z)
                finales.setdefault(izquierda_actual, set()).add((simbolos[0], Z))
                izquierda_actual = Z
                simbolos = simbolos[1:]
            finales.setdefault(izquierda_actual, set()).add((simbolos[0], simbolos[1]))

    gramatica_final.P = finales

    for A in gramatica_final.NT:
        gramatica_final.P.setdefault(A, set())

    return gramatica_final
