import pika


def main():
    # 1. Connexion à RabbitMQ (localhost car on est en dehors de Docker pour le test)
    # Les identifiants sont ceux de ton docker-compose (admin/admin)
    credentials = pika.PlainCredentials('admin', 'admin')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
    )
    queue_name = "music_data"
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    # 2. Fonction de rappel pour traiter les messages reçus
    def callback(ch, method, properties, body):
        print(f"Received {body}")

    # 3. Abonnement à la file d'attente
    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()