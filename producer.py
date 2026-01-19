import pika
import json
from datetime import datetime

# Données factices (simule ce que l'utilisateur envoie à l'API)
fake_music = {
    "title": "Daft Punk - One More Time",
    "artist": "Daft Punk",
    "duration": 320,
    "genre": "Techno",
    "created_at": datetime.now().isoformat() # Important: convertir la date en texte
}

def send_message():
    # 1. Connexion à RabbitMQ (localhost car on est en dehors de Docker pour le test)
    # Les identifiants sont ceux de ton docker-compose (admin/admin)
    credentials = pika.PlainCredentials('admin', 'admin')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5671, credentials=credentials)
    )
    channel = connection.channel()

    # 2. Déclaration de la file (La fameuse "Boîte aux lettres")
    queue_name = 'music_indexing_queue'
    channel.queue_declare(queue=queue_name, durable=True) 
    # durable=True : la file survit si RabbitMQ redémarre

    # 3. Envoi du message
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(fake_music), # On transforme le dictionnaire en texte JSON
        properties=pika.BasicProperties(
            delivery_mode=2,  # Rend le message persistant (il survit au reboot)
        )
    )
    
    print(f" [x] Envoyé : '{fake_music['title']}' dans RabbitMQ")
    connection.close()

if __name__ == "__main__":
    send_message()