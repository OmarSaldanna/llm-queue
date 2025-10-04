import time
from modules import get_db_connection, get_llm_response, count_tokens, Colors

def process_single_prompt():
    """
    Toma un prompt de la cola, lo procesa con el LLM y actualiza la base de datos.
    """
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    try:
        # 1. Seleccionar el prompt más antiguo y pendiente
        cursor.execute("""
            SELECT id, prompt 
            FROM fila_llm_anahuac 
            WHERE estatus = 'pendiente' 
            ORDER BY fecha_in ASC 
            LIMIT 1 FOR UPDATE SKIP LOCKED;
        """)
        job = cursor.fetchone()

        if not job:
            print(f"{Colors.CYAN}No hay prompts pendientes en la cola.{Colors.END}")
            # Crear archivo de control para detener el script de shell
            with open("empty_queue.tmp", "w") as f:
                f.write("empty")
            return

        job_id, prompt_text = job
        print(f"\n{Colors.BLUE}Procesando Job ID: {job_id}{Colors.END}")
        
        # 2. Procesar con el LLM y medir el tiempo
        start_time = time.time()
        respuesta = get_llm_response(prompt_text)
        end_time = time.time()
        
        tiempo_ejecucion = round(end_time - start_time, 2)
        
        if respuesta:
            # 3. Contar tokens y preparar datos para la actualización
            tokens_in = count_tokens(prompt_text)
            tokens_out = count_tokens(respuesta)
            
            print(f"{Colors.GREEN}Respuesta recibida. Tiempo: {tiempo_ejecucion}s, Tokens in/out: {tokens_in}/{tokens_out}{Colors.END}")
            
            # 4. Actualizar el registro en la DB a 'listo'
            cursor.execute("""
                UPDATE fila_llm_anahuac
                SET respuesta = %s, fecha_out = NOW(), tokens_in = %s, tokens_out = %s, 
                    estatus = 'listo', tiempo_ejecucion = %s
                WHERE id = %s;
            """, (respuesta, tokens_in, tokens_out, tiempo_ejecucion, job_id))
        
        else:
            # 5. Si hubo un error, actualizar el registro a 'error'
            print(f"{Colors.RED}Fallo al procesar Job ID: {job_id}. Marcando como error.{Colors.END}")
            cursor.execute("""
                UPDATE fila_llm_anahuac
                SET estatus = 'error', respuesta = 'Fallo en la comunicación con el LLM.', fecha_out = NOW()
                WHERE id = %s;
            """, (job_id,))
            
        # Confirmar la transacción
        conn.commit()

    except Exception as e:
        print(f"{Colors.RED}Ocurrió un error inesperado: {e}{Colors.END}")
        if conn:
            conn.rollback() # Revertir cambios en caso de error
    
    finally:
        # Cerrar la conexión
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    process_single_prompt()