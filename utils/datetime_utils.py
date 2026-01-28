# utils/datetime_utils.py

from datetime import datetime, timezone, timedelta

# Zona horaria de Campeche (CST - Central Standard Time)
CST = timezone(timedelta(hours=-6))

def get_local_now():
    """
    Retorna el datetime actual en zona horaria de Campeche (CST)
    """
    return datetime.now(CST)

def get_local_now_naive():
    """
    Retorna el datetime actual en zona horaria de Campeche pero como naive datetime
    (sin información de zona horaria para comparaciones con fechas de BD)
    """
    local_time = datetime.now(CST)
    return local_time.replace(tzinfo=None)

def format_datetime_local(dt, format_str='%d/%m/%Y %H:%M'):
    """
    Formatea un datetime en zona horaria local de Campeche
    """
    if dt.tzinfo is None:
        # Si no tiene zona horaria, asumimos que es CST
        dt = dt.replace(tzinfo=CST)
    else:
        # Convertir a CST si tiene otra zona horaria
        dt = dt.astimezone(CST)
    
    return dt.strftime(format_str)

def format_date_local(dt, format_str='%d/%m/%Y'):
    """
    Formatea solo la fecha en zona horaria local de Campeche
    """
    return format_datetime_local(dt, format_str)

def format_time_local(dt, format_str='%H:%M'):
    """
    Formatea solo la hora en zona horaria local de Campeche
    """
    return format_datetime_local(dt, format_str)