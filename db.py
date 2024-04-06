import mariadb
import itertools
from flask import current_app, g, json, jsonify
from .models.Usuario import Usuario
from werkzeug.security import generate_password_hash

#from model import planta;

# DB access
def get_db():
    if 'db' not in g:      
        # connection for MariaDB
        g.db = mariadb.connect(**current_app.config['DBCONFIG'])
        # create a connection cursor
        #cur = conn.cursor()
        #g.db.row_factory = mariadb.Row
        #g.db.autocommit=True
    return g.db


def close_db(e=None):
    db=g.pop('db',None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

# Data access

def get_usuarios():
    cursor = get_db().cursor()
    cursor.execute('SELECT id_usuario, nombre_usuario, clave, rol_id, nombre, apellido_paterno, apellido_materno, telefono_movil, activo FROM usuario')
    usuarios = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return usuarios

# verifica el nombre del usuario
def existing_user(nombre_usuario):
    cursor = get_db().cursor()
    sql = "SELECT id_usuario FROM usuario WHERE nombre_usuario = ?"
    cursor.execute(sql, (nombre_usuario,))
    existing_user = cursor.fetchone()
    return existing_user

#devuelve el obj usuario de id_usuario de la bd
def get_user(id_usuario):
    cursor = get_db().cursor()
    sql = "SELECT * FROM usuario WHERE id_usuario = %s"
    cursor.execute(sql, (id_usuario,))
    return cursor.fetchone()

#devuelve true si existe el nombre del usuario para un id distinto
def already_exists_user_name(id_usuario, nombre_usuario):
    cursor = get_db().cursor()
    sql_check_username = "SELECT id_usuario FROM usuario WHERE nombre_usuario = %s AND id_usuario != %s"
    cursor.execute(sql_check_username, (nombre_usuario, id_usuario))
    return cursor.fetchone()!=None
   
def insert_user(nombre_usuario, clave, rol, nombre, apellido_paterno, apellido_materno, telefono_movil, activo):
    try:
        cursor = get_db().cursor()
        sql = """
            INSERT INTO usuario (nombre_usuario, clave, rol_id, nombre, apellido_paterno, apellido_materno, telefono_movil, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Genera un hash de la contraseña antes de almacenarla en la base de datos
        hash_clave = generate_password_hash(clave)
        cursor.execute(sql, (nombre_usuario, hash_clave, rol, nombre, apellido_paterno, apellido_materno, telefono_movil, activo))
        get_db().commit()
        return True    
    except:
        return False
     

def delete_user(id_usuario):
    try:
        cursor = get_db().cursor()    
        # Si el usuario existe, procede a eliminarlo
        sql_delete = "DELETE FROM usuario WHERE id_usuario = ?"
        cursor.execute(sql_delete, (id_usuario,))
        get_db().commit()
        return True
    except Exception as e:
        print(e)
        return False

def update_user(id_usuario, nuevo_nombre, nuevo_apellido_paterno, nuevo_apellido_materno, nuevo_telefono_movil, nuevo_nombre_usuario, nuevo_rol, nuevo_activo, nueva_clave):
    try:
        cursor = get_db().cursor()
        sql_update = """
            UPDATE usuario
            SET nombre = %s,
                apellido_paterno = %s,
                apellido_materno = %s,
                telefono_movil = %s,
                nombre_usuario = %s,
                rol_id = %s,
                activo = %s 
            WHERE id_usuario = %s
        """
        if nueva_clave:
            nueva_clave_hash = generate_password_hash(nueva_clave)
            sql_update = sql_update.replace("WHERE", ", clave = %s WHERE")
            cursor.execute(sql_update, (nuevo_nombre, nuevo_apellido_paterno, nuevo_apellido_materno, nuevo_telefono_movil, nuevo_nombre_usuario, nuevo_rol, nuevo_activo, nueva_clave_hash, id_usuario))
        else:
            cursor.execute(sql_update, (nuevo_nombre, nuevo_apellido_paterno, nuevo_apellido_materno, nuevo_telefono_movil, nuevo_nombre_usuario, nuevo_rol, nuevo_activo, id_usuario))
        get_db().commit()
        return True
    except:
        return False

####### PLANTAS #################################

### CAPTURA PLANTAS #################################

def get_planta():
    cursor = get_db().cursor()
    cursor.execute('SELECT p.id_planta, p.nombre_ptar, e.nombre as estado, m.nombre as municipio, p.colonia, p.calle, p.numero, p.cp, '\
                    'p.coord_latitud, p.coord_longitud, p.superficie, p.caudal_entrada, p.influente_industrial, '\
                    'p.fecha_inicio_const, p.fecha_fin_const, p.fecha_inicio_oper, p.poblacion_beneficiada, p.anio_actual, '\
                    'p.tipo_tratamiento, p.gasto_diseño, p.gasto_operacion_estiaje, p.gasto_operacion_lluvia, '\
                    'p.ro_nombre_institucion, p.ro_nombre, p.ro_puesto, p.ro_correo, p.ro_telefono '\
                    'FROM planta p '\
                    'LEFT JOIN estado e ON e.id_estado = p.estado_id '\
                    'LEFT JOIN municipio m ON m.id_municipio = p.municipio_id')
    plantas = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    
    return plantas

def get_municipio():
    cursor = get_db().cursor()
    cursor.execute ('SELECT id_municipio, local, nombre, estado_id, organismo_id FROM municipio')
    municipio = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return municipio

def get_estado():
    cursor = get_db().cursor()
    cursor.execute ('SELECT id_estado, nombre, abreviatura, variable FROM estado')
    estado = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return estado

def registrar_nueva_planta(
        nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
        calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
        f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
        tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
        institucion,nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
        permiso_descarga,fecha_registro, tipo_descarga, volumen_descarga):

    cursor = get_db().cursor()
    sql = """
        INSERT INTO planta (
            nombre_ptar, estado_id, municipio_id, coord_latitud, coord_longitud,
            calle, numero, colonia, cp, superficie, caudal_entrada, influente_industrial, 
            fecha_inicio_const, fecha_fin_const, fecha_inicio_oper, poblacion_beneficiada,
            anio_actual, tipo_tratamiento, gasto_diseño, gasto_operacion_estiaje, gasto_operacion_lluvia,

            ro_nombre_institucion, ro_nombre, ro_puesto, ro_correo, ro_telefono
            , permiso_descarga, fecha_registro_permiso, tipo_descarga, volumen_descarga
        )   
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            
        )
    """

    cursor.execute(sql, (
        nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
        calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
        f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
        tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
        institucion,nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
        permiso_descarga,fecha_registro, tipo_descarga, volumen_descarga
    ))

    get_db().commit()
    cursor.close()
    return

def obtener_plantas_registradas(planta_id):
    cursor = get_db().cursor()
    sql = "SELECT * FROM planta WHERE id_planta = %s"
    cursor.execute(sql, (planta_id,)) 
    planta = cursor.fetchone()
    return planta


def actualizar_planta(
        nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
        calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
        f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
        tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
        institucion, nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
        permiso_descarga, fecha_registro, tipo_descarga, volumen_descarga,
        planta_id
    ):
    cursor = get_db().cursor()
    sql = """
        UPDATE planta
        SET nombre_ptar = %s,estado_id = %s,municipio_id = %s,coord_latitud = %s,coord_longitud = %s,calle = %s,numero = %s,colonia = %s,cp = %s,superficie = %s,
            caudal_entrada = %s,influente_industrial = %s,fecha_inicio_const = %s,fecha_fin_const = %s,fecha_inicio_oper = %s,
            poblacion_beneficiada = %s,anio_actual = %s,tipo_tratamiento = %s,gasto_diseño = %s, gasto_operacion_estiaje = %s,
            gasto_operacion_lluvia = %s,ro_nombre_institucion = %s,ro_nombre = %s,
            ro_puesto = %s,ro_correo = %s, ro_telefono = %s,permiso_descarga = %s,fecha_registro_permiso = %s,tipo_descarga = %s, volumen_descarga = %s
        WHERE id_planta = %s
    """

    cursor.execute(sql, (
        nombre_oficial, estado, municipio, coordenada_latitud, coordenada_longitud,
        calle, numero, colonia, codigo_postal, superficie, caudal_entrada, influente_industrial,
        f_construccion, f_finalizacion, f_i_operacion, p_beneficiada, a_actualizacion,
        tipo_tratamiento, gasto_diseño, gasto_estiaje, gasto_lluvia,
        institucion, nombre_responsabel, cargo_responsable, email_responsable, telefono_responsable,
        permiso_descarga, fecha_registro, tipo_descarga, volumen_descarga,
        planta_id
    ))

    get_db().commit()
    return

def estado_p_planta(estado_id):
    cursor = get_db().cursor()
    cursor.execute('SELECT id_municipio, nombre FROM municipio WHERE estado_id = ?', (estado_id,))
    municipios = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return jsonify(municipios)

def existing_planta(planta_id):
    cursor = get_db().cursor()
    sql = "SELECT id_planta FROM planta WHERE id_planta = ?"
    cursor.execute(sql, (planta_id,))
    existing_planta = cursor.fetchone()
    return existing_planta

def eliminar_planta(planta_id):
    cursor = get_db().cursor()
    sql = "SELECT id_planta FROM planta WHERE id_planta = ?"
    cursor.execute(sql, (planta_id,))
    existing_planta = cursor.fetchone()

    if existing_planta:
        sql_delete = "DELETE FROM planta WHERE id_planta = ?"
        cursor.execute(sql_delete, (planta_id,))
        get_db().commit()
    return

### CONSULTA PLANTAS #################################

def get_sql_planta(idPlanta):
    sql='SELECT id_planta, nombre_ptar, e.nombre as estado, m.nombre as municipio,colonia, calle, numero, cp, '\
                    'coord_latitud, coord_longitud, superficie,caudal_entrada, influente_industrial, '\
                    'fecha_inicio_const,fecha_fin_const, fecha_inicio_oper, poblacion_beneficiada,anio_actual, '\
                    'tipo_tratamiento, gasto_diseño, gasto_operacion_estiaje,gasto_operacion_lluvia, ro_nombre_institucion, '\
                    'ro_nombre, ro_puesto,ro_correo, ro_telefono '\
                    'FROM planta p '\
                    'LEFT JOIN estado e on e.id_estado=p.estado_id '\
                    'LEFT JOIN municipio m on m.id_municipio=p.municipio_id'
    if (idPlanta!=None):
        sql=sql+' WHERE p.id_planta='+idPlanta
    return sql    


def get_desc_plantas(idPlanta=None):
    cursor=get_db().cursor()
    cursor.execute(get_sql_planta(idPlanta))
    plantas=cursor.fetchall()
    planta_col_names=[i[0] for i in cursor.description]
    print(planta_col_names)
    #Ojo: las etiquetas de las plantas estan en las tabla
    cursor.execute("SELECT campo,etiqueta,seccion FROM etiqueta where tabla='planta' order by orden")
    # únicamente se carga la info de las etiquetas que estén en los campos  
    etiquetas = [row for row in cursor.fetchall() if row[0] in planta_col_names]
    # si las etiquetas regresan en formato de json objects
    #etiquetas=[dict((cursor.description[i][0], value) \
    #           for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(etiquetas) 
    # únicamente se carga la info de las etiquetas que estén en los campos  
    #etiquetas=[reg for reg in etiq if reg[0] in planta_col_names]
    #print(etiquetas) 
    #etiquetas=[dictEtiq[key] for key in planta_col_names if key in dictEtiq]
    return plantas,etiquetas


def get_datos_plantas(idPlantas, campos=""):
    cursor=get_db().cursor()
    if (campos!=""):
        campos=','+campos
    sql=" SELECT id_planta, nombre_ptar"+campos+" from planta where id_planta in ({}) """.format(idPlantas)
    cursor.execute(sql)
    resparams=[dict((cursor.description[i][0], value) \
            for i, value in enumerate(row)) for row in cursor.fetchall()]
    salida=jsonify(resparams)
    return salida

def get_campos_etiq_tabla(tabla='planta', soloConsulta=False):
    sql="SELECT campo,etiqueta,seccion FROM etiqueta "
    sqlWhere=''
    if (tabla!=None):
        sqlWhere=" tabla='planta' "
    if (soloConsulta):
        if (sqlWhere!=''):
            sqlWhere=sqlWhere+" and "
        sqlWhere=sqlWhere+" consulta=1 "
    if (sqlWhere!=''):
        sql=sql+' WHERE '+sqlWhere
    sql=sql+' order by orden '
    cursor=get_db().cursor()
    cursor.execute(sql)
    #etiquetas=[dict((cursor.description[i][0], value) \
    #           for i, value in enumerate(row)) for row in cursor.fetchall()]
    #return jsonify(etiquetas)
    return cursor.fetchall()


def get_desc_planta_json(idPlanta):
    cursor=get_db().cursor()
    cursor.execute(get_sql_planta(idPlanta))
    plantas=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    return jsonify(plantas)

    
def get_docs_plantas():
    cursor=get_db().cursor()
    cursor.execute('SELECT p.id_planta, p.nombre_ptar, p.doc_diagnostico, '\
                   'pd.pag_indice, pd.pag_informacion, pd.pag_desc, pd.pag_memoria, '\
                   'pd.pag_diag_personal, pd.pag_seguridad, pd.pag_laboratorio, pd.pag_info_hist, pd.pag_trab_campo, '\
                   'pd.pag_desempenio, pd.pag_anexos '\
                   'FROM planta p LEFT JOIN pag_diagnostico pd on pd.planta_id=p.id_planta ')
                   #'WHERE p.doc_diagnostico<>null')
    return cursor.fetchall()

def get_nombres_plantas(filtro='',campos_adic=''):
    cursor=get_db().cursor()
    if (campos_adic !=''):
        campos_adic= ',' + campos_adic
    sqlScr='SELECT id_planta, nombre_ptar'+campos_adic+' FROM planta'
    if filtro!='':
        sqlScr+=' where id_planta in ('+filtro+')'
    cursor.execute(sqlScr)
    return cursor.fetchall()    


def get_personal(idPlanta):
    cursor=get_db().cursor()
    cursor.execute('SELECT id_personal, nombre, puesto, tipo, escolaridad, DATE_FORMAT(fecha_ingreso,"%d/%m/%y") as fecha_ingreso, ant_planta, DATE_FORMAT(fecha_puesto,"%d/%m/%y") as  fecha_puesto, ant_puesto '\
                    ' FROM personal where planta_id ='+idPlanta)
    personal=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(personal)
    print(salida)
    return salida

def get_info_planta(idPlanta):
    cursor=get_db().cursor()
    sqlScr=("SELECT tipo_documento_id FROM info_planta WHERE planta_id="+idPlanta)
    cursor.execute(sqlScr)
    rowsTipoDoc=cursor.fetchall()
    print(rowsTipoDoc)
    if rowsTipoDoc!=[]:
        listaIdsTipoDoc=[str(reg[0]) for reg in rowsTipoDoc]
        strIdsTD=','.join(listaIdsTipoDoc)
        sqlScr="INSERT INTO info_planta(planta_id, tipo_documento_id) (SELECT "+idPlanta+",id_tipo_documento FROM tipo_documento "\
           "WHERE id_tipo_documento not in ("+strIdsTD+"))"
    else:
        sqlScr="INSERT INTO info_planta(planta_id, tipo_documento_id) (SELECT "+idPlanta+",id_tipo_documento FROM tipo_documento )"
    cursor.execute(sqlScr)
    g.db.commit()
    sqlScr='SELECT ip.planta_id, ip.tipo_documento_id, td.tipo_documento as documento,ip.entregado,ip.cant_arch_digitales, '\
           'ip.tam_arch_digitales,ip.tam_fisico, DATE_FORMAT(ip.fecha_recepcion,"%d/%m/%y") as fecha_recepcion, ip.observaciones FROM info_planta ip LEFT JOIN tipo_documento td'\
            ' ON td.id_tipo_documento=tipo_documento_id '\
            ' WHERE planta_id='+idPlanta    
    cursor.execute(sqlScr)
    salida = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    salida=jsonify(salida)
    print (salida)
    return salida

def identifica_usuario(usuario):
    try: 
        cursor=get_db().cursor()
        sql= """SELECT id_usuario,nombre_usuario,clave,rol_id,nombre,apellido_paterno,apellido_materno,
                    telefono_movil,activo FROM usuario WHERE nombre_usuario='{}'  """.format(usuario.nombre_usuario)
        cursor.execute(sql)
        row=cursor.fetchone()
        if (row!=None):
            usuario=Usuario(row[0], row[1], Usuario.verifica_clave(row[2], usuario.clave), row[3],row[4],row[5],row[6],row[7],row[8])
            return usuario
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def busca_usuario_por_id(id):
    try: 
        cursor=get_db().cursor()
        sql= """SELECT id_usuario,nombre_usuario,rol_id,nombre,apellido_paterno,apellido_materno,
                    telefono_movil,activo FROM usuario WHERE id_usuario={} """.format(id)
        cursor.execute(sql)
        row=cursor.fetchone()
        if (row!=None):
            usuario=Usuario(row[0], row[1], None, row[2],row[3],row[4],row[5],row[6],row[7])
            return usuario
        else:
            return None
    except Exception as ex:
        raise Exception(ex)
    

################################################################
# funciones nuevas no presentes en la versión compartida a Alejandro

def get_params_planta(idPlanta):
    cursor=get_db().cursor()
    sql=""" SELECT sum(n1996_ph) as n1996_ph, sum(n1996_temp) as n1996_temp, sum(n1996_matflotante) as n1996_matflotante, sum(n1996_solsed) as n1996_solsed,
            sum(n1996_grasas_aceites) as n1996_grasas_aceites, sum(n1996_sst) as n1996_sst, sum(n1996_dbo5) as n1996_dbo5, sum(n1996_nt) as n1996_nt,
            sum(n1996_pt) as n1996_pt, sum(n1996_metales) as n1996_metales, sum(n1996_hh) as n1996_hh, sum(n1996_cf) as n1996_cf, sum(n1996_ssv)
            as n1996_ssv, sum(n1996_n_nh3) as n1996_n_nh3, sum(n1996_n_no2) as n1996_n_no2, sum(n1996_n_no3) as n1996_n_no3, sum(n1996_p_po4) as
            n1996_p_po4, sum(p2017_dqo) as p2017_dqo, sum(p2017_tox_aguda) as p2017_tox_aguda, sum(p2017_color_verdadero) as p2017_color_verdadero,
            sum(p2017_esche_coli) as p2017_esche_coli, sum(p2017_disenio_ssv) as p2017_disenio_ssv, sum(p2017_cloro_residual) as p2017_cloro_residual,
            sum(p2017_cianuros) as p2017_cianuros, sum(p2017_nitratos) as p2017_nitratos, sum(p2017_nitrogeno_amoniacal) as
            p2017_nitrogeno_amoniacal, sum(p2017_ntk) as p2017_ntk, sum(p2017_n_organico) as p2017_n_organico, sum(n2021_dqo) as
            n2021_dqo, sum(n2021_tox_aguda) as n2021_tox_aguda, sum(n2021_color_verdadero) as n2021_color_verdadero,
            sum(n2021_esche_coli) as n2021_esche_coli, sum(n2021_ssv) as n2021_ssv, sum(n2021_cloro_residual) as n2021_cloro_residual,
            sum(n2021_cianuros) as n2021_cianuros, sum(n2021_nitratos) as n2021_nitratos, sum(n2021_nitrogeno_amoniacal) as
            n2021_nitrogeno_amoniacal, sum(n2021_ntk) as n2021_ntk, sum(n2021_n_organico) as n2021_n_organico, sum(n2021_cot) as
            n2021_cot, sum(otros_ntk) as otros_ntk, sum(otros_nh3) as otros_nh3, sum(otros_n_organico) as otros_n_organico, sum(otros_dbos_dqos) as
            otros_dbos_dqos, sum(otros_clorofila) as otros_clorofila, sum(otros_dqo_sol) as otros_dqo_sol, sum(otros_ssv) as otros_ssv,
            sum(otros_enterococos_fecales) as otros_enterococos_fecales from param_planta
            where planta_id = {} """.format(idPlanta)
    cursor.execute(sql)
    nomColumnas = [fields[0] for fields in cursor.description]
    camposStr=""
    for row in cursor.fetchall():
        for i, value in enumerate(row):
            if (value>0):
                camposStr+=nomColumnas[i]+", "
    if (camposStr!=""):
        camposStr=camposStr[:-2]
        print(camposStr)
        sql="SELECT id_param_planta,punto,descripcion,num_muestra,"+camposStr+",tipo_muestreo FROM param_planta where planta_id = {} """.format(idPlanta)
        cursor.execute(sql)
        resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        #print(personal)
        salida=jsonify(resparams)
        #print(salida)
        return salida
    return []

def fieldsWithNotNullValues(cursor):
    nomColumnas = [fields[0] for fields in cursor.description]
    colsNotNull = [0]*len(nomColumnas)
    camposStr=""
    for row in cursor.fetchall():
        for i, value in enumerate(row):
            if (not (value is None)):
                colsNotNull[i]=colsNotNull[i]+1;
    for i,value in enumerate(colsNotNull):
        if (value!=0):
            camposStr+=nomColumnas[i]+", "
    if (camposStr!=""):
        camposStr=camposStr[:-2]
    return camposStr

def get_resmuestra_compuesta(idPlantas, params=None, tipo=None, filtraCamposNotNull=True, muestraPlantas=False):
    if (params==None):
        params="ph,temp,grasas_aceites,matflotante,solsed,sst,dbo5,nt,pt,hh,dqo,color_a436,color_a525,color_a620,color_alph,arsenico, \
                cadmio,cobre,cromo,mercurio,niquel,plomo,zinc,cloro_residual,dqo_sol,ssv,cloruros_totales,cromo_hexavalente,ion_sulfato,n_nh3,ntk,sulfuros,cot, \
                esche_coli,cf,tox_aguda,enterococos_fecales"
    cursor=get_db().cursor()
    sql=" SELECT "+params+" from resmuestra_compuesta where planta_id in ({}) """.format(idPlantas)
    if (tipo!=None):
        sql=sql+" and tipo='"+tipo+"'"
    cursor.execute(sql)
    if (filtraCamposNotNull):
        camposStr=fieldsWithNotNullValues(cursor)
    else:
        camposStr=params
    if (camposStr!=""):
        #num_plantas=len(idPlantas.split(","))
        if (muestraPlantas):
            sql="SELECT p.nombre_ptar as ptar,muestreo,tipo,"+camposStr+" FROM resmuestra_compuesta, planta p where planta_id in ({}) and p.id_planta=planta_id """.format(idPlantas)
        else:
            sql="SELECT muestreo,tipo,"+camposStr+" FROM resmuestra_compuesta where planta_id in ({}) """.format(idPlantas)
        
        if (tipo!=None):
            sql=sql+" and tipo='"+tipo+"'"
        # se agrega la consulta para revisar las normas que aplican
        sql=sql+" UNION ALL ( SELECT "
        if (muestraPlantas): 
            sql=sql+" '', "
        sql=sql+"  1000+np.id_norma_param as muestreo, np.norma as tipo,"+camposStr+" from norma_param np "
        sql=sql+" WHERE np.id_norma_param in (select distinct norma_param_id from norma_param_planta where planta_id in ("+idPlantas+")))"
        print(sql)
        cursor.execute(sql)
        resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        #print(personal)
        salida=jsonify(resparams)
        #print(salida)
        return salida
    return []

def get_muestreos_tipos_planta(tabla, idPlanta):
    cursor=get_db().cursor()
    sql="SELECT distinct muestreo, tipo from "+tabla+" WHERE planta_id="+idPlanta+" order by muestreo"
    cursor.execute(sql)
    resparams=[dict((cursor.description[i][0], value) \
                    for i, value in enumerate(row)) for row in cursor.fetchall()]
    salida=jsonify(resparams)
    return salida

def get_resmuestra_caudal(idPlanta, muestreo, tipo):
    cursor=get_db().cursor()
    sql=""" SELECT caudal, ph, temp, matflotante, grasas_aceites, cf, 
            esche_coli, enterococos_fecales from resmuestra_caudal where planta_id = {} and muestreo = {} and tipo='{}' 
            order by muestra """.format(idPlanta, muestreo, tipo)
    cursor.execute(sql)
    camposStr=fieldsWithNotNullValues(cursor)
    if (camposStr!=""):
        sql=" SELECT muestra,"+camposStr+" from resmuestra_caudal where planta_id = {} and muestreo = {} and tipo='{}' order by muestra """.format(idPlanta, muestreo, tipo)
        cursor.execute(sql)
        resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        salida=jsonify(resparams)
        return salida
    return []

def get_resmuestra_tox(idPlanta, muestreo, tipo):
    cursor=get_db().cursor()
    sql=""" SELECT CE50_5, CE50_15, CE50_30, UT_5, UT_15, UT_30 from resmuestra_tox 
            where planta_id = {} and muestreo = {} and tipo='{}' 
            order by muestra """.format(idPlanta, muestreo, tipo)
    cursor.execute(sql)
    camposStr=fieldsWithNotNullValues(cursor)
    if (camposStr!=""):
        sql=" SELECT muestra,"+camposStr+" from resmuestra_tox where planta_id = {} and muestreo = {} and tipo='{}' order by muestra """.format(idPlanta, muestreo, tipo)
        cursor.execute(sql)
        resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        salida=jsonify(resparams)
        return salida
    return []

def get_datosgraf_resmuestra_caudal(idPlanta, muestreo):
    cursor=get_db().cursor()
    cmdSQL='select a.muestra,a.caudal as caudal_influente,b.caudal as caudal_efluente, '\
                    ' a.ph as ph_influente, b.ph as ph_efluente, '\
                    ' a.temp as temp_influente, b.temp as temp_efluente '\
                    ' from resmuestra_caudal a, resmuestra_caudal b '\
                    ' where b.planta_id=a.planta_id and b.muestra=a.muestra '\
                    ' and a.tipo="Influente" and b.tipo="Efluente" and a.muestreo=b.muestreo and '\
                    ' a.muestreo='+muestreo+' and a.planta_id = '+idPlanta
    cursor.execute(cmdSQL)
    print(cmdSQL)
    resmuestras=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(resmuestras)
    #print(salida)
    return salida


def get_resmuestra_simple(idPlanta):
    cursor=get_db().cursor()
    sql=""" SELECT muestreo,muestra,temp,pH,matflotante,solsed,grasas_aceites,sst,dbo5,nt,pt,hh,cf,dqo,clorofila,esche_coli,ntk,n_namoniacal,
            norg,ssv,dbos,dqos,n_nh3,n_norg,n_no3,arsenico,cadmio,cobre,cromo,mercurio,niquel,plomo,zinc,color_a436,
            color_a525,color_a620,color_alph,ce50_5,ce50_15,ce50_30,ut_5,ut_15,ut_30,cot,cloruros_totales,
            cromo_hexavalente,ion_sulfato,sulfuros,p_po4_3,n_no2,ce,enterococos_fecales
            from resmuestra_simple where planta_id = {} """.format(idPlanta)
    cursor.execute(sql)
    camposStr=fieldsWithNotNullValues(cursor)
    if (camposStr!=""):
        sql="SELECT muestreo,muestra,"+camposStr+" FROM resmuestra_simple where planta_id = {} """.format(idPlanta)
        cursor.execute(sql)
        resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
        #print(personal)
        salida=jsonify(resparams)
        #print(salida)
        return salida
    return []

def get_limitantes(idPlanta, nivel, plazo):
    cursor=get_db().cursor()
    sql= "SELECT nivel, numero, causa, plazo, explicacion, recomendacion from limitante WHERE planta_id = "+idPlanta
    if (nivel!="*"):
        sql=sql+" and nivel='"+nivel+"'"
    if (plazo!="*"):
        sql=sql+" and plazo='"+plazo+" plazo'"  # la palabra "plazo" no viene en el parámetro
    sql= sql+" order by nivel, numero "
    cursor.execute(sql)
    resparams=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    salida=jsonify(resparams)
    return salida

def get_capitulos_plantas():
    cursor=get_db().cursor()
    cursor.execute('SELECT pcd.planta_id, pcd.capitulodiag_id, cd.capitulo,  pcd.pagina_abs '\
                    'FROM planta_capitulodiag pcd LEFT JOIN capitulodiag cd on cd.id_capitulodiag=pcd.capitulodiag_id '\
                    'ORDER BY pcd.planta_id, pcd.orden_capitulo ')
                   #'WHERE p.doc_diagnostico<>null')
    return cursor.fetchall()


