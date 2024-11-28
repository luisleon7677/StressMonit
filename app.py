from flask import Flask, jsonify
from flask import render_template , redirect , request, Response, session, url_for
import sqlite3
from supabase import create_client, Client
from flask_mail import Mail, Message

app = Flask(__name__, template_folder='template')

# Configuración para Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'luisleon7677@gmail.com'  # Tu correo de Gmail
app.config['MAIL_PASSWORD'] = 'qzjw sxtb xthh vnbk'  # Tu contraseña de Gmail (o contraseña de app si tienes habilitada la verificación en dos pasos)
app.config['MAIL_DEFAULT_SENDER'] = 'luisleon7677@gmail.com'  # Remitente por defecto (tu correo)

mail = Mail(app)

#carpeta inicio madre
@app.route('/')
def home():
    return render_template('index.html')

#admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

#funcion de login
@app.route('/acceso-login',methods = ["GET","POST"])
def login():
    if request.method == 'POST' and 'correo' in request.form and 'password'in request.form:
        _correo = request.form['correo']
        _password = request.form['password']
        # Consultar la tabla Admin en Supabase
        response = supabase.table("Admin").select("*").eq("Correo", _correo).eq("Password", _password).execute()
        
        account = response.data
        
        if account:
            session['logueado'] = True
            session['id'] = account[0]['id']  # Asegúrate de que 'id' sea el nombre de la columna
            return render_template("home.html")
                     
        else:
            return render_template('index.html')
    
    else:     
        return render_template('index.html')  # Muestra el formulario en caso de GET
        

#registro
@app.route('/registro')
def registro():
    return render_template('registro.html')

#crear registro
@app.route('/crear-registro',methods = ["GET","POST"])
def crear_registro():
    if request.method == 'POST':
        #recibo datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        cargo = request.form['cargo']
        organizacion = request.form['organizacion']
        correo = request.form['correo']
        password = request.form['password']
        
        #Enviar a la base de datos
        
        response = (
        supabase.table("Admin")
        .insert({"Nombres": nombre, "Apellidos": apellido,"Edad":edad,'Cargo':cargo,'Organizacion':organizacion,'Correo':correo,'Password':password})
        .execute()
        )
       
        
        return render_template('index.html')
    else:
        return render_template('registro.html')

    #conectarme a base de datos
    
    # Ejecutar la consulta para verificar el usuario
   
    
 
 
# Configuracion de supabase
url = "https://ywguvjqbpghumydqawas.supabase.co"  # Reemplaza con tu URL de Supabase
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl3Z3V2anFicGdodW15ZHFhd2FzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk5NjcwNTYsImV4cCI6MjA0NTU0MzA1Nn0.eYT4XYraGvHkESQHfXzE5BISKHY6E2gda-RfiZ4frmg"  # Reemplaza con tu clave de Supabase
supabase: Client = create_client(url, key)

@app.route('/home')
def inicio():
     #consultar a la base de datos
    response = supabase.table("Proceso").select("*").execute()
    actividades = response.data
    #id = data[0]['id']
    #Crearemos el diccionario que necesitamos
    #el diccionario conta de las siguientes partes{id_act,nombre, actividad,duración total, estres promedio}
    #creamos el diccionario
    acumuladores = {}
    #recorremos la lista de actividades
    for actividad in actividades:
        acti_id = actividad['acti_id']
        duracion= actividad['duracion']
        estres = actividad['estres']
        # si el id_acti ya existe en el diccionario
        if acti_id in acumuladores:
            #Actualizar la duración acumulada
            acumuladores[acti_id]['duracion']+=duracion
            #acumular el estres
            acumuladores[acti_id]['estres_total']+=estres
            #aumentar el contador
            acumuladores[acti_id]['conteo']+=1
        
        # si no existe creamos en el diccionario    
        else:
            # consultar el nombre de la actividad por medio del id
            nombre = consultar_nombre_actXid(acti_id)
            acumuladores[acti_id]={
                'nombre':nombre,
                'duracion':duracion,
                'estres_total':estres,
                'conteo':1 # el conteo sirve para saber cuantas veces a sido registrada esa actividad
            }
            
        #{ Resultado final de ese diccionario
         #   6: {'duracion': 32, 'estres_total': 0, 'conteo': 2}, 
          #  7: {'duracion': 72, 'estres_total': 0, 'conteo': 2}, 
           # 1: {'duracion': 34, 'estres_total': 1, 'conteo': 3}
        #}
    
    
    #crear una lista de resultados
    resultado = []
    # promediar el estres
    for acti_id,data in acumuladores.items():
        promedio_estres = data['estres_total']/data['conteo'] # promedio de estres
        #redondeo a dos decimales
        promedio_estres = round(promedio_estres,2)
        resultado.append({
            'acti_id':acti_id,
            'nombre': data['nombre'],
            'duracion_acumulada':data['duracion'],
            'promedio_estres':promedio_estres
        })
    
    
    
    
    return render_template('home.html', resultado = resultado)

def consultar_nombre_actXid(acti_id: int) -> str:
    
    response = supabase.table('Actividades').select('nombre').eq('id', acti_id).single().execute()
    return response.data['nombre']

#salir de la app
@app.route('/loguot')
def loguot():
    return render_template('index.html')

#SECCION DE USUARIOS
#listar usuarios
@app.route('/usuarios')
def usuarios():
    #consultar la tabla de usuarios
    data = supabase.table("Usuarios").select("*").execute()
    usuarios = data.data
    #obtener las actividades de cada usuario
    usuarios_actividades = {}
    for usuario in usuarios:
        actividades = obtener_actividades_por_usuario(usuario['id'])
        usuarios_actividades[usuario['id']] = actividades
    
    return render_template('usuarios.html',usuarios = usuarios, usuarios_actividades=usuarios_actividades)
#registrar nuevos usuarios
@app.route('/registrar_usuarios',methods=["GET","POST"])
def registrar_usuarios():
    if request.method == 'POST':
        #recibimos los datos del formulario
        nombre =request.form['nombre']
        username = request.form['username']
        password = request.form['password']
        #los enviamos a la base de datos
        response = (
        supabase.table("Usuarios")
        .insert({"nombre": nombre, "username": username,"password":password})
        .execute()
        )
        print('registro exitoso')
        return redirect(url_for('usuarios'))
    
    
    return  render_template('usuarios.html')

#eliminar usuarios
@app.route('/eliminarUsuarios/<int:id>', methods = ["POST"])
def eliminar_usuarios(id):
    # Eliminar el registro del usuario basado en el ID
    response = supabase.table('Usuarios').delete().eq('id', id).execute()

    # Verificar si la eliminación fue exitosa
    print(response)
     # Verificar si la eliminación fue exitosa
    if response.data:
        return redirect(url_for('usuarios'))  # Redirige a la vista de usuarios
    else:
        return f"No se encontró un usuario con el ID {id} para eliminar", 404 
  
  
#Obtener datos de usuarios para ser modificados
@app.route('/update_users/<int:id>')
def update_user(id):
    print(f'id recolectado: {id}')
    #debemos obtener los datos del usuario con el id
    response = supabase.table('Usuarios').select('*').eq('id',id).execute()
    #los datos del json
    user_data = response.data[0]
    return render_template('modificarUsuarios.html',user = user_data) #estamos enviando todo el json a user    

#Actualziar registro de usuario
@app.route('/actualizar_user/<int:id>',methods = ['POST'])
def actualizar_usuarios(id):
    nombre = request.form['nombre']
    username = request.form['username']
    password = request.form['password']
    #modificar en base de datos
    response = supabase.table('Usuarios').update({
        'nombre': nombre,
        'username': username,
        'password':password
    }).eq('id', id).execute()
    
    return redirect(url_for('usuarios'))


#seccion de actividades
#listar actividades
@app.route('/actividades', methods = ['GET','POST'])
def actividades():
    
    if request.method == 'GET':
        #consultar a la base de datos
        response = supabase.table("Actividades").select("*").execute()
        actividades = response.data
        
        return render_template('actividades.html',list_actividades = actividades)
    
    else: #por metodo post
        #recibbimos los datos del formulario
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        grado_dif = request.form['dificultad']
        #registramos en la base de datos
        response = (
        supabase.table("Actividades")
        .insert({"nombre": nombre, "descripcion": descripcion,"grado_dif":grado_dif})
        .execute()
        )
        
        return render_template('usuarios.html')
        
#eliminar actividades
@app.route('/eliminarActividad/<int:id>', methods = ["POST"])
def eliminar_actividad(id):
    # Eliminar el registro del usuario basado en el ID
    response = supabase.table('Actividades').delete().eq('id', id).execute()

    # Verificar si la eliminación fue exitosa
    print(response)
     # Verificar si la eliminación fue exitosa
    if response.data:
        return redirect(url_for('actividades'))  # Redirige a la vista de usuarios
    else:
        return f"No se encontró una actividad con el ID {id} para eliminar", 404 

#editar actividades
@app.route('/edit_actividades/<int:id>')
def edit_activity(id):
     #debemos obtener los datos  con el id
    response = supabase.table('Actividades').select('*').eq('id',id).execute()
    #los datos del json
    actividades_data = response.data[0]
    return render_template('modificar_actividades.html',activity = actividades_data)

#modificar actividades
@app.route('/update_acti/<int:id>',methods = ['POST'])
def update_activities(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    grado_dif = request.form['grado_dif']
    #modificar en base de datos
    response = supabase.table('Actividades').update({
        'nombre': nombre,
        'descripcion': descripcion,
        'grado_dif':grado_dif
    }).eq('id', id).execute()
    
    return redirect(url_for('actividades'))

#Seccion para actividades por usuario
def obtener_actividades_por_usuario(user_id):
   # Consultar las actividades realizadas por el usuario desde la tabla 'Proceso'
    response_proceso = supabase.from_('Proceso').select('acti_id, fecha, VFC, FR, FC, estres').eq('user_id', user_id).execute()

    # Verificar si la respuesta contiene datos
    if not response_proceso.data:
        return []  # Si no hay datos, retornar una lista vacía

    actividades_data = response_proceso.data

    actividades = []
    for actividad in actividades_data:
        acti_id = actividad['acti_id']
        
        # Consultar el nombre de la actividad desde la tabla 'Actividades' usando 'acti_id'
        response_actividad = supabase.from_('Actividades').select('nombre').eq('id', acti_id).single().execute()
        
        # Verificar si la respuesta contiene datos de la actividad
        if response_actividad.data:
            nombre_actividad = response_actividad.data['nombre']
        else:
            nombre_actividad = 'Desconocida'

        # Agregar los datos de la actividad a la lista
        actividades.append({
            'nombre': nombre_actividad,
            'fecha': actividad['fecha'],
            'VFC': actividad['VFC'],
            'FR': actividad['FR'],
            'FC': actividad['FC'],
            'estres': actividad['estres']
        })

    return actividades

#-------------------

@app.route('/recursos')
def recursos():
    return render_template('recursos.html')

# seccion de soporte
@app.route('/soporte')
def soporte():
    return render_template('soporte.html')

# Ruta para procesar el formulario y enviar el correo
@app.route('/enviar-correo', methods=['POST'])
def enviar_correo():
    # Obtener los datos del formulario
    asunto = request.form['asunto']
    contenido = request.form['contenido']
    
    # Crear el mensaje
    msg = Message(subject=asunto,
                  recipients=['luisleon7677@gmail.com'],  # Dirección de correo de destino
                  body=contenido)
    
    try:
        # Enviar el correo
        mail.send(msg)
        return render_template('home.html')
    except Exception as e:
        return f'Ocurrió un error al enviar el correo: {str(e)}'




if __name__ == '__main__':
     app.secret_key= 'luis_1234'
     app.run(debug=True)
     
