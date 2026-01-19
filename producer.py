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
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
    )
    queu_name = "music_data"
    channel = connection.channel()
    channel.queue_declare(queue=queu_name)
    channel.basic_publish(exchange='',
                          routing_key=queu_name,
                          body=json.dumps(fake_music)
                          )
    connection.close()
    print(f"send {fake_music}")

    

if __name__ == "__main__":
    send_message()