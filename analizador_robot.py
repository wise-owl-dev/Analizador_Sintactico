import re
from token import Token, TipoToken

class AnalizadorRobot:
    # Diccionarios para palabras reservadas y acciones/métodos
    PALABRAS_RESERVADAS = {
        "robot": TipoToken.PALABRA_R
    }
    
    ACCIONES_Y_METODOS = {
        "iniciar": TipoToken.ACCION,
        "finalizar": TipoToken.ACCION,
        "abrirGarra": TipoToken.ACCION,
        "cerrarGarra": TipoToken.ACCION,
        
        "base": TipoToken.METODO,
        "cuerpo": TipoToken.METODO,
        "garra": TipoToken.METODO,
        "velocidad": TipoToken.METODO
    }
    
    # Patrones regex para reconocimiento de tokens
    PATRON_IDENTIFICADOR = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*")
    PATRON_NUMERO = re.compile(r"^[0-9]+")
    PATRON_COMENTARIO = re.compile(r"^//.*")
    PATRON_COMENTARIO_MULTILINEA = re.compile(r"^/\*(.|\\n)*?\*/", re.DOTALL)
    
    @staticmethod
    def analizar(codigo):
        """
        Analiza el código y devuelve una lista de tokens
        
        Args:
            codigo: Código fuente a analizar
        Returns:
            Lista de tokens encontrados
        """
        tokens = []
        errores = []
        
        # Normalizar el código (eliminar retornos de carro y normalizar fin de línea)
        codigo = codigo.replace("\r\n", "\n").replace("\r", "\n")
        
        # Dividir el código en líneas para mantener el seguimiento de línea/columna
        lineas = codigo.split("\n")
        
        for num_linea, linea in enumerate(lineas):
            columna = 0
            
            while columna < len(linea):
                # Omitir espacios en blanco
                if linea[columna].isspace():
                    columna += 1
                    continue
                
                # Buscar comentarios de una línea
                if columna + 1 < len(linea) and linea[columna] == '/' and linea[columna + 1] == '/':
                    # Es un comentario de una línea
                    comentario = linea[columna:]
                    tokens.append(Token(TipoToken.COMENTARIO, comentario, num_linea + 1, columna + 1))
                    columna = len(linea)  # Ir al final de la línea
                    continue
                
                # Punto (separador para métodos)
                if linea[columna] == '.':
                    tokens.append(Token(TipoToken.PUNTO, ".", num_linea + 1, columna + 1))
                    columna += 1
                    continue
                
                # Paréntesis
                if linea[columna] == '(':
                    tokens.append(Token(TipoToken.PARENTESIS_IZQ, "(", num_linea + 1, columna + 1))
                    columna += 1
                    continue
                
                if linea[columna] == ')':
                    tokens.append(Token(TipoToken.PARENTESIS_DER, ")", num_linea + 1, columna + 1))
                    columna += 1
                    continue
                
                # Igual
                if linea[columna] == '=':
                    tokens.append(Token(TipoToken.IGUAL, "=", num_linea + 1, columna + 1))
                    columna += 1
                    continue
                
                # Identificador o palabra reservada
                if linea[columna].isalpha() or linea[columna] == '_':
                    match = AnalizadorRobot.PATRON_IDENTIFICADOR.search(linea[columna:])
                    if match:
                        lexema = match.group()
                        
                        # Verificar si es una palabra reservada (case-insensitive)
                        lexema_lower = lexema.lower()
                        if lexema_lower in AnalizadorRobot.PALABRAS_RESERVADAS:
                            tipo = AnalizadorRobot.PALABRAS_RESERVADAS[lexema_lower]
                            tokens.append(Token(tipo, lexema, num_linea + 1, columna + 1))
                        # Verificar si es una acción o método (sólo después de un punto)
                        elif tokens and tokens[-1].get_tipo() == TipoToken.PUNTO and lexema in AnalizadorRobot.ACCIONES_Y_METODOS:
                            tipo = AnalizadorRobot.ACCIONES_Y_METODOS[lexema]
                            tokens.append(Token(tipo, lexema, num_linea + 1, columna + 1))
                        # Es un identificador normal
                        else:
                            tokens.append(Token(TipoToken.IDENTIFICADOR, lexema, num_linea + 1, columna + 1))
                        
                        columna += len(lexema)
                        continue
                
                # Número
                if linea[columna].isdigit():
                    match = AnalizadorRobot.PATRON_NUMERO.search(linea[columna:])
                    if match:
                        numero = match.group()
                        try:
                            valor_numerico = int(numero)
                            tokens.append(Token(TipoToken.NUMERO, numero, num_linea + 1, columna + 1, valor=numero))
                        except ValueError:
                            tokens.append(Token(TipoToken.ERROR, numero, num_linea + 1, columna + 1, 
                                               mensaje_error="Número entero fuera de rango"))
                        columna += len(numero)
                        continue
                
                # Si llegamos aquí, es un carácter desconocido
                caracter_desconocido = linea[columna]
                tokens.append(Token(TipoToken.ERROR, caracter_desconocido, num_linea + 1, columna + 1,
                                   mensaje_error="Carácter no reconocido"))
                columna += 1
            
            # Fin de línea (opcional, útil para algunas gramáticas)
            # tokens.append(Token(TipoToken.FIN_LINEA, "EOL", num_linea + 1, columna + 1))
        
        return tokens
    
    @staticmethod
    def procesar_para_tabla(tokens):
        """
        Procesa los tokens para mostrar la información en formato tabular
        mejorado para incluir información de errores
        
        Args:
            tokens: Lista de tokens a procesar
        Returns:
            Lista de datos para la tabla (cada fila es una lista de objetos)
        """
        filas = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Saltar tokens de fin de línea si se usan
            if token.get_tipo() == TipoToken.FIN_LINEA:
                i += 1
                continue
            
            # Si es un error, mostrarlo con su mensaje
            if token.get_tipo() == TipoToken.ERROR:
                filas.append([
                    token.get_lexema(),
                    token.get_tipo().get_descripcion(),
                    token.get_mensaje_error(),
                    "Error" # Estado
                ])
                i += 1
                continue
            
            # Si es un comentario, mostrarlo como tal
            if token.get_tipo() == TipoToken.COMENTARIO:
                filas.append([
                    token.get_lexema(),
                    token.get_tipo().get_descripcion(),
                    "", # Sin valor
                    "N/A" # No aplica
                ])
                i += 1
                continue
            
            # Caso especial para métodos que están seguidos de paréntesis vacíos (sin parámetros)
            if ((token.get_tipo() == TipoToken.METODO or token.get_tipo() == TipoToken.ACCION)
                    and i + 2 < len(tokens)
                    and tokens[i + 1].get_tipo() == TipoToken.PARENTESIS_IZQ
                    and tokens[i + 2].get_tipo() == TipoToken.PARENTESIS_DER):
                
                filas.append([
                    token.get_lexema() + "()",
                    token.get_tipo().get_descripcion(),
                    "", # Sin valor
                    "No" # No tiene parámetros
                ])
                i += 3  # Saltar el método y los paréntesis
            
            # Caso para métodos con valores (seguidos de igual y número)
            elif (token.get_tipo() == TipoToken.METODO
                    and i + 2 < len(tokens)
                    and tokens[i + 1].get_tipo() == TipoToken.IGUAL
                    and tokens[i + 2].get_tipo() == TipoToken.NUMERO):
                
                filas.append([
                    token.get_lexema(),
                    token.get_tipo().get_descripcion(),
                    tokens[i + 2].get_lexema(), # El valor es el número
                    "Sí" # Tiene parámetros
                ])
                i += 3  # Saltar el método, el igual y el número
            
            # Caso general para otros tokens
            elif token.get_tipo() != TipoToken.PUNTO:  # Ignoramos los puntos para simplificar la salida
                filas.append([
                    token.get_lexema(),
                    token.get_tipo().get_descripcion(),
                    token.get_valor(),
                    "N/A" # No aplica parámetro
                ])
                i += 1
            else:
                i += 1  # Si es un punto, simplemente avanzamos
        
        return filas
    
    @staticmethod
    def obtener_errores(tokens):
        """
        Genera una representación textual de los errores léxicos encontrados
        
        Args:
            tokens: Lista de tokens que puede contener errores
        Returns:
            Cadena con los errores formateados
        """
        errores = []
        hay_errores = False
        
        for token in tokens:
            if token.get_tipo() == TipoToken.ERROR:
                hay_errores = True
                errores.append(f"Error en línea {token.get_linea()}, columna {token.get_columna()}: "
                              f"{token.get_mensaje_error()} - '{token.get_lexema()}'")
        
        if not hay_errores:
            return "No se encontraron errores léxicos."
        
        return "\n".join(errores)

# Método principal para probar el analizador léxico mejorado
if __name__ == "__main__":
    # Código de ejemplo para el brazo robótico
    codigo_ejemplo = """// Programa de prueba para el brazo robótico
Robot r1
r1.iniciar()
r1.velocidad=50 // Establecer velocidad media
r1.base=180
r1.cuerpo=45
r1.garra=90
r1.cerrarGarra()
r1.abrirGarra()
r1.finalizar()"""

    # Código con errores para prueba
    codigo_con_errores = """Robot r1
r1.iniciar()
r1.@velocidad=50
r1.base=180
r1.cuerp0=45
r1.garra=90x
r1.cerrarGarra()
r1.abrirGarra()
r1.finalizar()"""

    # Analizar el código correcto
    print("=== ANÁLISIS LÉXICO DE CÓDIGO CORRECTO ===")
    tokens = AnalizadorRobot.analizar(codigo_ejemplo)

    # Mostrar los tokens en formato crudo
    print("TOKENS CRUDOS:")
    print(f"{'LEXEMA':<15} {'TIPO':<15} {'VALOR':<15} {'LINEA':<5} {'COL':<5}")
    print("-" * 60)
    for token in tokens:
        print(token)

    # Mostrar los tokens procesados para una tabla
    print("\nTOKENS PROCESADOS PARA TABLA:")
    print(f"{'TOKEN':<15} {'TIPO':<15} {'VALOR':<15} {'PARAMETRO':<15}")
    print("-" * 60)
    filas_tabla = AnalizadorRobot.procesar_para_tabla(tokens)
    for fila in filas_tabla:
        print(f"{fila[0]:<15} {fila[1]:<15} {fila[2]:<15} {fila[3]:<15}")

    # Mostrar errores léxicos (si los hay)
    print("\nERRORES LÉXICOS:")
    print(AnalizadorRobot.obtener_errores(tokens))

    # Analizar el código con errores
    print("\n=== ANÁLISIS LÉXICO DE CÓDIGO CON ERRORES ===")
    tokens = AnalizadorRobot.analizar(codigo_con_errores)

    # Mostrar los tokens en formato crudo
    print("TOKENS CRUDOS:")
    print(f"{'LEXEMA':<15} {'TIPO':<15} {'VALOR/ERROR':<25} {'LINEA':<5} {'COL':<5}")
    print("-" * 60)
    for token in tokens:
        print(token)

    # Mostrar errores léxicos
    print("\nERRORES LÉXICOS:")
    print(AnalizadorRobot.obtener_errores(tokens))