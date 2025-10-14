#Módulo principal para llamar a las funciones de los otros módulos
from gramatica import Gramatica

def main():

    #Gramática de ejemplo
    gramatica = Gramatica()
    gramatica.definir_simbolo_inicial('S')
    gramatica.agregar_produccion("S", ("NP", "VP"))
    gramatica.agregar_produccion("VP", ("VP", "NP", "V", "PP", "cooks", "drinks", "eats", "cuts"))
    gramatica.agregar_produccion("V", ("eats", "cooks", "drinks", "cuts"))
    gramatica.agregar_produccion("NP", ("Det", "N", "he", "she"))
    gramatica.agregar_produccion("Det", ("a", "the"))
    gramatica.agregar_produccion("N", ("cat", "dog", "beer", "cake", "juice", "meat", "soup", "fork", "knife", "oven", "spoon"))

    print(gramatica.format())


if __name__ == "__main__":
    main()