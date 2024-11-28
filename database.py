import sqlite3

#conectar a base de datos (crearla)

conn = sqlite3.connect('escuela.db')
cursor = conn.cursor()

#crear tabla 
# Crear tabla Estudiantes
cursor.execute('''
CREATE TABLE IF NOT EXISTS Estudiantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
)
''')

# Crear tabla Cursos
cursor.execute('''
CREATE TABLE IF NOT EXISTS Cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
)
''')

# Crear tabla intermedia Estudiante_Curso
cursor.execute('''
CREATE TABLE IF NOT EXISTS Estudiante_Curso (
    estudiante_id INTEGER,
    curso_id INTEGER,
    PRIMARY KEY (estudiante_id, curso_id),
    FOREIGN KEY (estudiante_id) REFERENCES Estudiantes(id),
    FOREIGN KEY (curso_id) REFERENCES Cursos(id)
)
''')
# Guardar cambios y cerrar conexión
conn.commit()
conn.close()