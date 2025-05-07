from enum import Enum, auto
from typing import List, Optional

class TipoToken(Enum):
    """Enumeración de los tipos de tokens reconocidos en el lenguaje de control del brazo robótico."""
    PALABRA_R = auto()
    IDENTIFICADOR = auto()
    PUNTO = auto()
    ACCION = auto()
    METODO = auto()
    IGUAL = auto()
    NUMERO = auto()
    PARENTESIS_IZQ = auto()
    PARENTESIS_DER = auto()
    COMENTARIO = auto()
    ERROR = auto()
    
    def get_descripcion(self):
        """Retorna una descripción legible del tipo de token."""
        descripciones = {
            TipoToken.PALABRA_R: "Palabra clave Robot",
            TipoToken.IDENTIFICADOR: "Identificador",
            TipoToken.PUNTO: "Punto",
            TipoToken.ACCION: "Acción",
            TipoToken.METODO: "Método",
            TipoToken.IGUAL: "Signo igual",
            TipoToken.NUMERO: "Número",
            TipoToken.PARENTESIS_IZQ: "Paréntesis izquierdo",
            TipoToken.PARENTESIS_DER: "Paréntesis derecho",
            TipoToken.COMENTARIO: "Comentario",
            TipoToken.ERROR: "Token no reconocido"
        }
        return descripciones.get(self, "Desconocido")


class Token:
    """Representa un token reconocido en el código fuente."""
    
    def __init__(self, tipo: TipoToken, lexema: str, linea: int, columna: int):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
    
    def get_tipo(self) -> TipoToken:
        return self.tipo
    
    def get_lexema(self) -> str:
        return self.lexema
    
    def get_linea(self) -> int:
        return self.linea
    
    def get_columna(self) -> int:
        return self.columna
    
    def __str__(self) -> str:
        return f"Token({self.tipo.name}, '{self.lexema}', línea {self.linea}, columna {self.columna})"


class AnalizadorLexico:
    """Analizador léxico para el lenguaje de control del brazo robótico."""
    
    @staticmethod
    def analizar(codigo: str) -> List[Token]:
        """
        Analiza el código fuente y retorna una lista de tokens.
        Esta es una implementación simplificada. En un caso real, sería necesario
        un analizador léxico más completo.
        """
        tokens = []
        lineas = codigo.split('\n')
        
        for num_linea, linea in enumerate(lineas, 1):
            indice = 0
            while indice < len(linea):
                if linea[indice].isspace():
                    indice += 1
                    continue
                
                # Detección de comentarios
                if linea[indice:indice+2] == "//":
                    comentario = linea[indice:]
                    tokens.append(Token(TipoToken.COMENTARIO, comentario, num_linea, indice + 1))
                    break  # Pasar a la siguiente línea
                
                # Detección de diferentes tokens
                if linea[indice:indice+5].lower() == "robot":
                    tokens.append(Token(TipoToken.PALABRA_R, "Robot", num_linea, indice + 1))
                    indice += 5
                elif linea[indice] == '.':
                    tokens.append(Token(TipoToken.PUNTO, ".", num_linea, indice + 1))
                    indice += 1
                elif linea[indice] == '=':
                    tokens.append(Token(TipoToken.IGUAL, "=", num_linea, indice + 1))
                    indice += 1
                elif linea[indice] == '(':
                    tokens.append(Token(TipoToken.PARENTESIS_IZQ, "(", num_linea, indice + 1))
                    indice += 1
                elif linea[indice] == ')':
                    tokens.append(Token(TipoToken.PARENTESIS_DER, ")", num_linea, indice + 1))
                    indice += 1
                elif linea[indice].isdigit():
                    # Reconocimiento de números
                    inicio = indice
                    while indice < len(linea) and linea[indice].isdigit():
                        indice += 1
                    numero = linea[inicio:indice]
                    tokens.append(Token(TipoToken.NUMERO, numero, num_linea, inicio + 1))
                elif linea[indice].isalpha():
                    # Reconocimiento de identificadores, acciones o métodos
                    inicio = indice
                    while indice < len(linea) and (linea[indice].isalnum() or linea[indice] == '_'):
                        indice += 1
                    palabra = linea[inicio:indice]
                    
                    # Clasificar la palabra según su contexto
                    if palabra in ["iniciar", "finalizar", "cerrarGarra", "abrirGarra"]:
                        tokens.append(Token(TipoToken.ACCION, palabra, num_linea, inicio + 1))
                    elif palabra in ["base", "cuerpo", "garra", "velocidad"]:
                        tokens.append(Token(TipoToken.METODO, palabra, num_linea, inicio + 1))
                    else:
                        tokens.append(Token(TipoToken.IDENTIFICADOR, palabra, num_linea, inicio + 1))
                else:
                    # Carácter no reconocido
                    tokens.append(Token(TipoToken.ERROR, linea[indice], num_linea, indice + 1))
                    indice += 1
        
        return tokens


class AnalizadorSintactico:
    """
    Analizador sintáctico para el lenguaje de control del brazo robótico.
    Utiliza el analizador léxico para obtener los tokens del código.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicion_actual = 0
        self.errores = []
    
    def analizar(self) -> bool:
        """
        Ejecuta el análisis sintáctico del programa.
        
        Returns:
            bool: True si el programa es sintácticamente correcto, False en caso contrario
        """
        try:
            self.programa()
            return len(self.errores) == 0
        except Exception as e:
            self.errores.append(f"Error inesperado: {str(e)}")
            return False
    
    def get_errores(self) -> List[str]:
        """
        Obtiene la lista de errores sintácticos encontrados.
        
        Returns:
            List[str]: Lista de mensajes de error
        """
        return self.errores
    
    def hay_tokens(self) -> bool:
        """
        Verifica si hay tokens disponibles.
        
        Returns:
            bool: True si hay más tokens por analizar
        """
        # Avanzamos automáticamente sobre los comentarios
        self.saltar_comentarios()
        return self.posicion_actual < len(self.tokens)
    
    def saltar_comentarios(self) -> None:
        """Salta los tokens de tipo comentario."""
        while (self.posicion_actual < len(self.tokens) and
               self.tokens[self.posicion_actual].get_tipo() == TipoToken.COMENTARIO):
            self.posicion_actual += 1
    
    def token_actual(self) -> Optional[Token]:
        """
        Obtiene el token actual sin avanzar en la lista.
        
        Returns:
            Optional[Token]: Token actual o None si no hay más tokens
        """
        # Aseguramos que saltamos los comentarios antes de obtener el token actual
        self.saltar_comentarios()
        if not self.hay_tokens():
            return None
        return self.tokens[self.posicion_actual]
    
    def avanzar(self) -> Optional[Token]:
        """
        Avanza al siguiente token.
        
        Returns:
            Optional[Token]: Token anterior (el que era actual antes de avanzar)
        """
        actual = self.token_actual()
        self.posicion_actual += 1
        # Saltamos comentarios después de avanzar
        self.saltar_comentarios()
        return actual
    
    def coincide(self, tipo: TipoToken) -> bool:
        """
        Comprueba si el token actual es del tipo esperado.
        
        Args:
            tipo: Tipo de token esperado
            
        Returns:
            bool: True si el token actual coincide con el tipo esperado
        """
        if not self.hay_tokens():
            return False
        return self.token_actual().get_tipo() == tipo
    
    def consumir(self, tipo: TipoToken, mensaje: str) -> bool:
        """
        Consume el token actual si es del tipo esperado, de lo contrario registra un error.
        
        Args:
            tipo: Tipo de token esperado
            mensaje: Mensaje de error si no coincide
            
        Returns:
            bool: True si se consumió correctamente, False en caso contrario
        """
        if self.coincide(tipo):
            self.avanzar()
            return True
        
        token = self.token_actual()
        descripcion_error = mensaje
        if token is not None:
            descripcion_error += f" En línea {token.get_linea()}, columna {token.get_columna()}. " \
                                f"Encontrado: '{token.get_lexema()}' ({token.get_tipo().get_descripcion()})"
        else:
            descripcion_error += " Se llegó al final del archivo."
        
        self.errores.append(descripcion_error)
        return False
    
    def programa(self) -> None:
        """
        Regla gramatical para el programa completo.
        programa -> declaracionRobot instrucciones
        """
        self.declaracion_robot()
        self.instrucciones()
    
    def declaracion_robot(self) -> None:
        """
        Regla gramatical para la declaración del robot.
        declaracionRobot -> PALABRA_R IDENTIFICADOR
        """
        if not self.consumir(TipoToken.PALABRA_R, "Se esperaba la palabra 'Robot'"):
            # Si no se encuentra la declaración, intentamos recuperarnos
            self.sincronizar(TipoToken.IDENTIFICADOR)
        
        if not self.consumir(TipoToken.IDENTIFICADOR, "Se esperaba un identificador para el robot"):
            # Si no se encuentra el identificador, intentamos sincronizar
            self.sincronizar(TipoToken.PUNTO)
    
    def instrucciones(self) -> None:
        """
        Regla gramatical para las instrucciones.
        instrucciones -> instruccion instrucciones | ε
        """
        while self.hay_tokens():
            self.instruccion()
    
    def instruccion(self) -> None:
        """
        Regla gramatical para una instrucción.
        instruccion -> IDENTIFICADOR PUNTO (accion | asignacion)
        """
        if not self.consumir(TipoToken.IDENTIFICADOR, "Se esperaba un identificador de robot"):
            # Si no se encuentra el identificador, intentamos sincronizar
            self.sincronizar(TipoToken.PUNTO)
        
        if not self.consumir(TipoToken.PUNTO, "Se esperaba un punto después del identificador"):
            # Si no se encuentra el punto, intentamos sincronizar
            self.sincronizar_instruccion()
            return
        
        # Verificar si la siguiente instrucción es una acción o una asignación
        if self.coincide(TipoToken.ACCION):
            self.accion()
        elif self.coincide(TipoToken.METODO):
            self.asignacion()
        else:
            token = self.token_actual()
            if token is not None:
                self.errores.append(f"Se esperaba una acción o método en línea {token.get_linea()}, "
                                  f"columna {token.get_columna()}. Encontrado: '{token.get_lexema()}' "
                                  f"({token.get_tipo().get_descripcion()})")
                self.avanzar()  # Consumir el token para continuar
            else:
                self.errores.append("Se esperaba una acción o método, pero se llegó al final del archivo.")
            # Intenta recuperarse
            self.sincronizar_instruccion()
    
    def accion(self) -> None:
        """
        Regla gramatical para una acción.
        accion -> ACCION PARENTESIS_IZQ PARENTESIS_DER
        """
        accion_token = self.avanzar()  # Consumir la ACCION
        
        # Validar que sea una acción válida
        accion = accion_token.get_lexema()
        if accion not in ["iniciar", "finalizar", "cerrarGarra", "abrirGarra"]:
            self.errores.append(f"Acción no reconocida: '{accion}' en línea {accion_token.get_linea()}. "
                              f"Acciones válidas: iniciar, finalizar, cerrarGarra, abrirGarra")
        
        if not self.consumir(TipoToken.PARENTESIS_IZQ, f"Se esperaba paréntesis izquierdo después de {accion}"):
            self.sincronizar(TipoToken.PARENTESIS_DER)
        
        if not self.consumir(TipoToken.PARENTESIS_DER, f"Se esperaba paréntesis derecho para cerrar {accion}"):
            self.sincronizar_instruccion()
    
    def asignacion(self) -> None:
        """
        Regla gramatical para una asignación.
        asignacion -> METODO IGUAL NUMERO
        """
        metodo_token = self.avanzar()  # Consumir el METODO
        
        # Validar que sea un método válido
        metodo = metodo_token.get_lexema()
        if metodo not in ["base", "cuerpo", "garra", "velocidad"]:
            self.errores.append(f"Método no reconocido: '{metodo}' en línea {metodo_token.get_linea()}. "
                              f"Métodos válidos: base, cuerpo, garra, velocidad")
        
        if not self.consumir(TipoToken.IGUAL, f"Se esperaba un signo igual después de {metodo}"):
            self.sincronizar(TipoToken.NUMERO)
        else:
            # Solo verificamos el número si encontramos el signo igual
            if self.coincide(TipoToken.NUMERO):
                numero_token = self.avanzar()  # Consumir el NUMERO
                
                # Validación de rango para los valores según el tipo de método
                try:
                    valor = int(numero_token.get_lexema())
                    
                    if metodo == "base":
                        if valor < 0 or valor > 180:
                            self.errores.append(f"El valor para 'base' debe estar entre 0 y 180 grados. "
                                              f"Valor proporcionado: {valor} en línea {numero_token.get_linea()}")
                    elif metodo == "cuerpo":
                        if valor < 0 or valor > 90:
                            self.errores.append(f"El valor para 'cuerpo' debe estar entre 0 y 90 grados. "
                                              f"Valor proporcionado: {valor} en línea {numero_token.get_linea()}")
                    elif metodo == "garra":
                        if valor < 0 or valor > 180:
                            self.errores.append(f"El valor para 'garra' debe estar entre 0 y 180 grados. "
                                              f"Valor proporcionado: {valor} en línea {numero_token.get_linea()}")
                    elif metodo == "velocidad":
                        if valor < 1 or valor > 100:
                            self.errores.append(f"El valor para 'velocidad' debe estar entre 1 y 100. "
                                              f"Valor proporcionado: {valor} en línea {numero_token.get_linea()}")
                except ValueError:
                    self.errores.append(f"Error al convertir valor numérico para {metodo}: "
                                      f"{numero_token.get_lexema()} en línea {numero_token.get_linea()}")
            else:
                token = self.token_actual()
                if token is not None:
                    self.errores.append(f"Se esperaba un valor numérico para '{metodo}' en línea "
                                      f"{token.get_linea()}. Encontrado: '{token.get_lexema()}' "
                                      f"({token.get_tipo().get_descripcion()})")
                    self.avanzar()  # Consumir el token inesperado para continuar
                else:
                    self.errores.append(f"Se esperaba un valor numérico para '{metodo}', "
                                      f"pero se llegó al final del archivo.")
    
    def sincronizar(self, tipo: TipoToken) -> None:
        """
        Método para sincronizar el analizador en caso de error.
        Avanza hasta encontrar un token del tipo especificado.
        
        Args:
            tipo: Tipo de token hasta el que avanzar
        """
        while self.hay_tokens() and not self.coincide(tipo):
            self.avanzar()
    
    def sincronizar_instruccion(self) -> None:
        """
        Método para sincronizar al inicio de la siguiente instrucción.
        Avanza hasta encontrar un identificador seguido de un punto.
        """
        while self.hay_tokens():
            if (self.coincide(TipoToken.IDENTIFICADOR) and
                    self.posicion_actual + 1 < len(self.tokens) and
                    self.tokens[self.posicion_actual + 1].get_tipo() == TipoToken.PUNTO):
                return
            self.avanzar()


def main():
    """Método principal para probar el analizador sintáctico."""
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

    # Código con errores para probar
    codigo_con_errores = """Robot r1
r1.iniciar()
r1.velocidad=150
r1.@base=45
r1.brazo=45
r1.cuerpo45
r1.garra=
r1.cerrarGarra
finalizar()"""

    # Analizar el código correcto
    print("=== ANÁLISIS SINTÁCTICO DE CÓDIGO CORRECTO ===")
    tokens = AnalizadorLexico.analizar(codigo_ejemplo)

    # Mostrar tokens reconocidos
    print("\nTOKENS RECONOCIDOS:")
    for token in tokens:
        if token.get_tipo() != TipoToken.COMENTARIO:
            print(token)

    # Analizar sintaxis
    analizador_sintactico = AnalizadorSintactico(tokens)
    es_valido = analizador_sintactico.analizar()

    if es_valido:
        print("\nEl código es sintácticamente correcto.")
    else:
        print("\nEl código tiene errores sintácticos:")
        for error in analizador_sintactico.get_errores():
            print(f"- {error}")

    # Analizar el código con errores
    print("\n=== ANÁLISIS SINTÁCTICO DE CÓDIGO CON ERRORES ===")
    tokens = AnalizadorLexico.analizar(codigo_con_errores)

    # Mostrar tokens reconocidos (incluyendo errores)
    print("\nTOKENS RECONOCIDOS (INCLUYENDO ERRORES):")
    for token in tokens:
        print(token)

    # Analizar sintaxis con errores
    analizador_sintactico = AnalizadorSintactico(tokens)
    es_valido = analizador_sintactico.analizar()

    if es_valido:
        print("\nEl código es sintácticamente correcto.")
    else:
        print("\nEl código tiene errores sintácticos:")
        for error in analizador_sintactico.get_errores():
            print(f"- {error}")


if __name__ == "__main__":
    main()