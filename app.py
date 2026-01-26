from flask import Flask, render_template, redirect, url_for
from flask_mail import Mail
import os

# Importar configuración centralizada
from config import config

# Importar blueprints
from routes.login import login_bp
from routes.dashboard import dashboard_bp
from routes.clientes import clientes_bp
from routes.inventario import bp_inventario
from routes.producto import bp_producto
from routes.empleados import empleados_bp
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.rentas import rentas_bp
from routes.salidas_internas import salidas_internas_bp
from routes.notas_entrada import notas_entrada_bp
from routes.notas_salida import notas_salida_bp
from routes.prefactura import prefactura_bp
from routes.cobros_extra import bp_extras
from routes.cobro_retraso import cobro_retraso_bp
from routes.caja import caja_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    mail = Mail(app)
    
    # Filtros de plantillas
    @app.template_filter('estado_color')
    def estado_color(estado):
        colores = {
            'activa': 'success',
            'programada': 'primary',
            'finalizada': 'secondary',
            'cancelada': 'danger',
            'renovada': 'info',
            'parcialmente devuelta': 'warning'
        }
        return colores.get(estado, 'dark')
    
    # Registrar blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(bp_inventario)
    app.register_blueprint(bp_producto)
    app.register_blueprint(empleados_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(cotizaciones_bp)
    app.register_blueprint(rentas_bp)
    app.register_blueprint(salidas_internas_bp)
    app.register_blueprint(notas_entrada_bp)
    app.register_blueprint(notas_salida_bp)
    app.register_blueprint(prefactura_bp)
    app.register_blueprint(bp_extras)
    app.register_blueprint(cobro_retraso_bp)
    app.register_blueprint(caja_bp)
    
    # Ruta principal
    @app.route('/')
    def home():
        return redirect(url_for('login.login'))
    
    return app

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])