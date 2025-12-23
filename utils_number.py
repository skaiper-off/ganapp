def parse_input_number(s, field_name="número"):
    """Parsea números que pueden usar separadores de miles o diferentes separadores decimales.
    Devuelve float o lanza ValueError si no es válido."""
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    # Remover símbolos de moneda y espacios
    s = s.replace('$', '').replace('MXN', '').replace('mxn', '').replace(' ', '')

    # Si tiene ambos separadores, asumir que el último es el decimal
    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '')
            s = s.replace(',', '.')
        else:
            s = s.replace(',', '')
    else:
        if ',' in s and '.' not in s:
            if s.count(',') == 1 and len(s.split(',')[-1]) <= 2:
                s = s.replace(',', '.')
            else:
                s = s.replace(',', '')
        elif '.' in s and ',' not in s:
            if s.count('.') > 1:
                s = s.replace('.', '')
            else:
                # Si hay 3 dígitos después del punto, probablemente sea separador de miles
                if len(s.split('.')[-1]) == 3:
                    s = s.replace('.', '')
    try:
        return float(s)
    except Exception:
        raise ValueError(f"El valor ingresado para {field_name} no es un número válido: {s}")
