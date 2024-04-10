from kafka import KafkaProducer
import json

SERVER_HOST = os.getenv('SERVER_HOST', 'default_url')

# Kafka 프로듀서 인스턴스 생성
producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=[f'{SERVER_HOST}:19094'],
                         value_serializer=lambda x:json.dumps(x).encode('utf-8'),
                          api_version=(2,)
                         )

# 보낼 메시지 정의
test_message = {
    'symbol': 'TEST',
    'price': 100,
    'timestamp': '2024-03-23T12:00:00'
}

# 'stock_data' 토픽으로 메시지 전송
producer.send('stock_data', value=test_message)
producer.flush()  # 모든 메시지가 전송되도록 보장

print("Test message sent to Kafka")

