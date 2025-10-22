#Representación de la gramática, parser y validación.

from typing import Dict,Set, Tuple, Iterable
import re

Symbol = str
Production = Tuple[Symbol, ...]

class Gramatica:
#Constructor
    def __init__(self):
        # Conjuntos de símbolos
        self.NT: Set[Symbol] = set()    # No terminales
        self.T: Set[Symbol] = set()     # Terminales
        self.S: Symbol | None = None    # Símbolo inicial
        self.P: Dict[Symbol, Set[Production]] = {}  # Producciones

    def agregar_no_terminal(self, simbolo: Symbol):
        if simbolo and simbolo[0].isupper(): #Asegurar que el No terminal inicie con mayúscula
            self.NT.add(simbolo)
        else:
            raise ValueError("El símbolo de no terminal debe comenzar con una letra mayúscula.")

    def agregar_terminal(self, simbolo: Symbol):
        
        if not simbolo:
            raise ValueError("El símbolo de terminal no puede ser vacío.")
        if simbolo == 'ε':
            return
        self.T.add(simbolo)

    def definir_simbolo_inicial(self, simbolo: Symbol):
        self.S = simbolo
        self.agregar_no_terminal(simbolo)  #Asegurar que el símbolo inicial sea un no terminal

    def agregar_produccion(self, no_terminal: Symbol, produccion: Production):
        if no_terminal not in self.NT:
            self.agregar_no_terminal(no_terminal)

        if isinstance(produccion, str):
            produccion = (produccion,)
        elif isinstance(produccion, list):
            produccion = tuple(produccion)

        self.P.setdefault(no_terminal, set()).add(produccion)
        for simbolo in produccion:
            if simbolo == 'ε':
                continue
            if es_no_terminal(simbolo):
                self.agregar_no_terminal(simbolo)
            else:
                self.agregar_terminal(simbolo)
                
    def format(self) -> str:
        nt_list = [x for x in self.NT if x is not None]
        gramatica_formateada = []
        gramatica_formateada.append(f"No terminales: {', '.join(sorted(nt_list))}")
        gramatica_formateada.append(f"Terminales: {', '.join(sorted(self.T))}")
        gramatica_formateada.append(f"Símbolo inicial: {self.S}")
        gramatica_formateada.append("Producciones:")
        for A, producciones in self.P.items():
            derivaciones = [" ".join(p) if p else "ε" for p in producciones]
            gramatica_formateada.append(f"  {A} -> {' | '.join(sorted(derivaciones))}")
        return "\n".join(gramatica_formateada)

    

NT_REGEX = re.compile(r"[A-Z][A-Za-z0-9_]*")

def es_no_terminal(simbolo: Symbol) -> bool:
    return bool(NT_REGEX.fullmatch(simbolo))

def parsear_derivacion(derivacion: str) -> Production:

    derivacion = derivacion.strip()
    if derivacion == "ε":
        return tuple()
    tokens = derivacion.split()
    return tuple(tokens)

def parsear_reglas(lines: Iterable[str], inicio: Symbol) -> "Gramatica":
    gramatica = Gramatica()
    gramatica.definir_simbolo_inicial(inicio)

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if "->" not in line:
            raise ValueError(f"Producción inválida, falta '->': {raw}")

        left, right = map(str.strip, line.split("->", 1))

        # El lado izquierdo debe ser No Terminal
        if not es_no_terminal(left):
            raise ValueError(f"El lado izquierdo debe ser no terminal: '{left}'")

        #Dividir las producciones por '|'
        for alt in right.split("|"):
            alt = alt.strip()
            if not alt:
                raise ValueError(f"Producción vacía en línea: {raw}")
            prod = parsear_derivacion(alt)
            gramatica.agregar_produccion(left, prod)

    return gramatica

def procesar_archivo(path: str, inicio: Symbol) -> "Gramatica":
    with open(path, "r", encoding="utf-8") as file:
        return parsear_reglas(file, inicio)