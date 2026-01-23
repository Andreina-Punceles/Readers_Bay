import json 
import datetime 

# Al inicio de tu main o interfaz
with open("data/reseñas.json", "r", encoding="utf-8") as f:
    reseñas = json.load(f)
# --- 1. Funciones para Cargar y Guardar Datos ---
# (Sin cambios)
def cargar_datos(archivo):
    """Carga los datos desde un archivo JSON."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def guardar_datos(archivo, datos):
    """Guarda una lista de datos (diccionarios) en un archivo JSON."""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- 2. Lógica de Negocio (Libros) ---
# (Sin cambios)
def filtrar_libros(lista_libros, clave, valor):
    """Filtra la lista de libros por una clave y un valor (sin mayúsculas)."""
    resultados = []
    valor_buscado = valor.lower()
    for libro in lista_libros:
        valor_libro = str(libro.get(clave, '')).lower()
        if valor_buscado in valor_libro:
            resultados.append(libro)
    return resultados

def buscar_libro_por_id(lista_libros, id_buscado):
    """Busca un libro específico en la lista usando su ID."""
    try:
        id_num = int(id_buscado)
    except ValueError:
        return None 
    for libro in lista_libros:
        if libro['id'] == id_num:
            return libro
    return None

# --- 3. Lógica de Negocio (Reseñas) ---
# (MODIFICADO)

def buscar_reseñas_por_libro(lista_reseñas, libro_id):
    """Devuelve una lista de reseñas que coinciden con un libro_id."""
    resultados = []
    for reseña in lista_reseñas:
        if reseña['libro_id'] == libro_id:
            resultados.append(reseña)
    return resultados

def calcular_promedio(reseñas_del_libro):
    """Calcula el rating promedio de una lista de reseñas."""
    if not reseñas_del_libro:
        return 0
    suma = sum(r['rating'] for r in reseñas_del_libro)
    promedio = suma / len(reseñas_del_libro)
    return round(promedio, 1)

# --- NUEVA FUNCIÓN DE AYUDA ---
def buscar_indice_reseña(lista_reseñas, libro_id, usuario_id):
    """
    Busca si un usuario ya tiene una reseña para un libro.
    Retorna el ÍNDICE de la reseña si la encuentra, o None si no.
    """
    # Usamos enumerate para obtener tanto el índice (i) como el objeto (reseña)
    for i, reseña in enumerate(lista_reseñas):
        if reseña['libro_id'] == libro_id and reseña['usuario_id'] == usuario_id:
            return i # Retorna el índice (la posición en la lista)
    return None # No la encontró

# --- FUNCIÓN PRINCIPAL DE RESEÑAS (MODIFICADA) ---
def gestionar_reseña(lista_reseñas, libro_id, usuario_id):
    """
    Proceso para crear O EDITAR una reseña.
    Cumple la regla de negocio de "no duplicados".
    """
    
    # 1. Buscar si ya existe una reseña
    indice_existente = buscar_indice_reseña(lista_reseñas, libro_id, usuario_id)
    
    fecha_hoy = datetime.date.today().isoformat()
    
    if indice_existente is not None:
        # --- LÓGICA DE EDICIÓN ---
        reseña_vieja = lista_reseñas[indice_existente]
        print(f"\n  Ya tienes una reseña para este libro (de {reseña_vieja['fecha']}):")
        print(f"  Rating: {reseña_vieja['rating']}★ | Texto: '{reseña_vieja['texto']}'")
        
        confirmar = input("  ¿Deseas editarla? (s/n): ")
        if confirmar.lower() != 's':
            print("  Edición cancelada.")
            return lista_reseñas # Devuelve la lista sin cambios

        print("  --- Editando Reseña ---")
        # Pedir nuevos datos (Validación de Rating)
        rating = 0
        while True:
            try:
                rating_input = input(f"  Nuevo Rating (1-5) [Actual: {reseña_vieja['rating']
                }]: ")
                rating = int(rating_input)
                if 1 <= rating <= 5: break
                else: print("  ¡Error! El rating debe estar entre 1 y 5.")
            except ValueError:
                print("  ¡Error! Debes ingresar un número.")
        
        texto = input(f"  Nuevo Texto [Actual: '{reseña_vieja['texto']}']: ")
        
        # Modificar la reseña existente EN LA LISTA
        lista_reseñas[indice_existente]['rating'] = rating
        lista_reseñas[indice_existente]['texto'] = texto
        lista_reseñas[indice_existente]['fecha'] = fecha_hoy
        
        print("\n  ¡Reseña editada con éxito!")

    else:
        # --- LÓGICA DE AGREGAR (la que ya teníamos) ---
        print("\n  --- Nueva Reseña ---")
        # Pedir datos (Validación de Rating)
        rating = 0
        while True:
            try:
                rating_input = input("  Rating (1-5): ")
                rating = int(rating_input)
                if 1 <= rating <= 5: break
                else: print("  ¡Error! El rating debe estar entre 1 y 5.")
            except ValueError:
                print("  ¡Error! Debes ingresar un número.")

        texto = input("  Reseña (opcional): ")
        
        # Generar ID nuevo
        nuevo_id = lista_reseñas[-1]['id'] + 1 if lista_reseñas else 1

        nueva_reseña = {
            "id": nuevo_id,
            "libro_id": libro_id,
            "usuario_id": usuario_id,
            "rating": rating,
            "texto": texto,
            "fecha": fecha_hoy
        }
        
        lista_reseñas.append(nueva_reseña)
        print("\n  ¡Reseña guardada con éxito!")

    # 3. Guardar cambios (sea edición o nueva)
    guardar_datos(FILE_RESEÑAS, lista_reseñas)
    return lista_reseñas


# --- 4. Lógica de Negocio (Compartidos) ---
# (Sin cambios)

def buscar_compartidos_por_libro(lista_compartidos, libro_id):
    """Devuelve una lista de recomendaciones para un libro_id."""
    resultados = []
    for comp in lista_compartidos:
        if comp['libro_id'] == libro_id:
            resultados.append(comp)
    return resultados

def buscar_usuario_por_id(lista_usuarios, usuario_id):
    """Busca un usuario por su ID."""
    for u in lista_usuarios:
        if u['id'] == usuario_id:
            return u
    return None 

def agregar_compartido(lista_compartidos, lista_usuarios, libro_id, de_usuario_id):
    """Proceso para recomendar (compartir) un libro a otro usuario."""
    
    print("\n  --- Recomendar este libro ---")
    print("  ¿A qué usuario deseas recomendarlo?")
    
    usuarios_disponibles = []
    for u in lista_usuarios:
        if u['id'] != de_usuario_id:
            usuarios_disponibles.append(u)
            print(f"    [ID: {u['id']}] {u['nombre']}")
    
    if not usuarios_disponibles:
        print("  No hay otros usuarios a quién recomendar.")
        return lista_compartidos

    usuario_destino = None
    while True:
        try:
            id_destino_input = input("  Selecciona el ID del destinatario: ")
            id_destino = int(id_destino_input)
            
            if id_destino == de_usuario_id:
                print("  ¡Error! No puedes recomendarte un libro a ti mismo.")
                continue

            usuario_destino = buscar_usuario_por_id(usuarios_disponibles, id_destino)
            if usuario_destino: break 
            else: print("  ¡Error! ID de usuario no válido.")
        except ValueError:
            print("  ¡Error! Debes ingresar un número.")

    nota = input(f"  Nota para {usuario_destino['nombre']} (opcional): ")
    nuevo_id = lista_compartidos[-1]['id'] + 1 if lista_compartidos else 1
    fecha_hoy = datetime.date.today().isoformat()

    nuevo_compartido = {
        "id": nuevo_id,
        "de_usuario_id": de_usuario_id,
        "a_usuario_id": usuario_destino['id'],
        "libro_id": libro_id,
        "fecha": fecha_hoy,
        "nota": nota
    }
    
    lista_compartidos.append(nuevo_compartido)
    guardar_datos(FILE_COMPARTIDOS, lista_compartidos) 
    
    print(f"\n  ¡Libro recomendado a {usuario_destino['nombre']} con éxito!")
    return lista_compartidos

# --- 5. Carga Inicial ---
# (Sin cambios)
FILE_LIBROS = 'data/libros.json'
FILE_USUARIOS = 'data/usuarios.json'
FILE_RESEÑAS = 'data/reseñas.json'
FILE_COMPARTIDOS = 'data/compartidos.json'

libros = cargar_datos(FILE_LIBROS)
usuarios = cargar_datos(FILE_USUARIOS)
reseñas = cargar_datos(FILE_RESEÑAS)
compartidos = cargar_datos(FILE_COMPARTIDOS)

USUARIO_ACTUAL = usuarios[0] 
print(f"¡Bienvenido a tu Club de Libros, {USUARIO_ACTUAL['nombre']}!")
print(f"Total de libros cargados: {len(libros)}")

# --- 6. Flujo por consola - BUCLE PRINCIPAL ---
# (Solo un pequeño cambio en la llamada a la función)
while True:
    print("\n--- Menú Principal: Búsqueda de Libros ---")
    filtro_autor = input("Escribe el nombre de un autor para filtrar (o ENTER para ver todos): ")

    if filtro_autor:
        libros_mostrados = filtrar_libros(libros, 'autor', filtro_autor)
        print(f"\n--- Resultados para: '{filtro_autor}' ---")
    else:
        libros_mostrados = libros
        print("\n--- Mostrando Todos los Libros ---")

    if not libros_mostrados:
        print("No se encontraron libros para ese filtro.")
        continue 

    for libro in libros_mostrados:
        print(f"  [ID: {libro['id']}] {libro['titulo']} - {libro['autor']}")
    
    print("---------------------------------")
    id_seleccionado = input("Escribe el ID de un libro para ver su detalle (o 's' para salir): ")

    if id_seleccionado.lower() == 's':
        break 

    libro_detalle = buscar_libro_por_id(libros, id_seleccionado)

    if libro_detalle:
        print("\n--- Detalle del Libro ---")
        print(f"  ID:      {libro_detalle['id']}")
        print(f"  Título:  {libro_detalle['titulo']}")
        print(f"  Autor:   {libro_detalle['autor']}")
        
        reseñas_del_libro = buscar_reseñas_por_libro(reseñas, libro_detalle['id'])
        promedio_libro = calcular_promedio(reseñas_del_libro)
        print(f"\n  Calificación Promedio: {promedio_libro} ★ ({len(reseñas_del_libro)} reseñas)")
        
        if reseñas_del_libro:
            print("  --- Reseñas ---")
            for r in reseñas_del_libro:
                user = buscar_usuario_por_id(usuarios, r['usuario_id'])
                nombre_usuario = user['nombre'] if user else "Usuario Desconocido"
                print(f"    * {nombre_usuario} ({r['fecha']}) - {r['rating']}★: '{r['texto']}'")
        
        compartidos_del_libro = buscar_compartidos_por_libro(compartidos, libro_detalle['id'])
        print(f"\n  --- Recomendaciones ({len(compartidos_del_libro)}) ---")
        if compartidos_del_libro:
            for c in compartidos_del_libro:
                user_de = buscar_usuario_por_id(usuarios, c['de_usuario_id'])
                user_a = buscar_usuario_por_id(usuarios, c['a_usuario_id'])
                nombre_de = user_de['nombre'] if user_de else "?"
                nombre_a = user_a['nombre'] if user_a else "?"
                print(f"    * {nombre_de} recomendó a {nombre_a} ({c['fecha']})")
                if c.get('nota'):
                    print(f"      Nota: '{c['nota']}'")

        print("---------------------------------")
        print("  ¿Qué deseas hacer?")
        print("  1. Agregar o Editar mi reseña")
        print("  2. Recomendar (Compartir) este libro")
        print("  (Presiona ENTER para volver al menú)")
        
        accion_detalle = input("  Elige una opción (1, 2 o ENTER): ")
        
        if accion_detalle == '1':
            # --- CAMBIO AQUÍ ---
            # Llamamos a la nueva función
            reseñas = gestionar_reseña(reseñas, libro_detalle['id'], USUARIO_ACTUAL['id'])
            
        elif accion_detalle == '2':
            compartidos = agregar_compartido(compartidos, usuarios, libro_detalle['id'], USUARIO_ACTUAL['id'])
            
        else:
            pass 
            
    else:
        print(f"\n¡Error! No se encontró ningún libro con el ID '{id_seleccionado}'.")

    input("\n... Presiona ENTER para continuar ...")

print("\n¡Gracias por usar el Club de Libros! ¡Hasta pronto!")