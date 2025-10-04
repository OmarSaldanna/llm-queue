#!/bin/bash

# Ruta al activador del entorno virtual de Python
source /ruta/a/tu/proyecto/venv/bin/activate

# Navega al directorio del script para que los archivos .tmp se creen en el lugar correcto
cd /ruta/a/tu/proyecto/

echo "Iniciando proceso de la cola de prompts..."

# Bucle principal: se ejecuta mientras no exista 'empty_queue.tmp' y la hora sea antes de las 06:00
while [ ! -f empty_queue.tmp ] && [ $(date +%H) -lt 6 ]; do
    python3 job.py
    # Pequeña pausa para no saturar el sistema en caso de fallos rápidos
    sleep 2 
done

# Mensaje de finalización
if [ -f empty_queue.tmp ]; then
    echo "Proceso detenido: la cola de prompts está vacía."
else
    echo "Proceso detenido: se alcanzaron las 6 AM."
fi

# Limpieza: elimina el archivo de control para la próxima ejecución
rm -f empty_queue.tmp

echo "Proceso de la cola finalizado."