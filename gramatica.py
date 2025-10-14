#Representación de la gramática, parser y validación.

from typing import Dict,Set, Tuple

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
        if simbolo and simbolo[0].islower(): #Asegurar que el Terminal inicie con minúscula
            self.T.add(simbolo)
        else:
            raise ValueError("El símbolo de terminal debe comenzar con una letra minúscula.")

    def definir_simbolo_inicial(self, simbolo: Symbol):
        self.S = simbolo
        self.agregar_no_terminal(simbolo)  #Asegurar que el símbolo inicial sea un no terminal

    def agregar_produccion(self, no_terminal: Symbol, produccion: Production):
        if no_terminal not in self.NT:
            self.agregar_no_terminal(no_terminal)

            if isinstance(produccion, str):
                produccion = (produccion)
            elif isinstance(produccion, list):
                produccion = tuple(produccion)

            self.P.setdefault(no_terminal, set()).add(produccion)

            for simbolo in produccion:
                if simbolo.isupper():
                    self.agregar_no_terminal(simbolo)
                elif simbolo.islower():
                    self.agregar_terminal(simbolo)
                elif simbolo == 'ε':
                    continue
                else:
                    raise ValueError("Los símbolos deben empezar con mayúscula (no terminal) o minúscula (terminal).")
                
    def format(self) -> str:
        gramatica_formateada = []
        gramatica_formateada.append(f"No terminales: {', '.join(sorted(self.NT))}")
        gramatica_formateada.append(f"Terminales: {', '.join(sorted(self.T))}")
        gramatica_formateada.append(f"Símbolo inicial: {self.S}")
        gramatica_formateada.append("Producciones:")
        for I, producciones in self.P.items():
            derivaciones = [" ".join(i) for i in producciones]
            gramatica_formateada.append(f"  {I} -> {' | '.join(derivaciones)}")
        return "\n".join(gramatica_formateada)