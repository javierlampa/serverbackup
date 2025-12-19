import re

def parse_robocopy_log(content):
    """Parsea el contenido del log de Robocopy para extraer stats y errores."""
    stats = {"total": 0, "copied": 0, "skipped": 0, "failed": 0, "start": "-", "end": "-", "errors": [], "recent_activity": []}
    
    if not content:
        return stats

    # Buscar ultimo bloque
    bloques = content.split("--- INICIO BACKUP")
    
    if len(bloques) > 1:
        # Caso ideal: Encontramos el inicio
        last_block = bloques[-1]
        start_match = last_block.split("---")[0].strip()
        stats['start'] = start_match if start_match else "-"
    else:
        # Caso log truncado o sin header visible en el buffer
        last_block = content
        stats['start'] = "En curso (Inicio fuera de buffer)"

    # Determinar estado
    end_match = re.search(r'--- FIN BACKUP (.*) ---', last_block)
    if end_match: 
        stats['end'] = end_match.group(1).strip()
        stats['status'] = 'FINISHED'
        # Si ya termino y el inicio estaba fuera de buffer, mejor mostrar que fue antes del fin
        if stats['start'] == "En curso (Inicio fuera de buffer)":
            stats['start'] = "Anterior a " + stats['end'].split()[0]
    else:
        stats['end'] = "En Progreso..."
        stats['status'] = 'RUNNING'
    
    # Si detectamos que ya termino por la tabla de estadisticas pero no vimos el header de FIN
    if stats['status'] == 'RUNNING' and ("Velocidad :" in last_block or "Speed :" in last_block):
        stats['status'] = 'FINISHED'
        stats['end'] = "Finalizado (ver log)"
    
    # Errores generales (red, disco)
    for line in last_block.splitlines():
        # Filtramos la palabra ERROR pero evitando la cabecera de la tabla de Robocopy
        if ("ERROR" in line or "Error" in line or "Fallo" in line or "CRITICO" in line):
            # Excluimos la linea que es claramente una cabecera de tabla
            if "Total" in line and "Copiado" in line and "Omitido" in line:
                continue
            if "---" not in line and "ROBOCOPY" not in line:
                clean_err = line.strip()
                if clean_err and clean_err not in stats['errors']: 
                    stats['errors'].append(clean_err)

    # Stats Robocopy (Tabla Files / Archivos)
    files_lines = re.findall(r'(?:Files|Archivos)\s*:\s*([\d\s\n\r]+)', last_block, re.IGNORECASE)
    for fl in files_lines:
        # Limpiar saltos de linea para capturar numeros que hayan bajado de renglon
        clean_fl = fl.replace("\n", " ").replace("\r", " ")
        parts = []
        for x in clean_fl.split():
            try: 
                parts.append(int(x))
                if len(parts) >= 6: break # Solo nos interesan las primeras 6 columnas
            except: pass
            
        if len(parts) >= 5:
            stats['total'] += parts[0]
            stats['copied'] += parts[1]
            stats['skipped'] += parts[2]
            stats['failed'] += parts[4]

    # Extraer ultimas lineas de actividad
    raw_lines = last_block.splitlines()
    activity_lines = []
    for line in reversed(raw_lines):
        if len(activity_lines) >= 15: break
        clean = line.strip()
        # Filtar lineas vacias
        if not clean: continue
        
        # Filtrar encabezados y pies de pagina conocidos de Robocopy (EN/ES)
        if "---" in clean or "Files :" in clean or "Archivos :" in clean or "Bytes :" in clean or \
           "Times :" in clean or "Tiempos :" in clean or "Speed :" in clean or "Velocidad :" in clean or \
           "Ended :" in clean or "Finalizado :" in clean or "Director." in clean:
            continue
            
        # Filtrar lineas muy cortas (ruido)
        if len(clean) < 10: continue

        activity_lines.insert(0, clean)
    
    stats['recent_activity'] = activity_lines

    return stats
