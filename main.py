# main.py
# Módulo principal para llamar a las funciones de los otros módulos
from gramatica import procesar_archivo
from eliminarEpsilonProd import encontrar_anulables, eliminar_epsilon
from eliminarUnariasProd import eliminar_unarias
from eliminarSimbolosInutiles import eliminar_simbolos_inutiles
from cnf import convertir_a_cnf
from cyk import cyk, imprimir_tabla_cyk

def main():
    archivo = "gramaticas/gramaticaProyecto.txt"
    simbolo_inicial = "S"

    print("="*80)
    print("ANALIZADOR SINTÁCTICO CON CYK")
    print("="*80)

    # Cargar la gramática desde archivo
    print("\n[1] Cargando gramática desde archivo...")
    gramatica = procesar_archivo(archivo, simbolo_inicial)

    # Mostrar gramática original
    print("\nGramática original:")
    print("-"*80)
    print(gramatica.format())

    # Mostrar anulables
    anulables = encontrar_anulables(gramatica)
    print("\n[2] Símbolos anulables:", ", ".join(sorted(anulables)) if anulables else "∅")

    # Eliminar producciones epsilon
    print("\n[3] Eliminando producciones ε...")
    gramatica_sin_epsilon = eliminar_epsilon(gramatica)
    print("\nGramática sin producciones ε:")
    print("-"*80)
    print(gramatica_sin_epsilon.format())

    # Eliminar producciones unarias
    print("\n[4] Eliminando producciones unarias...")
    gramatica_sin_unitarias = eliminar_unarias(gramatica_sin_epsilon)
    print("\nGramática sin unarias:")
    print("-"*80)
    print(gramatica_sin_unitarias.format())

    # Eliminar símbolos inútiles
    print("\n[5] Eliminando símbolos inútiles...")
    gramatica_util = eliminar_simbolos_inutiles(gramatica_sin_unitarias)
    print("\nGramática sin símbolos inútiles:")
    print("-"*80)
    print(gramatica_util.format())

    # Convertir a CNF
    print("\n[6] Convirtiendo a CNF...")
    gramatica_cnf = convertir_a_cnf(gramatica_util)
    print("\nGramática en CNF:")
    print("-"*80)
    print(gramatica_cnf.format())

    # Modo interactivo para validar oraciones
    print("\n" + "="*80)
    print("VALIDACIÓN DE ORACIONES CON CYK")
    print("="*80)
    print("\nIngrese oraciones para validar (palabras separadas por espacios)")
    print("Escriba 'salir' para terminar")
    print("Escriba 'debug' para ver información de depuración\n")

    modo_debug = False

    while True:
        try:
            oracion = input("Oración > ").strip()
            
            if oracion.lower() == 'salir':
                print("\n¡Hasta luego!")
                break
            
            if oracion.lower() == 'debug':
                modo_debug = not modo_debug
                print(f"Modo debug: {'ACTIVADO' if modo_debug else 'DESACTIVADO'}\n")
                continue
            
            if not oracion:
                print("⚠️  Por favor ingrese una oración válida\n")
                continue

            # Ejecutar CYK
            print(f"\nAnalizando: '{oracion}'")
            print("-"*80)
            
            if modo_debug:
                palabras = oracion.strip().lower().split()
                print(f"Tokens: {palabras}")
                print(f"Número de tokens: {len(palabras)}")
                print("\nBuscando producciones para cada token:")
                for i, palabra in enumerate(palabras):
                    encontradas = []
                    for A, prods in gramatica_cnf.P.items():
                        for prod in prods:
                            if len(prod) == 1 and prod[0] == palabra:
                                encontradas.append(A)
                    print(f"  '{palabra}' -> {encontradas if encontradas else 'NINGUNA'}")
                print()
            
            resultado = cyk(gramatica_cnf, oracion)
            
            # Mostrar resultado
            if resultado.acepta:
                print(f"✅ ACEPTADA (tiempo: {resultado.tiempo:.6f}s)")
                print("\nÁrbol de derivación:")
                print(resultado.imprimir_parse_tree())
                
                # Opcionalmente mostrar tabla CYK
                respuesta = input("\n¿Desea ver la tabla CYK? (s/n): ").strip().lower()
                if respuesta == 's':
                    palabras = oracion.strip().split()
                    imprimir_tabla_cyk(resultado.tabla, palabras)
            else:
                print(f"❌ RECHAZADA (tiempo: {resultado.tiempo:.6f}s)")
                print("La oración no pertenece al lenguaje de la gramática.")
            
            print("\n" + "="*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print()

if __name__ == "__main__":
    main()