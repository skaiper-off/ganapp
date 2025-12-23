from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from datetime import datetime
from utils_number import parse_input_number
import database
import matplotlib
matplotlib.use('Agg')  # Para generar gráficas sin interfaz gráfica
import matplotlib.pyplot as plt
from openpyxl import Workbook
import io
import base64

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala_en_produccion'  # Necesario para flash messages

# Inicializar base de datos
database.crear_tablas()

# ==================== PÁGINA PRINCIPAL ====================
@app.route('/')
def index():
    """Página principal con resumen"""
    conn = database.conectar()
    cursor = conn.cursor()
    
    # Obtener estadísticas rápidas
    cursor.execute("SELECT COUNT(*) FROM ganado")
    total_ganado = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ganado WHERE LOWER(estado) = 'vivo'")
    ganado_vivo = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos")
    total_eventos = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', 
                         total_ganado=total_ganado,
                         ganado_vivo=ganado_vivo,
                         total_eventos=total_eventos)

# ==================== GESTIÓN DE GANADO ====================
@app.route('/ganado')
def listar_ganado():
    """Muestra listado completo de ganado"""
    busqueda = request.args.get('buscar', '')
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    if busqueda:
        cursor.execute("""
            SELECT arete, nombre, sexo, fecha_nacimiento, estado, observaciones 
            FROM ganado 
            WHERE LOWER(arete) LIKE ? OR LOWER(nombre) LIKE ?
            ORDER BY arete
        """, (f'%{busqueda.lower()}%', f'%{busqueda.lower()}%'))
    else:
        cursor.execute("""
            SELECT arete, nombre, sexo, fecha_nacimiento, estado, observaciones 
            FROM ganado 
            ORDER BY arete
        """)
    
    ganado = cursor.fetchall()
    conn.close()
    
    return render_template('ganado.html', ganado=ganado, busqueda=busqueda)

@app.route('/ganado/registrar', methods=['GET', 'POST'])
def registrar_ganado():
    """Registra nuevo ganado"""
    if request.method == 'POST':
        arete = request.form.get('arete', '').strip()
        nombre = request.form.get('nombre', '').strip()
        sexo = request.form.get('sexo', 'Macho')
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        estado = request.form.get('estado', 'Vivo')
        observaciones = request.form.get('observaciones', '').strip()
        
        if not arete:
            flash('El número de arete es obligatorio', 'error')
            return redirect(url_for('registrar_ganado'))
        
        conn = database.conectar()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ganado (arete, nombre, sexo, fecha_nacimiento, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (arete, nombre, sexo, fecha, estado, observaciones))
            conn.commit()
            flash(f'Ganado {arete} registrado correctamente', 'success')
            return redirect(url_for('listar_ganado'))
        except Exception as e:
            flash(f'Error: Ese número de arete ya existe', 'error')
        finally:
            conn.close()
    
    return render_template('ganado.html')

@app.route('/ganado/eliminar', methods=['POST'])
def eliminar_ganado():
    """Elimina un ganado y sus eventos"""
    arete = request.form.get('arete', '').strip()
    if not arete:
        flash('No se especificó el arete a eliminar', 'error')
        return redirect(url_for('listar_ganado'))

    conn = database.conectar()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM ganado WHERE arete = ?", (arete,))
        cursor.execute("DELETE FROM eventos WHERE arete = ?", (arete,))
        conn.commit()
        flash(f'Ganado {arete} eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('listar_ganado'))

# ==================== EVENTOS ====================
@app.route('/eventos')
def eventos():
    """Página de registro de eventos"""
    conn = database.conectar()
    cursor = conn.cursor()
    
    # Obtener lista de aretes para el selector
    cursor.execute("SELECT arete, nombre FROM ganado ORDER BY arete")
    ganado = cursor.fetchall()
    conn.close()
    
    return render_template('eventos.html', ganado=ganado)

@app.route('/eventos/registrar', methods=['POST'])
def registrar_evento():
    """Registra un nuevo evento"""
    arete = request.form.get('arete')
    tipo = request.form.get('tipo', 'Otro')
    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    peso_str = request.form.get('peso', '').strip()
    costo_str = request.form.get('costo', '').strip()
    notas = request.form.get('notas', '').strip()
    
    peso = None
    costo = None
    
    try:
        if peso_str:
            peso = parse_input_number(peso_str, "peso")
    except ValueError as e:
        flash(f'Error en peso: {str(e)}', 'error')
        return redirect(url_for('eventos'))
    
    try:
        if costo_str:
            costo = parse_input_number(costo_str, "costo")
    except ValueError as e:
        flash(f'Error en costo: {str(e)}', 'error')
        return redirect(url_for('eventos'))
    
    if not arete:
        flash('Debes seleccionar un arete', 'error')
        return redirect(url_for('eventos'))
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO eventos (arete, tipo, fecha, peso, costo, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (arete, tipo, fecha, peso, costo, notas))
        conn.commit()
        flash('Evento registrado correctamente', 'success')
    except Exception as e:
        flash(f'Error al registrar evento: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('eventos'))

# ==================== NACIMIENTO ====================
@app.route('/nacimiento', methods=['GET', 'POST'])
def nacimiento():
    """Registro de nacimientos"""
    if request.method == 'GET':
        conn = database.conectar()
        cursor = conn.cursor()
        
        # Obtener machos y hembras para padres
        cursor.execute("SELECT arete, nombre FROM ganado WHERE LOWER(sexo) = 'macho' ORDER BY arete")
        machos = cursor.fetchall()
        
        cursor.execute("SELECT arete, nombre FROM ganado WHERE LOWER(sexo) = 'hembra' ORDER BY arete")
        hembras = cursor.fetchall()
        
        conn.close()
        
        return render_template('nacimiento.html', machos=machos, hembras=hembras)
    
    # POST - Registrar nacimiento
    arete_cria = request.form.get('arete_cria', '').strip()
    nombre_cria = request.form.get('nombre_cria', '').strip()
    sexo = request.form.get('sexo', 'Macho')
    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    padre = request.form.get('padre', '')
    madre = request.form.get('madre', '')
    descripcion = request.form.get('descripcion', '').strip()
    
    if not arete_cria:
        flash('El número de arete de la cría es obligatorio', 'error')
        return redirect(url_for('nacimiento'))
    
    if padre == 'No especificado':
        padre = None
    if madre == 'No especificado':
        madre = None
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    try:
        # Registrar la cría como nuevo ganado
        cursor.execute("""
            INSERT INTO ganado (arete, nombre, sexo, fecha_nacimiento, estado, observaciones)
            VALUES (?, ?, ?, ?, 'Vivo', ?)
        """, (arete_cria, nombre_cria, sexo, fecha, descripcion))
        
        # Registrar evento de nacimiento
        notas_evento = f"Padre: {padre or 'No especificado'}, Madre: {madre or 'No especificado'}"
        if descripcion:
            notas_evento += f". {descripcion}"
        
        cursor.execute("""
            INSERT INTO eventos (arete, tipo, fecha, peso, costo, notas)
            VALUES (?, 'Nacimiento', ?, NULL, NULL, ?)
        """, (arete_cria, fecha, notas_evento))
        
        conn.commit()
        flash(f'Nacimiento registrado correctamente - Cría: {arete_cria}', 'success')
        return redirect(url_for('listar_ganado'))
    except Exception as e:
        flash(f'Error al registrar nacimiento: {str(e)}', 'error')
        return redirect(url_for('nacimiento'))
    finally:
        conn.close()

# ==================== MUERTE ====================
@app.route('/muerte', methods=['GET', 'POST'])
def muerte():
    """Registro de muertes"""
    if request.method == 'GET':
        conn = database.conectar()
        cursor = conn.cursor()
        
        # Obtener solo ganado vivo
        cursor.execute("""
            SELECT arete, nombre FROM ganado 
            WHERE LOWER(estado) = 'vivo' 
            ORDER BY arete
        """)
        ganado_vivo = cursor.fetchall()
        conn.close()
        
        return render_template('muerte.html', ganado=ganado_vivo)
    
    # POST - Registrar muerte
    arete = request.form.get('arete')
    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    causa = request.form.get('causa', 'Desconocida')
    descripcion = request.form.get('descripcion', '').strip()
    
    if not arete:
        flash('Debes seleccionar un animal', 'error')
        return redirect(url_for('muerte'))
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    try:
        # Actualizar estado a Muerto
        cursor.execute("UPDATE ganado SET estado = 'Muerto' WHERE arete = ?", (arete,))
        
        # Registrar evento de muerte
        notas_evento = f"Causa: {causa}"
        if descripcion:
            notas_evento += f". {descripcion}"
        
        cursor.execute("""
            INSERT INTO eventos (arete, tipo, fecha, peso, costo, notas)
            VALUES (?, 'Muerte', ?, NULL, NULL, ?)
        """, (arete, fecha, notas_evento))
        
        conn.commit()
        flash(f'Muerte del ganado {arete} registrada correctamente', 'success')
        return redirect(url_for('listar_ganado'))
    except Exception as e:
        flash(f'Error al registrar muerte: {str(e)}', 'error')
        return redirect(url_for('muerte'))
    finally:
        conn.close()

# ==================== HISTORIAL ====================
@app.route('/historial')
def historial():
    """Muestra historial de eventos"""
    arete = request.args.get('arete', '')
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    if arete:
        cursor.execute("""
            SELECT tipo, fecha, peso, costo, notas, arete
            FROM eventos
            WHERE arete = ?
            ORDER BY fecha DESC
        """, (arete,))
    else:
        cursor.execute("""
            SELECT tipo, fecha, peso, costo, notas, arete
            FROM eventos
            ORDER BY fecha DESC
            LIMIT 100
        """)
    
    eventos = cursor.fetchall()
    
    # Obtener lista de aretes para el filtro
    cursor.execute("SELECT DISTINCT arete FROM ganado ORDER BY arete")
    aretes = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('historial.html', eventos=eventos, aretes=aretes, arete_seleccionado=arete)

# ==================== ESTADÍSTICAS ====================
@app.route('/estadisticas')
def estadisticas():
    """Muestra estadísticas generales"""
    conn = database.conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM ganado")
    total_ganado = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ganado WHERE LOWER(estado) = 'vivo'")
    vivos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ganado WHERE LOWER(estado) = 'muerto'")
    muertos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos")
    total_eventos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos WHERE LOWER(tipo) = 'pesaje'")
    total_pesajes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos WHERE LOWER(tipo) = 'nacimiento'")
    total_nacimientos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos WHERE LOWER(tipo) = 'muerte'")
    total_muertes = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT AVG(peso) FROM eventos
        WHERE LOWER(tipo) = 'pesaje' AND peso IS NOT NULL
    """)
    promedio_peso = cursor.fetchone()[0]
    
    conn.close()
    
    stats = {
        'total_ganado': total_ganado,
        'vivos': vivos,
        'muertos': muertos,
        'total_eventos': total_eventos,
        'total_pesajes': total_pesajes,
        'total_nacimientos': total_nacimientos,
        'total_muertes': total_muertes,
        'promedio_peso': f"{promedio_peso:.2f}" if promedio_peso else "N/A"
    }
    
    return render_template('estadisticas.html', stats=stats)

# ==================== ECONOMÍA ====================
@app.route('/economia')
def economia():
    """Muestra resumen económico"""
    conn = database.conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(costo) FROM eventos
        WHERE LOWER(tipo) = 'venta' AND costo IS NOT NULL
    """)
    ingresos = cursor.fetchone()[0] or 0
    
    cursor.execute("""
        SELECT SUM(costo) FROM eventos
        WHERE LOWER(tipo) IN ('compra', 'vacunación', 'vacuna', 'baño', 'aretado', 'desparasitación')
        AND costo IS NOT NULL
    """)
    egresos = cursor.fetchone()[0] or 0
    
    balance = ingresos - egresos
    conn.close()
    
    return render_template('economia.html', 
                         ingresos=ingresos, 
                         egresos=egresos, 
                         balance=balance)

# ==================== GRÁFICA DE PESO ====================
@app.route('/grafica_peso')
def grafica_peso():
    """Genera gráfica de evolución de peso"""
    arete = request.args.get('arete', '')
    
    conn = database.conectar()
    cursor = conn.cursor()
    
    # Obtener lista de aretes
    cursor.execute("SELECT DISTINCT arete FROM ganado ORDER BY arete")
    aretes = [row[0] for row in cursor.fetchall()]
    
    grafica_base64 = None
    
    if arete:
        cursor.execute("""
            SELECT fecha, peso
            FROM eventos
            WHERE arete = ? AND LOWER(tipo) = 'pesaje' AND peso IS NOT NULL
            ORDER BY fecha
        """, (arete,))
        datos = cursor.fetchall()
        
        if datos:
            fechas = [datetime.strptime(str(d[0]), '%Y-%m-%d') for d in datos]
            pesos = [float(d[1]) for d in datos]
            
            # Crear gráfica
            plt.figure(figsize=(10, 6))
            plt.plot(fechas, pesos, marker='o', linewidth=2.5, color='#3498DB', label='Peso')
            plt.scatter(fechas, pesos, s=80, color='#27AE60', edgecolors='#34495E', linewidths=1.5, zorder=5)
            plt.title(f'Evolución del Peso - Arete {arete}', fontsize=14, fontweight='bold')
            plt.xlabel('Fecha', fontsize=11, fontweight='bold')
            plt.ylabel('Peso (kg)', fontsize=11, fontweight='bold')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convertir a base64 para mostrar en HTML
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            grafica_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
    
    conn.close()
    
    return render_template('grafica_peso.html', 
                         aretes=aretes, 
                         arete_seleccionado=arete,
                         grafica=grafica_base64)

# ==================== EXPORTAR A EXCEL ====================
@app.route('/exportar/ganado')
def exportar_ganado_excel():
    """Exporta ganado a Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Ganado"
    
    ws.append(["Arete", "Nombre", "Sexo", "Fecha Nacimiento", "Estado", "Observaciones"])
    
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT arete, nombre, sexo, fecha_nacimiento, estado, observaciones 
        FROM ganado 
        ORDER BY arete
    """)
    
    for fila in cursor.fetchall():
        ws.append(fila)
    
    conn.close()
    
    # Guardar en memoria
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'ganado_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/exportar/eventos')
def exportar_eventos_excel():
    """Exporta eventos a Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Eventos"
    
    ws.append(["Arete", "Tipo", "Fecha", "Peso", "Costo", "Notas"])
    
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT arete, tipo, fecha, peso, costo, notas
        FROM eventos
        ORDER BY fecha DESC
    """)
    
    for fila in cursor.fetchall():
        ws.append(fila)
    
    conn.close()
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'eventos_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    