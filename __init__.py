import os
from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
from .db import get_usuarios, existing_user, insert_user, get_user, delete_user, update_user, already_exists_user_name, \
                get_planta, get_municipio, get_estado, registrar_nueva_planta, obtener_plantas_registradas, actualizar_planta, estado_p_planta, eliminar_planta, \
                get_desc_plantas, get_desc_planta_json, get_docs_plantas, get_nombres_plantas, get_personal, get_info_planta, \
                get_params_planta, get_resmuestra_compuesta, get_resmuestra_simple, \
                get_capitulos_plantas, get_resmuestra_caudal, get_muestreos_tipos_planta, \
                get_datosgraf_resmuestra_caudal, get_resmuestra_tox, get_limitantes, \
                get_campos_etiq_tabla, get_datos_plantas
from flask_login import LoginManager,login_user,logout_user, login_required,current_user
from .models.Usuario import Usuario

def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    # manejo de usuarios loggeados
    login_manager_app=LoginManager(app)
    app.config.from_mapping(
        SECRET_KEY='dev'
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        #print ("SECRET: " + str(app.secret_key))
        #print (app.config['DBCONFIG'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @login_manager_app.user_loader
    def load_user(id_usuario):
        return db.busca_usuario_por_id(id_usuario)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('Login'))

    @app.route('/')
    def Raiz():
        if ( current_user.is_active):
            return redirect(url_for('Inicio'))    
        else:
            return redirect(url_for('Login'))
        #return render_template('inicio.html')

    @app.route('/inicio')
    @login_required
    def Inicio():
        return render_template('inicio.html')

### Control de usuarios de la app

    @app.route('/login', methods=['GET','POST'])
    def Login():
        if ((request.method=='POST') and (request.form['formId']!=None)):
            if ('checkAsAnonimo' in request.form):
                frm_usr='anonimo'
                frm_password='anonimo'
            else:
                frm_usr=request.form['usuario']
                frm_password=request.form['password']
            print(frm_usr)
            print(frm_password)
                
            usuario=Usuario(0,frm_usr,frm_password)
            usuario_identificado=db.identifica_usuario(usuario)
                
            if usuario_identificado!=None:
                if (usuario_identificado.clave):
                    login_user(usuario_identificado)
                    return redirect(url_for('Inicio'))
                else:
                    flash("Clave incorrecta")
                    return render_template('identifica.html')
            else:
                flash("Usuario no registrado")
                return render_template('identifica.html')
        else:
            return render_template('identifica.html')

    @app.route('/mostrar_usuarios')
    @login_required
    def MostrarUsuarios():
        usuarios = get_usuarios()
        return render_template('muestra_usuarios.html', usuarios=usuarios)

    @app.route('/registro', methods=['GET', 'POST'])
    @login_required
    def Registro():
        usr=None
        print("Method: "+request.method)
        if request.method == 'POST':
            nombre_usuario = request.form['nombre_usuario']
            nombre = request.form['nombre']
            apellido_paterno = request.form['apellido_paterno']
            apellido_materno = request.form['apellido_materno']
            telefono_movil = request.form['telefono_movil']
            clave = request.form['clave']  
            rol = request.form['rol']
            activo = request.form['activo']
            usr = Usuario(-1,nombre_usuario, clave, rol, nombre, apellido_paterno, apellido_materno, telefono_movil, activo)
            if existing_user(nombre_usuario):
                flash("Nombre de usuario ya registrado. Elige un nombre de usuario diferente.", 'danger')
            else:
                # Si el nombre de usuario no existe, procede con la inserciÃ³n
                if insert_user(nombre_usuario, clave, rol, nombre, apellido_paterno, apellido_materno, telefono_movil, activo):
                    flash("Usuario registrado con éxito.", 'success')
                else:
                    flash("Error al insertar usuario.", 'danger')
            #print("rol: "+usr.rol_id+", activo: "+usr.activo)
        return render_template('registrar_usuario.html', usuario=usr, modo_edicion=False)


    @app.route('/Delete/<string:id_usuario>', methods=['GET', 'POST'])
    @login_required
    def DeleteUser(id_usuario):
        # Verifica si el usuario existe antes de eliminarlo
        if delete_user(id_usuario):
            flash("Usuario eliminado con éxito.", 'success')
        else:
            flash("El usuario no existe.", 'danger')

        return redirect("/mostrar_usuarios")

    @app.route('/Edit/<string:id_usuario>', methods=['GET'])
    @login_required
    def EditUser(id_usuario):
        user=get_user(id_usuario)
        #id, nombre_usuario, clave, rol_id=-1, nombre="", apellido_paterno="", apellido_materno="", telefono_movil=-1, activo=-1
        #id_usuario, nombre_usuario, clave, rol_id, nombre, apellido_paterno, apellido_materno, telefono_movil, activo
        user1=Usuario(user[0],user[1],user[2],user[3],user[4],user[5], user[6], user[7], user[8] )
        return render_template('registrar_usuario.html', usuario=user1, modo_edicion=True)
    
    @app.route('/Update/<string:id_usuario>', methods=['POST'])
    @login_required
    def UpdateUser(id_usuario):
        try:
            if request.method == 'POST':
                nuevo_nombre = request.form['nombre']
                nuevo_apellido_paterno = request.form['apellido_paterno']
                nuevo_apellido_materno = request.form['apellido_materno']
                nuevo_telefono_movil = request.form['telefono_movil']
                nuevo_nombre_usuario = request.form['nombre_usuario']
                nuevo_rol = request.form['rol']
                nuevo_activo = 1 if 'activo' in request.form else 0  # Verifica si 'activo' 
                nueva_clave = request.form['clave']

                if already_exists_user_name(id_usuario, nuevo_nombre_usuario):
                    flash("El nombre de usuario ya está en uso. Elija otro nombre de usuario.", 'danger')
                    return redirect(f"/Edit/{id_usuario}")

                if ( update_user(id_usuario, nuevo_nombre, nuevo_apellido_paterno, nuevo_apellido_materno, nuevo_telefono_movil, nuevo_nombre_usuario, nuevo_rol, nuevo_activo, nueva_clave) ):
                    flash("Usuario actualizado con éxito.", 'success')
                    return redirect('/mostrar_usuarios')
                
        except Exception as e:
            flash("Error al actualizar el usuario. Por favor, inténtelo de nuevo.", 'danger')
            print(str(e))  
            return redirect(f"/Edit/{id_usuario}")

###### PLANTAS #################################

    @app.route('/mostrar_planta')
    @login_required
    def mostrar_planta():
            plantas = get_planta()
            return render_template('muestra_plantas.html', plantas = plantas)
    

    # Ruta para mostrar el formulario
    @app.route('/mostrar_formulario_registro_planta', methods=['GET'])
    @login_required
    def mostrar_formulario_registro_planta():
        municipios = get_municipio()
        estados = get_estado()
        return render_template('registro_planta.html', municipios=municipios, estados=estados)

    # Ruta para manejar la acciÃ³n de registro
    @app.route('/registrar_planta', methods=['POST'])
    @login_required
    def registrar_planta():
        try:
            nombre_oficial = request.form['nombre_oficial']
            estado = request.form['estado']
            municipio = request.form['municipio']
            colonia = request.form['colonia']
            calle = request.form['calle']
            numero = request.form['numero']
            codigo_postal = request.form['cp']
            coordenada_latitud = request.form['latitud']
            coordenada_longitud = request.form['longitud']
            superficie = request.form['superficie']
            caudal_entrada = request.form['caudal_entrada']
            influente_industrial = request.form['influente']

            f_construccion= request.form['fecha_inicio_construccion']
            f_finalizacion = request.form['fecha_final_construccion']
            f_i_operacion = request.form['inicio_operacion']
            p_beneficiada = request.form['poblacion_beneficiada']
            a_actualizacion = request.form['anio_actualizacion']
            tipo_tratamiento = request.form['tipo_tratamiento']
            gasto_diseño = request.form['gasto_diseno']
            gasto_estiaje = request.form['gasto_o_estiaje']
            gasto_lluvia = request.form['gasto_o_lluvia']
            institucion = request.form['institucion']
            nombre_responsabel = request.form['nombre_responsable']
            telefono_responsable  = request.form['telefono_responsable']
            cargo_responsable = request.form['cargo_responsable']
            email_responsable = request.form['email_responsable']
            permiso_descarga = request.form['punto_descarga']
            fecha_registro = request.form['fecha_registro']
            tipo_descarga = request.form['tipo_descarga']
            volumen_descarga = request.form['volumen_descarga']

            registrar_nueva_planta(nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
                                    calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
                                    f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
                                    tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
                                    institucion,nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
                                    permiso_descarga,fecha_registro, tipo_descarga, volumen_descarga)

            flash("Registro exitoso", 'success')
            return redirect(url_for('mostrar_planta'))
        except Exception as e:
            flash("Error al registrar la planta. Por favor, intÃ©ntelo de nuevo.", 'error')
            print(str(e))
            return redirect(url_for('mostrar_formulario_registro_planta'))


    @app.route('/Edit_info_ptar/<string:planta_id>', methods=['GET'])
    @login_required
    def Edit_info_ptar(planta_id):
        planta = obtener_plantas_registradas(planta_id)
        return render_template('editar_ptars.html', planta=planta)
    

    @app.route('/Update_datos_planta/<string:planta_id>', methods=['POST'])
    @login_required
    def Update_datos_planta(planta_id):
        try:
            if request.method == 'POST':
                nombre_oficial = request.form['nombre_ptar']
                estado = request.form['estado']
                municipio = request.form['municipio_id']
                colonia = request.form['colonia']
                calle = request.form['calle']
                numero = request.form['numero']
                codigo_postal = request.form['cp']
                coordenada_latitud = request.form['latitud']
                coordenada_longitud = request.form['longitud']
                superficie = request.form['superficie']
                caudal_entrada = request.form['caudal_entrada']
                influente_industrial = request.form['influente']

                f_construccion= request.form['fecha_inicio_construccion']
                f_finalizacion = request.form['fecha_final_construccion']
                f_i_operacion = request.form['inicio_operacion']
                p_beneficiada = request.form['poblacion_beneficiada']
                a_actualizacion = request.form['anio_actualizacion']
                tipo_tratamiento = request.form['tipo_tratamiento']

                gasto_diseño = request.form['gasto_diseno']
                gasto_estiaje = request.form['gasto_o_estiaje']
                gasto_lluvia = request.form['gasto_o_lluvia']
                institucion = request.form['institucion']
                nombre_responsabel = request.form['nombre_responsable']
                telefono_responsable  = request.form['telefono_responsable']
                cargo_responsable = request.form['cargo_responsable']
                email_responsable = request.form['email_responsable']

                permiso_descarga = request.form['punto_descarga']
                fecha_registro = request.form['fecha_registro']
                tipo_descarga = request.form['tipo_descarga']
                volumen_descarga = request.form['volumen_descarga']

                actualizar_planta(
                nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
                calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
                f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
                tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
                institucion, nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
                permiso_descarga, fecha_registro, tipo_descarga, volumen_descarga,
                planta_id)
                flash("Planta actualizada con Ã©xito.", 'success')
                return redirect(url_for('mostrar_planta'))
        except Exception as e:
            flash("Error al actualizar la planta. Por favor, intÃ©ntelo de nuevo.", 'error')
            print(str(e))
            return redirect(f"/Edit_info_ptar/{planta_id}")

    @app.route('/get_municipios', methods=['GET'])
    @login_required
    def GetMunicipios():
        estado_id = request.args.get('estado_id')
        municipios=estado_p_planta(estado_id)
        return municipios
        
    @app.route('/Delete_planta/<int:planta_id>', methods=['GET', 'POST'])
    @login_required  # AsegÃºrate de tener la funciÃ³n login_required configurada
    def DeletePlanta(planta_id):
        eliminar_planta(planta_id)
        flash("Planta eliminada con Ã©xito.", 'success')
        return redirect("/mostrar_planta")


################################################################

    @app.route('/localizacion', methods=['POST','GET'])
    @login_required
    def Localiza():
        return render_template('localiza.html', lista_plantas=get_nombres_plantas())

    @app.route('/consulta_desc_planta', methods=['POST','GET'])
    @login_required
    def ConsultaDescPlanta():
        planta=request.args.get("planta")
        return get_desc_planta_json(planta)

    @app.route('/datos_personal')
    @login_required
    def DatosPersonal():
        plantas=get_nombres_plantas('Select distinct planta_id from personal')
        return render_template('datos_personal.html',lista_plantas=plantas)

    @app.route('/consulta_personal')
    @login_required
    def ConsultaPersonal():
        planta=request.args.get("planta")
        if planta is None:
            return  []
        else:
            return  get_personal(planta)

    @app.route('/info_plantas')
    @login_required
    def InfoPlantas():
        plantas=get_nombres_plantas()
        return render_template('info_plantas.html',lista_plantas=plantas)

    @app.route('/consulta_info_planta')
    @login_required
    def consulta_info_planta():
        planta=request.args.get("planta")
        print("Consulta info planta: "+planta)
        if planta != None:
            return  get_info_planta(planta)        
        return []


################################################################
# funciones nuevas no presentes en la versión compartida a Alejandro

    @app.route('/info_general', methods=['POST','GET'])
    @login_required
    def InfoGeneral():
        plantas, etiquetas=get_desc_plantas()
        return render_template('info_general.html', lista_plantas=plantas, etiquetas_plantas=etiquetas)

    @app.route('/params_planta')
    @login_required
    def ParamsPlanta():
        plantas=get_nombres_plantas()
        return render_template('params_planta.html',lista_plantas=plantas)

    @app.route('/consulta_params_planta')
    @login_required
    def consulta_params_planta():
        planta=request.args.get("planta")
        print("Consulta params planta : "+planta)
        if planta != None:
            return  get_params_planta(planta)        
        return []

    @app.route('/resmuestra_compuesta', methods=['POST','GET'])
    @login_required
    def ResMuestraCompuesta():
        plantas=get_nombres_plantas()
        return render_template('resmuestra_compuesta.html',lista_plantas=plantas)

    @app.route('/consulta_resmuestra_compuesta', methods=['POST','GET'])
    @login_required
    def consulta_resmuestra_compuesta():
        planta=request.args.get("planta")
        params=request.args.get("params")
        tipo=request.args.get("tipo")
        filtraCNN=request.args.get("filtraCNN")
        muestraPlantas=request.args.get("muestraPlantas")
        if filtraCNN==None:
            filtraCNN=True; # valor por defecto: true
        if muestraPlantas==None:
            muestraPlantas=False; # valor por defecto: false
        print("Consulta resmuestra_compuesta : "+planta)
        if planta != None:
            return  get_resmuestra_compuesta(planta, params, tipo, filtraCNN, muestraPlantas)
        return []

    #ojo: este consulta se usa para caudal y toxicidad
    @app.route('/consulta_muestreos_tipos_planta', methods=['POST','GET'])
    @login_required
    def consulta_muestreos_tipos_planta():
        tabla=request.args.get("tabla")
        planta=request.args.get("planta")
        print('muestreos_tipo tabla:'+tabla+", planta: "+planta);
        if (tabla!=''):
            tabla='resmuestra_'+tabla
        return  get_muestreos_tipos_planta(tabla, planta)        

    # ojo: esta misma url y método se usan para la consulta de los análisis del caudal y de toxicidad
    @app.route('/consulta_resmuestra_caudal_tox')
    @login_required
    def consulta_resmuestra_caudal_tox():
        tabla=request.args.get("tabla")
        planta=request.args.get("planta")
        muestreo=request.args.get("muestreo")
        tipo=request.args.get("tipo")
        print("Consulta resmuestra_caudal_tox : "+tabla+","+planta+","+muestreo+","+tipo)
        if planta != None:
            if (tabla=='caudal'):
                return  get_resmuestra_caudal(planta, muestreo, tipo)        
            if (tabla=='tox'):
                return  get_resmuestra_tox(planta, muestreo, tipo)        
        return []

    @app.route('/consulta_datosgraf_resmuestra_caudal')
    @login_required
    def consulta_datosgraf_resmuestra_caudal():
        planta=request.args.get("planta")
        muestreo=request.args.get("muestreo")
        print("Consulta info planta: "+planta)
        if planta != None:
            return  get_datosgraf_resmuestra_caudal(planta, muestreo)        
        return []

    @app.route('/resmuestra_simple')
    @login_required
    def ResMuestraSimple():
        plantas=get_nombres_plantas()
        return render_template('resmuestra_simple.html',lista_plantas=plantas)

    @app.route('/consulta_resmuestra_simple')
    @login_required
    def consulta_resmuestra_simple():
        planta=request.args.get("planta")
        print("Consulta resmuestra_simple : "+planta)
        if planta != None:
            return  get_resmuestra_simple(planta)        
        return []

    @app.route('/resmuestra_tox', methods=['POST','GET'])
    @login_required
    def ResMuestraToxicidad():
        plantas=get_nombres_plantas()
        return render_template('resmuestra_toxicidad.html',lista_plantas=plantas)

    @app.route('/limitantes', methods=['POST','GET'])
    @login_required
    def Limitantes():
        plantas=get_nombres_plantas()
        return render_template('limitantes.html',lista_plantas=plantas)
    
    @app.route('/consulta_limitantes')
    @login_required
    def consulta_limitantes():
        planta=request.args.get("planta")
        nivel=request.args.get("nivel")
        plazo=request.args.get("plazo")
        if (nivel==None):
            nivel='*'
        if (plazo==None):
            plazo='*'    
        if (planta != None):
            return  get_limitantes(planta, nivel,plazo)
        return []
  
    @app.route('/doc_diagnostico')
    @login_required
    def Doc_Diagnostico():
        caps_plantas=get_capitulos_plantas();
        nom_plantas=get_nombres_plantas('','doc_diagnostico');
        return render_template('doc_cap_diagnostico.html',lista_plantas=nom_plantas,capitulos_planta=caps_plantas)

    @app.route('/compara_rmcomp_plantas', methods=['POST','GET'])
    @login_required
    def Compara_RMComp_Plantas():
        plantas=get_nombres_plantas()
        return render_template('compara_rm_compuesta.html',lista_plantas=plantas)

    @app.route('/compara_plantas', methods=['POST','GET'])
    @login_required
    def ComparaPlantas():
        plantas=get_nombres_plantas()
        ce=get_campos_etiq_tabla('planta',1)
        return render_template('compara_plantas.html',lista_plantas=plantas, campos_etiquetas=ce)

    @app.route('/consulta_campos_etiq_tabla', methods=['POST','GET'])
    @login_required
    def ConsultaCamposEtiqTabla():
        tabla=request.args.get("tabla")
        consulta=request.args.get("consulta")
        return get_campos_etiq_tabla(tabla,consulta)

    @app.route('/consulta_campos_planta', methods=['POST','GET'])
    @login_required
    def ConsultaCamposPlanta():
        plantas=request.args.get("planta")
        campos=request.args.get("campos")
        return get_datos_plantas(plantas,campos)
    
    @app.route('/tablero')
    @login_required
    def Tablero():
        return "<br><b> En construcción... </b>"
    
    @app.route('/reportes')
    @login_required
    def Reportes():
        return "<br><b> En construcción... </b>"

    
## REGRESA LA APP
    return app
