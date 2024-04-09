import pika
import json

def send_message(input_text: str, user_id):
    connection_params = pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='/',
        credentials=pika.PlainCredentials(
            username='user', 
            password='123'
        ),
        heartbeat=30,
        blocked_connection_timeout=2
    )

    params = {
        "input_text": input_text,
        "user_id": user_id
    }
    message_body = json.dumps(params)

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    queue_name = 'prediction_queue'
    result_queue_name = 'result_queue'
    channel.queue_declare(queue=queue_name)
    channel.queue_declare(queue=result_queue_name)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message_body,
        properties=pika.BasicProperties(reply_to=result_queue_name)
    )

    connection.close()
