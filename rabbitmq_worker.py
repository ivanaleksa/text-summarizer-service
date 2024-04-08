import pika
import json
from nn_model import Model as SummarizeModel

def callback(ch, method, properties, body):
    parameters = json.loads(body)

    model = SummarizeModel()

    predict_result = model.make_prediction(parameters["input_text"], min_len=10, max_len=1000)[0]["summary_text"]

    response_queue = properties.reply_to
    response_message = json.dumps({"result": predict_result, "user_id": parameters["user_id"], "input_text": parameters["input_text"]})
    ch.basic_publish(exchange='', routing_key=response_queue, body=response_message)

    ch.basic_ack(delivery_tag=method.delivery_tag)

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

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

queue_name = 'prediction_queue'
channel.queue_declare(queue=queue_name)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
