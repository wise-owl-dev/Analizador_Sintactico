import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import sys
import os
import importlib.util

# Importar los módulos de analizador léxico y sintáctico
# Asegúrate de que estos archivos estén en el mismo directorio que este script
try:
    # Importar el módulo token.py
    spec_token = importlib.util.spec_from_file_location("token_module", "token.py")
    token_module = importlib.util.module_from_spec(spec_token)
    spec_token.loader.exec_module(token_module)
    Token = token_module.Token
    TipoToken = token_module.TipoToken

    # Importar el módulo analizador_robot.py
    spec_robot = importlib.util.spec_from_file_location("analizador_robot", "analizador_robot.py")
    analizador_robot = importlib.util.module_from_spec(spec_robot)
    spec_robot.loader.exec_module(analizador_robot)
    AnalizadorRobot = analizador_robot.AnalizadorRobot

    # Importar el módulo analizador_sintactico.py
    spec_sintactico = importlib.util.spec_from_file_location("analizador_sintactico", "analizador_sintactico.py")
    analizador_sintactico = importlib.util.module_from_spec(spec_sintactico)
    spec_sintactico.loader.exec_module(analizador_sintactico)
    AnalizadorLexico = analizador_sintactico.AnalizadorLexico
    AnalizadorSintactico = analizador_sintactico.AnalizadorSintactico
    
    MODULOS_CARGADOS = True
except Exception as e:
    print(f"Error al importar los módulos: {e}")
    MODULOS_CARGADOS = False


class InterfazAnalizadorRobot:
    """Interfaz gráfica para el analizador de lenguaje de control de brazo robótico"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Lenguaje de Control de Brazo Robótico")
        self.root.geometry("1200x700")
        
        # Variables para almacenar los resultados del análisis
        self.tokens = []
        self.errores_lexicos = []
        self.errores_sintacticos = []
        
        # Crear código de ejemplo
        self.codigo_ejemplo = """// Programa de prueba para el brazo robótico
Robot r1
r1.iniciar()
r1.velocidad=50 // Establecer velocidad media
r1.base=180
r1.cuerpo=45
r1.garra=90
r1.cerrarGarra()
r1.abrirGarra()
r1.finalizar()"""
        
        # Configurar la interfaz gráfica
        self.configurar_interfaz()
        
        # Verificar si los módulos se han cargado correctamente
        if not MODULOS_CARGADOS:
            messagebox.showerror("Error", "No se pudieron cargar los módulos necesarios. Asegúrate de que los archivos 'token.py', 'analizador_robot.py' y 'analizador_sintactico.py' estén en el mismo directorio que este script.")
    
    def configurar_interfaz(self):
        """Configura todos los componentes de la interfaz gráfica"""
        # Crear menú
        self.crear_menu()
        
        # Panel principal dividido en dos
        self.panel_principal = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo: editor de código
        self.crear_panel_editor()
        
        # Panel derecho: resultados del análisis
        self.crear_panel_resultados()
        
        # Barra de estado en la parte inferior
        self.barra_estado = tk.Label(self.root, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cargar el código de ejemplo en el editor
        self.editor_codigo.insert(tk.END, self.codigo_ejemplo)
    
    def crear_menu(self):
        """Crea la barra de menú de la aplicación"""
        barra_menu = tk.Menu(self.root)
        self.root.config(menu=barra_menu)
        
        # Menú Archivo
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Nuevo", command=self.nuevo_archivo)
        menu_archivo.add_command(label="Abrir...", command=self.abrir_archivo)
        menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        menu_archivo.add_command(label="Guardar como...", command=self.guardar_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        # Menú Analizar
        menu_analizar = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Analizar", menu=menu_analizar)
        menu_analizar.add_command(label="Análisis Léxico", command=self.realizar_analisis_lexico)
        menu_analizar.add_command(label="Análisis Sintáctico", command=self.realizar_analisis_sintactico)
        menu_analizar.add_command(label="Análisis Completo", command=self.realizar_analisis_completo)
        
        # Menú Ejemplos
        menu_ejemplos = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ejemplos", menu=menu_ejemplos)
        menu_ejemplos.add_command(label="Código correcto", command=self.cargar_ejemplo_correcto)
        menu_ejemplos.add_command(label="Código con errores", command=self.cargar_ejemplo_errores)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Gramática del lenguaje", command=self.mostrar_gramatica)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
    
    def crear_panel_editor(self):
        """Crea el panel del editor de código fuente"""
        frame_editor = ttk.Frame(self.panel_principal)
        self.panel_principal.add(frame_editor, weight=1)
        
        # Etiqueta para el editor
        ttk.Label(frame_editor, text="Editor de Código", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Editor de código con números de línea
        frame_editor_con_lineas = ttk.Frame(frame_editor)
        frame_editor_con_lineas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Números de línea
        self.lineas = tk.Text(frame_editor_con_lineas, width=4, padx=3, pady=5, takefocus=0,
                              border=0, background='lightgray', state='disabled')
        self.lineas.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de código
        self.editor_codigo = scrolledtext.ScrolledText(frame_editor_con_lineas, wrap=tk.WORD, 
                                                      width=50, height=20, font=("Consolas", 10))
        self.editor_codigo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Vincular evento de actualizacióm de líneas
        self.editor_codigo.bind('<KeyRelease>', self.actualizar_lineas)
        self.editor_codigo.bind('<MouseWheel>', self.actualizar_lineas)
        
        # Botones para el análisis
        frame_botones = ttk.Frame(frame_editor)
        frame_botones.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botones, text="Análisis Léxico", 
                  command=self.realizar_analisis_lexico).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Análisis Sintáctico", 
                  command=self.realizar_analisis_sintactico).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Análisis Completo", 
                  command=self.realizar_analisis_completo).pack(side=tk.LEFT, padx=5)
        
        # Inicializar números de línea
        self.actualizar_lineas()
    
    def crear_panel_resultados(self):
        """Crea el panel para mostrar los resultados del análisis"""
        frame_resultados = ttk.Frame(self.panel_principal)
        self.panel_principal.add(frame_resultados, weight=1)
        
        # Notebook para organizar los resultados en pestañas
        self.notebook = ttk.Notebook(frame_resultados)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña para tokens
        self.tab_tokens = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tokens, text="Tokens")
        
        # Tabla de tokens
        self.crear_tabla_tokens()
        
        # Pestaña para errores léxicos
        self.tab_errores_lexicos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_errores_lexicos, text="Errores Léxicos")
        
        # Área de texto para errores léxicos
        self.texto_errores_lexicos = scrolledtext.ScrolledText(self.tab_errores_lexicos, wrap=tk.WORD, 
                                                             width=50, height=15, font=("Consolas", 10))
        self.texto_errores_lexicos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña para errores sintácticos
        self.tab_errores_sintacticos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_errores_sintacticos, text="Errores Sintácticos")
        
        # Área de texto para errores sintácticos
        self.texto_errores_sintacticos = scrolledtext.ScrolledText(self.tab_errores_sintacticos, wrap=tk.WORD, 
                                                                 width=50, height=15, font=("Consolas", 10))
        self.texto_errores_sintacticos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def crear_tabla_tokens(self):
        """Crea la tabla para mostrar los tokens encontrados"""
        # Frame para la tabla con scrollbar
        frame_tabla = ttk.Frame(self.tab_tokens)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Tabla de tokens (Treeview)
        self.tabla_tokens = ttk.Treeview(frame_tabla, columns=("Lexema", "Tipo", "Valor", "Línea", "Columna"),
                                        show="headings", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tabla_tokens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scrollbars
        scrollbar_y.config(command=self.tabla_tokens.yview)
        scrollbar_x.config(command=self.tabla_tokens.xview)
        
        # Configurar encabezados de columnas
        self.tabla_tokens.heading("Lexema", text="Lexema")
        self.tabla_tokens.heading("Tipo", text="Tipo")
        self.tabla_tokens.heading("Valor", text="Valor")
        self.tabla_tokens.heading("Línea", text="Línea")
        self.tabla_tokens.heading("Columna", text="Columna")
        
        # Configurar anchos de columnas
        self.tabla_tokens.column("Lexema", width=100, anchor="w")
        self.tabla_tokens.column("Tipo", width=150, anchor="w")
        self.tabla_tokens.column("Valor", width=100, anchor="w")
        self.tabla_tokens.column("Línea", width=60, anchor="center")
        self.tabla_tokens.column("Columna", width=60, anchor="center")
    
    def actualizar_lineas(self, event=None):
        """Actualiza los números de línea en el editor"""
        # Obtener el número total de líneas
        final_index = self.editor_codigo.index('end-1c')
        num_lineas = int(final_index.split('.')[0])
        
        # Actualizar el widget de números de línea
        self.lineas.config(state='normal')
        self.lineas.delete('1.0', tk.END)
        for i in range(1, num_lineas + 1):
            self.lineas.insert(tk.END, f"{i}\n")
        self.lineas.config(state='disabled')
        
        # Ajustar el scroll para que coincida con el editor
        self.lineas.yview_moveto(self.editor_codigo.yview()[0])
    
    def nuevo_archivo(self):
        """Crea un nuevo archivo en blanco"""
        # Preguntar si se desea guardar el archivo actual
        if messagebox.askyesno("Confirmar", "¿Desea guardar el archivo actual antes de crear uno nuevo?"):
            self.guardar_archivo()
        
        # Limpiar el editor
        self.editor_codigo.delete(1.0, tk.END)
        self.actualizar_lineas()
        
        # Reiniciar los resultados
        self.limpiar_resultados()
        
        # Actualizar la barra de estado
        self.barra_estado.config(text="Nuevo archivo creado")
    
    def abrir_archivo(self):
        """Abre un archivo existente"""
        # Mostrar el diálogo para seleccionar archivo
        ruta_archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos de Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        
        # Si se seleccionó un archivo, abrirlo
        if ruta_archivo:
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Cargar el contenido en el editor
                self.editor_codigo.delete(1.0, tk.END)
                self.editor_codigo.insert(tk.END, contenido)
                self.actualizar_lineas()
                
                # Reiniciar los resultados
                self.limpiar_resultados()
                
                # Actualizar la barra de estado
                self.barra_estado.config(text=f"Archivo abierto: {ruta_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")
    
    def guardar_archivo(self):
        """Guarda el contenido del editor en el archivo actual"""
        # Si no hay archivo actual, usar guardar como
        if hasattr(self, 'archivo_actual') and self.archivo_actual:
            try:
                contenido = self.editor_codigo.get(1.0, tk.END)
                with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                self.barra_estado.config(text=f"Archivo guardado: {self.archivo_actual}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            self.guardar_como()
    
    def guardar_como(self):
        """Guarda el contenido del editor en un nuevo archivo"""
        # Mostrar el diálogo para seleccionar archivo
        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Archivos de Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        
        # Si se seleccionó un archivo, guardarlo
        if ruta_archivo:
            try:
                contenido = self.editor_codigo.get(1.0, tk.END)
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                self.archivo_actual = ruta_archivo
                self.barra_estado.config(text=f"Archivo guardado como: {ruta_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
    
    def realizar_analisis_lexico(self):
        """Realiza el análisis léxico del código en el editor"""
        if not MODULOS_CARGADOS:
            messagebox.showerror("Error", "No se pudieron cargar los módulos necesarios.")
            return
        
        # Obtener el código del editor
        codigo = self.editor_codigo.get(1.0, tk.END)
        
        try:
            # Realizar el análisis léxico usando AnalizadorRobot
            self.tokens = AnalizadorRobot.analizar(codigo)
            
            # Mostrar los tokens en la tabla
            self.mostrar_tokens_en_tabla()
            
            # Mostrar errores léxicos
            errores_texto = AnalizadorRobot.obtener_errores(self.tokens)
            self.texto_errores_lexicos.delete(1.0, tk.END)
            self.texto_errores_lexicos.insert(tk.END, errores_texto)
            
            # Limpiar errores sintácticos
            self.texto_errores_sintacticos.delete(1.0, tk.END)
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Análisis léxico completado. Tokens encontrados: {len(self.tokens)}")
            
            # Cambiar a la pestaña de tokens
            self.notebook.select(self.tab_tokens)
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar el análisis léxico: {str(e)}")
    
    def realizar_analisis_sintactico(self):
        """Realiza el análisis sintáctico del código en el editor"""
        if not MODULOS_CARGADOS:
            messagebox.showerror("Error", "No se pudieron cargar los módulos necesarios.")
            return
        
        # Obtener el código del editor
        codigo = self.editor_codigo.get(1.0, tk.END)
        
        try:
            # Primero realizar el análisis léxico
            self.tokens = AnalizadorLexico.analizar(codigo)
            
            # Mostrar los tokens en la tabla
            self.mostrar_tokens_en_tabla()
            
            # Realizar el análisis sintáctico
            analizador = AnalizadorSintactico(self.tokens)
            es_valido = analizador.analizar()
            
            # Mostrar errores sintácticos
            self.texto_errores_sintacticos.delete(1.0, tk.END)
            if es_valido:
                self.texto_errores_sintacticos.insert(tk.END, "No se encontraron errores sintácticos.")
            else:
                for error in analizador.get_errores():
                    self.texto_errores_sintacticos.insert(tk.END, f"{error}\n")
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Análisis sintáctico completado. Código {'válido' if es_valido else 'inválido'}.")
            
            # Cambiar a la pestaña de errores sintácticos si hay errores
            if not es_valido:
                self.notebook.select(self.tab_errores_sintacticos)
            else:
                self.notebook.select(self.tab_tokens)
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar el análisis sintáctico: {str(e)}")
    
    def realizar_analisis_completo(self):
        """Realiza tanto el análisis léxico como el sintáctico"""
        # Obtener el código del editor
        codigo = self.editor_codigo.get(1.0, tk.END)
        
        if not MODULOS_CARGADOS:
            messagebox.showerror("Error", "No se pudieron cargar los módulos necesarios.")
            return
        
        try:
            # Análisis léxico usando AnalizadorRobot (más detallado)
            self.tokens_robot = AnalizadorRobot.analizar(codigo)
            
            # Mostrar errores léxicos
            errores_lexicos = AnalizadorRobot.obtener_errores(self.tokens_robot)
            self.texto_errores_lexicos.delete(1.0, tk.END)
            self.texto_errores_lexicos.insert(tk.END, errores_lexicos)
            
            # Análisis léxico usando AnalizadorLexico (para el sintáctico)
            self.tokens = AnalizadorLexico.analizar(codigo)
            
            # Mostrar los tokens en la tabla
            self.mostrar_tokens_en_tabla()
            
            # Análisis sintáctico
            analizador = AnalizadorSintactico(self.tokens)
            es_valido = analizador.analizar()
            
            # Mostrar errores sintácticos
            self.texto_errores_sintacticos.delete(1.0, tk.END)
            if es_valido:
                self.texto_errores_sintacticos.insert(tk.END, "No se encontraron errores sintácticos.")
            else:
                for error in analizador.get_errores():
                    self.texto_errores_sintacticos.insert(tk.END, f"{error}\n")
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Análisis completo finalizado. Código {'válido' if es_valido else 'inválido'}.")
            
            # Decidir qué pestaña mostrar
            hay_errores_lexicos = "No se encontraron errores léxicos" not in errores_lexicos
            
            if hay_errores_lexicos:
                self.notebook.select(self.tab_errores_lexicos)
            elif not es_valido:
                self.notebook.select(self.tab_errores_sintacticos)
            else:
                self.notebook.select(self.tab_tokens)
        except Exception as e:
            messagebox.showerror("Error", f"Error al realizar el análisis completo: {str(e)}")
    
    def mostrar_tokens_en_tabla(self):
        """Muestra los tokens en la tabla"""
        # Limpiar la tabla
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        
        # Agregar cada token a la tabla
        for token in self.tokens:
            # Extraer la información del token
            lexema = token.get_lexema()
            tipo = token.get_tipo().name
            
            # El valor puede estar en diferentes atributos dependiendo de la clase
            valor = ""
            if hasattr(token, 'get_valor') and callable(getattr(token, 'get_valor')):
                valor = token.get_valor()
            
            linea = token.get_linea()
            columna = token.get_columna()
            
            # Agregar a la tabla
            self.tabla_tokens.insert("", tk.END, values=(lexema, tipo, valor, linea, columna))
    
    def limpiar_resultados(self):
        """Limpia todos los resultados de análisis previos"""
        # Limpiar la tabla de tokens
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        
        # Limpiar los errores léxicos
        self.texto_errores_lexicos.delete(1.0, tk.END)
        
        # Limpiar los errores sintácticos
        self.texto_errores_sintacticos.delete(1.0, tk.END)
    
    def cargar_ejemplo_correcto(self):
        """Carga un ejemplo de código correcto en el editor"""
        self.editor_codigo.delete(1.0, tk.END)
        self.editor_codigo.insert(tk.END, self.codigo_ejemplo)
        self.actualizar_lineas()
        self.limpiar_resultados()
        self.barra_estado.config(text="Ejemplo de código correcto cargado")
    
    def cargar_ejemplo_errores(self):
        """Carga un ejemplo de código con errores en el editor"""
        codigo_con_errores = """Robot r1
r1.iniciar()
r1.velocidad=150
r1.@base=45
r1.brazo=45
r1.cuerpo45
r1.garra=
r1.cerrarGarra
finalizar()"""
        
        self.editor_codigo.delete(1.0, tk.END)
        self.editor_codigo.insert(tk.END, codigo_con_errores)
        self.actualizar_lineas()
        self.limpiar_resultados()
        self.barra_estado.config(text="Ejemplo de código con errores cargado")
    
    def mostrar_gramatica(self):
        """Muestra la gramática del lenguaje"""
        info_gramatica = """
Gramática del Lenguaje de Control del Brazo Robótico
===================================================

REGLAS GRAMATICALES:

programa -> declaracionRobot instrucciones

declaracionRobot -> PALABRA_R IDENTIFICADOR

instrucciones -> instruccion instrucciones | ε

instruccion -> IDENTIFICADOR PUNTO (accion | asignacion)

accion -> ACCION PARENTESIS_IZQ PARENTESIS_DER

asignacion -> METODO IGUAL NUMERO

TOKENS:

PALABRA_R: 'Robot'
IDENTIFICADOR: [a-zA-Z][a-zA-Z0-9_]*
PUNTO: '.'
ACCION: 'iniciar' | 'finalizar' | 'cerrarGarra' | 'abrirGarra'
METODO: 'base' | 'cuerpo' | 'garra' | 'velocidad'
IGUAL: '='
NUMERO: [0-9]+
PARENTESIS_IZQ: '('
PARENTESIS_DER: ')'
COMENTARIO: '//' seguido de cualquier texto

RESTRICCIONES SEMÁNTICAS:

- base: valor entre 0 y 180 grados
- cuerpo: valor entre 0 y 90 grados
- garra: valor entre 0 y 180 grados
- velocidad: valor entre 1 y 100
"""
        ventana_gramatica = tk.Toplevel(self.root)
        ventana_gramatica.title("Gramática del Lenguaje")
        ventana_gramatica.geometry("600x500")
        
        texto_gramatica = scrolledtext.ScrolledText(ventana_gramatica, wrap=tk.WORD, 
                                                  width=70, height=25, font=("Consolas", 10))
        texto_gramatica.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        texto_gramatica.insert(tk.END, info_gramatica)
        texto_gramatica.config(state=tk.DISABLED)
    
    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        mensaje = """
Analizador de Lenguaje de Control de Brazo Robótico
Versión 1.0

Esta aplicación permite analizar el código fuente para 
controlar un brazo robótico utilizando un lenguaje
específico diseñado para este propósito.

Incluye:
- Análisis léxico
- Análisis sintáctico
- Detección de errores
- Validación semántica
"""
        messagebox.showinfo("Acerca de", mensaje)


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazAnalizadorRobot(root)
    root.mainloop()