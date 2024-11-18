import json
import base64
from queue import Empty, Queue
import paho.mqtt.client as mqtt
import cv2

class CommunicationHandler:
    def __init__(self, player_images, player_names, substrate_name):
        self.player_images = player_images
        self.player_names = player_names
        self.substrate_name = substrate_name

        self.current_images = []
        self.current_orientations = []
        
        
        # Dirección del broker MQTT
        self.BROKER_ADDRESS = "172.29.113.185"  # Cambia esta IP por la del broker en tu red local
        self.DATA_TOPIC = "topic/data"
        self.ACTIONS_TOPIC = "topic/actions"
        
        self.able_to_move = False  # Flag que indica si el jugador puede moverse

        # Cola para almacenar las acciones recibidas
        self.action_queue = Queue()

        # Inicializa el cliente MQTT
        self.client = mqtt.Client()

        # Conectar el cliente al broker y configurar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message_received

        # Inicia la conexión al broker
        self.client.connect(self.BROKER_ADDRESS)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al broker MQTT")
            # Suscribirse al tópico de acciones
            self.client.subscribe(self.ACTIONS_TOPIC)
        else:
            print(f"Error al conectar al broker. Código de error: {rc}")

    def publish_data_topic(self, new_images, player_orientations, player_turn, text):
        """
        Publica información en el tópico de datos con la estructura necesaria para cada agente.
        """
        data_dict = {}
        for i, (img_array, orientation) in enumerate(zip(new_images, player_orientations)):
            agent_is_turn = (str(i+1) == player_turn)
            agent_text = text if agent_is_turn else "Is not your turn"
            
            # Se asegura de que la imagen esté en formato base64 para enviarla en JSON
            _, img_encoded = cv2.imencode('.jpg', img_array)
            img_base64 = base64.b64encode(img_encoded).decode('utf-8')

            agent_data = {
                "is_turn": agent_is_turn,
                "image": img_base64,
                "text": agent_text,
                "orientation": orientation
            }
            agent_id = f"{i+1}"
            data_dict[agent_id] = agent_data

        # Serializa los datos en JSON y publica en el tópico
        data_json = json.dumps(data_dict)
        self.client.publish(self.DATA_TOPIC, data_json)
        
        self.current_images = new_images
        self.current_orientations = player_orientations

    def publish_data_topic_from_agent(self, player_turn, text):
        self.publish_data_topic(self.current_images, self.current_orientations, player_turn, text)
    
    def on_message_received(self, client, userdata, message):
        try:
            msg_json = message.payload.decode("utf-8")
            msg = json.loads(msg_json)

            agent_id = msg.get("agent_id")
            agent_action = msg.get("action")

            print(f"Acción recibida - Agente: {agent_id}, Acción: {agent_action}")

            self.process_agent_action(agent_id, agent_action)
        
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el mensaje JSON: {e}")
    
    def process_agent_action(self, agent_id, agent_action):
        #if agent_id == self.agent_id:
        self.action_queue.put((agent_id, agent_action))

    def get_next_action(self, timeout=None):
        try:
            agent_id, agent_action = self.action_queue.get(timeout=timeout)
            return agent_id, agent_action
        except Empty:
            return None, None

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Desconectado del broker MQTT")