# cnf.py
# Conversión a Forma Normal de Chomsky (CNF)

import re
from typing import Dict, Set, Tuple, List

from gramatica import Gramatica, Symbol, Production, es_no_terminal

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def _sanear_nombre_terminal(t: str) -> str:
    """
    Convierte un terminal cualquiera en un fragmento "seguro" para usar en un no terminal:
      '+' -> 'plus', '*' -> 'mul', '(' -> 'lpar', ')' -> 'rpar', etc.
    Para el resto, reemplaza caracteres no alfanum por '_' y evita empezar con dígito.
    """
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
    """
    Genera un no terminal nuevo que no colisione con NT, T ni claves de P.
    Debe empezar con mayúscula para cumplir tu heurística de no terminal.
    """
    k = 1
    nuevo_simbolo = base if base and base[0].isupper() else ("X_" + str(k))
    usados = set(gramatica.NT) | set(gramatica.T) | set(gramatica.P.keys())
    while nuevo_simbolo in usados:
        k += 1
        nuevo_simbolo = f"{base}_{k}"
    return nuevo_simbolo

def _variable_para_terminal(gramatica: Gramatica,
                            t: Symbol,
                            memo: Dict[Symbol, Symbol]) -> Symbol:
    """
    Devuelve un no terminal (p.ej. T_plus) que derive el terminal t: T_plus -> t.
    Reutiliza el mismo para el mismo t (memo).
    """
    if t in memo:
        return memo[t]
    nombre_seguro = _sanear_nombre_terminal(t)
    base = f"T_{nombre_seguro}"
    if not base[0].isupper():
        base = "T_" + base
    var = _nueva_variable(gramatica, base)
    gramatica.NT.add(var)
    gramatica.P.setdefault(var, set()).add((t,))  # var -> t
    memo[t] = var
    return var

# ---------------------------------------------------
# Conversión principal a CNF
# ---------------------------------------------------

def convertir_a_cnf(gramatica: Gramatica) -> Gramatica:
    """
    Devuelve una gramática equivalente en CNF.
    Reglas finales solo en las formas:
      A -> a
      A -> B C
    y (siempre) S0 -> S como nuevo símbolo inicial.

    **Supone** que ya no hay ε (salvo el caso manejado con S0) ni producciones unitarias.
    """
    # 0) Clonar
    g = Gramatica()
    g.NT = set(gramatica.NT)
    g.T  = set(gramatica.T)
    g.S  = gramatica.S
    g.P  = {A: set(prods) for A, prods in gramatica.P.items()}

    # 1) Introducir nuevo inicio S0 -> S (estándar)
    s0 = _nueva_variable(g, base="S0")
    g.NT.add(s0)
    # En lugar de S0 -> S, copiamos todas las producciones de S a S0
    if g.S in g.P:
        for produccion in g.P[g.S]:
            g.P.setdefault(s0, set()).add(produccion)
    g.S = s0

    # 2) Sustituir terminales dentro de producciones de longitud >= 2 por variables T_x
    mapa_terminales: Dict[Symbol, Symbol] = {}
    producciones_transformadas: Dict[Symbol, Set[Production]] = {}

    for A, producciones in list(g.P.items()):
        producciones_transformadas[A] = set()
        for produccion in producciones:
            # Caso A -> a (terminal único): ya es CNF, lo dejamos
            if len(produccion) == 1 and not es_no_terminal(produccion[0]):
                producciones_transformadas[A].add(produccion)
                continue
            # Caso A -> B (unitaria): no debería aparecer tras el paso de unitarias;
            # si aparece, la dejamos pasar (o podrías assert False).
            if len(produccion) == 1 and es_no_terminal(produccion[0]):
                producciones_transformadas[A].add(produccion)
                continue

            # Longitud >= 2: reemplazar cualquier terminal por su variable T_x
            nueva: List[Symbol] = []
            for simbolo in produccion:
                if es_no_terminal(simbolo):
                    nueva.append(simbolo)
                else:
                    v = _variable_para_terminal(g, simbolo, mapa_terminales)
                    nueva.append(v)
            producciones_transformadas[A].add(tuple(nueva))

    g.P = producciones_transformadas

    # 3) Binarizar (A -> X1 X2 ... Xn con n>=3)
    finales: Dict[Symbol, Set[Production]] = {}

    for A, producciones in g.P.items():
        finales[A] = set()
        for produccion in producciones:
            n = len(produccion)
            if n <= 2:
                # Ya es CNF (A -> a o A -> B C)
                finales[A].add(produccion)
                continue

            # Binarización encadenada para n >= 3
            simbolos = list(produccion)
            izquierda_actual = A

            while len(simbolos) > 2:
                Z = _nueva_variable(g, base="X")
                g.NT.add(Z)
                finales.setdefault(Z, set())
                # izquierda_actual -> simbolos[0] Z
                finales[izquierda_actual].add((simbolos[0], Z))
                # Z recibirá el resto más adelante
                izquierda_actual = Z
                simbolos = simbolos[1:]

            # Última regla binaria: izquierda_actual -> s_{-2} s_{-1}
            finales[izquierda_actual].add((simbolos[0], simbolos[1]))

    # Reemplazar P por las finales (ya binarias o unitarias válidas A->a)
    g.P = finales

    # 4) Asegurar que todas las claves de P existan
    for A in g.NT:
        g.P.setdefault(A, set())

    return g