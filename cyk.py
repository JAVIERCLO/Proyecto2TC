# cyk.py
# Implementación del algoritmo CYK (Cocke-Younger-Kasami)

from typing import Dict, Set, List, Tuple, Optional
from gramatica import Gramatica, Symbol, Production
import time

class Derivacion:
    """Representa un nodo de derivación en el parse tree"""
    def __init__(self, simbolo: Symbol, hijos: List['Derivacion'] = None, terminal: str = None):
        self.simbolo = simbolo
        self.hijos = hijos if hijos else []
        self.terminal = terminal  # Si es una hoja (terminal)
    
    def __repr__(self):
        if self.terminal:
            return f"{self.simbolo}({self.terminal})"
        return f"{self.simbolo}{self.hijos}"

class ResultadoCYK:
    """Resultado del algoritmo CYK"""
    def __init__(self, acepta: bool, tiempo: float, tabla: List[List[Dict[Symbol, List[Derivacion]]]] = None):
        self.acepta = acepta
        self.tiempo = tiempo
        self.tabla = tabla
        self.parse_tree = None
        
        if acepta and tabla:
            self.parse_tree = self._construir_parse_tree()
    
    def _construir_parse_tree(self) -> Optional[Derivacion]:
        """Construye el parse tree desde la tabla CYK"""
        if not self.tabla:
            return None
        
        n = len(self.tabla)
        simbolo_inicial = None
        
        # Buscar el símbolo inicial en la celda superior
        for simbolo, derivaciones in self.tabla[n-1][0].items():
            if derivaciones:
                simbolo_inicial = simbolo
                return derivaciones[0]
        
        return None
    
    def imprimir_parse_tree(self, nodo: Derivacion = None, nivel: int = 0, prefijo: str = "") -> str:
        """Imprime el parse tree en formato legible"""
        if nodo is None:
            nodo = self.parse_tree
        
        if nodo is None:
            return "No hay parse tree disponible"
        
        resultado = []
        
        # Imprimir el nodo actual
        if nodo.terminal:
            resultado.append(f"{prefijo}{nodo.simbolo} → '{nodo.terminal}'")
        else:
            resultado.append(f"{prefijo}{nodo.simbolo}")
        
        # Imprimir los hijos
        for i, hijo in enumerate(nodo.hijos):
            es_ultimo = (i == len(nodo.hijos) - 1)
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            conector = "└── " if es_ultimo else "├── "
            
            lineas_hijo = self.imprimir_parse_tree(hijo, nivel + 1, nuevo_prefijo)
            primera_linea = lineas_hijo.split('\n')[0]
            resultado.append(f"{prefijo}{conector}{primera_linea.strip()}")
            
            # Agregar el resto de las líneas con la indentación correcta
            for linea in lineas_hijo.split('\n')[1:]:
                if linea.strip():
                    resultado.append(linea)
        
        return '\n'.join(resultado)


def cyk(gramatica: Gramatica, cadena: str) -> ResultadoCYK:
    """
    Algoritmo CYK para determinar si una cadena pertenece al lenguaje
    generado por una gramática en CNF.
    
    Args:
        gramatica: Gramática en Forma Normal de Chomsky
        cadena: Cadena a validar (palabras separadas por espacios)
    
    Returns:
        ResultadoCYK con el resultado del parsing
    """
    inicio_tiempo = time.time()
    
    # Tokenizar la cadena (CONVERTIR a minúsculas)
    palabras = cadena.strip().lower().split()
    n = len(palabras)
    
    if n == 0:
        tiempo_transcurrido = time.time() - inicio_tiempo
        return ResultadoCYK(False, tiempo_transcurrido)
    
    # Crear tabla CYK: tabla[i][j] contiene los no terminales que derivan w[j]...w[j+i]
    # Para cada no terminal, guardamos una lista de posibles derivaciones
    tabla: List[List[Dict[Symbol, List[Derivacion]]]] = [
        [{} for _ in range(n)] for _ in range(n)
    ]
    
    # Paso 1: Llenar la primera fila (subcadenas de longitud 1)
    for j in range(n):
        palabra = palabras[j]
        
        # Buscar producciones A -> palabra (comparación exacta, case-sensitive)
        for A, producciones in gramatica.P.items():
            for produccion in producciones:
                # Producción A -> a (terminal único)
                if len(produccion) == 1 and produccion[0] == palabra:
                    if A not in tabla[0][j]:
                        tabla[0][j][A] = []
                    # Crear nodo hoja
                    derivacion = Derivacion(A, terminal=palabra)
                    tabla[0][j][A].append(derivacion)
    
    # Paso 2: Llenar el resto de la tabla (subcadenas de longitud > 1)
    for i in range(1, n):  # longitud - 1
        for j in range(n - i):  # posición inicial
            # Para cada forma de partir la subcadena
            for k in range(i):  # punto de partición
                # Mirar producciones A -> B C
                for A, producciones in gramatica.P.items():
                    for produccion in producciones:
                        if len(produccion) == 2:
                            B, C = produccion
                            
                            # Si B está en tabla[k][j] y C está en tabla[i-k-1][j+k+1]
                            if B in tabla[k][j] and C in tabla[i-k-1][j+k+1]:
                                if A not in tabla[i][j]:
                                    tabla[i][j][A] = []
                                
                                # Crear derivaciones combinando todas las posibles
                                for derivacion_B in tabla[k][j][B]:
                                    for derivacion_C in tabla[i-k-1][j+k+1][C]:
                                        nueva_derivacion = Derivacion(
                                            A, 
                                            hijos=[derivacion_B, derivacion_C]
                                        )
                                        tabla[i][j][A].append(nueva_derivacion)
    
    # Verificar si el símbolo inicial está en la celda superior
    acepta = gramatica.S in tabla[n-1][0] and len(tabla[n-1][0][gramatica.S]) > 0
    
    tiempo_transcurrido = time.time() - inicio_tiempo
    
    return ResultadoCYK(acepta, tiempo_transcurrido, tabla if acepta else None)


def imprimir_tabla_cyk(tabla: List[List[Dict[Symbol, List[Derivacion]]]], palabras: List[str]):
    """Imprime la tabla CYK de forma legible"""
    n = len(palabras)
    
    print("\nTabla CYK:")
    print("=" * 80)
    
    # Caso especial: oración de 1 palabra
    if n == 1:
        print(f"\nLongitud 1:")
        simbolos = list(tabla[0][0].keys())
        if simbolos:
            print(f"  [0:1] '{palabras[0].lower()}': {{{', '.join(sorted(simbolos))}}}")
        return
    
    for i in range(n-1, -1, -1):
        print(f"\nLongitud {i+1}:")
        for j in range(n - i):
            simbolos = list(tabla[i][j].keys())
            if simbolos:
                rango = f"[{j}:{j+i+1}]"
                subcadena = " ".join(palabras[j:j+i+1])
                print(f"  {rango} '{subcadena.lower()}': {{{', '.join(sorted(simbolos))}}}")