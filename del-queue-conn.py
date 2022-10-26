#!/usr/bin/env python3

import subprocess
import requests
import datetime
import time

def _notify(text):
    msg = {'text': text}
    print(f"[{datetime.datetime.now().isoformat()}] {text}")
    requests.post('slackurl', json=msg)


def delete_rabbitmq(ns):
    #obtengo los nombres de los pods de RabbitMQ segun el namespace
    rabbit_get_pods = subprocess.check_output(['kubectl get pods -n 'f"{ns}"' -o=name | grep rabbitmq'], text=True, shell=True)
    rabbit_pods = rabbit_get_pods.split('\n')
    
    #obtengo cantidad de conexiones abiertas en RabbitMQ       
    rabbit_conn = subprocess.check_output(['kubectl exec -ti -n 'f"{ns}"' 'f"{rabbit_pods[0]}"' -- bash -c "rabbitmqctl list_connections | wc -l"'], text=True, shell=True)
    
    #elimino los pods de rabbit si la cantidad de conexiones es mayor a 13000
    flag = FLAGS[ns]
    if int(rabbit_conn) > 13000:
        for pod in rabbit_pods:
            _notify(f"Se eliminaran las conexiones abiertas en {flag}, debido a que actualmente son {int(rabbit_conn)}.")
            subprocess.run(["/usr/local/bin/kubectl", "delete", "-n", f"{ns}", f"{pod}"])
            _notify(f"Conexiones eliminadas :white_check_mark:")
    else:
         _notify(f"La cantidad de conexiones abiertas actualmente en {flag}, son {int(rabbit_conn)}.")


namespaces = ('app','br','mx')

FLAGS = {
    'app': ':flag-ar:',
    'br': ':flag-br:',
    'mx': ':flag-mx:'
}

while True: 
    now = datetime.datetime.now()
    run_script = now.replace(hour=10, minute=36)
    end_script = now.replace(hour=10, minute=36, second=1)
    
    if run_script <= now <= end_script:
        for ns in namespaces:
            delete_rabbitmq(ns)
        now = datetime.datetime.now()    
    else:
        time.sleep(0.2)
