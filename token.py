from enum import Enum

class TipoToken(Enum):
    """Enumeración de los tipos de tokens"""
    PALABRA_R = "Palabra_Reservada"  # Robot
    IDENTIFICADOR = "Identificador"
    ACCION = "Accion"  # iniciar, finalizar, abrirGarra, cerrarGarra
    METODO = "Metodo"  # base, cuerpo, garra, velocidad
    NUMERO = "Numero"
    IGUAL = "Igual"
    PARENTESIS_IZQ = "Parentesis_Izq"
    PARENTESIS_DER = "Parentesis_Der"
    PUNTO = "Punto"
    COMENTARIO = "Comentario"
    ERROR = "Error"
    FIN_LINEA = "Fin_Linea"
    
    def get_descripcion(self):
        return self.value

class Token:
    """Clase que representa un token con información extendida"""
    
    def __init__(self, tipo, lexema, linea, columna, valor="", mensaje_error=""):
        self.tipo = tipo
        self.lexema = lexema
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.mensaje_error = mensaje_error
    
    def get_tipo(self):
        return self.tipo
    
    def get_lexema(self):
        return self.lexema
    
    def get_valor(self):
        return self.valor
    
    def get_linea(self):
        return self.linea
    
    def get_columna(self):
        return self.columna
    
    def get_mensaje_error(self):
        return self.mensaje_error
    
    def __str__(self):
        if self.tipo == TipoToken.ERROR:
            return f"{self.lexema:<15} {self.tipo.get_descripcion():<15} {self.mensaje_error:<25} {self.linea:<5} {self.columna:<5}"
        else:
            return f"{self.lexema:<15} {self.tipo.get_descripcion():<15} {self.valor:<15} {self.linea:<5} {self.columna:<5}"