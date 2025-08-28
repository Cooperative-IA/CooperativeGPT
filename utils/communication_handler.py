import json
import base64
from queue import Empty, Queue
import paho.mqtt.client as mqtt
import cv2
import os
from datetime import datetime

class CommunicationHandler:
    def __init__(self, player_images, player_names, substrate_name, port, logger_timestamp):
        self.player_images = player_images
        self.player_names = player_names
        self.substrate_name = substrate_name

        self.current_images = []
        self.current_orientations = []
        self.log_path = os.path.join("logs", str(logger_timestamp))
        
        # Create human_audios directory
        self.audio_path = os.path.join(self.log_path, "human_audios")
        os.makedirs(self.audio_path, exist_ok=True)
        
        # Dirección del broker MQTT
        self.BROKER_ADDRESS = "172.24.98.252"  # Cambia esta IP por la del broker en tu red local
        self.DATA_TOPIC = "topic/data"
        self.ACTIONS_TOPIC = "topic/actions"
        self.AUDIO_TOPIC = "topic/audio"
        
        self.able_to_move = False  # Flag que indica si el jugador puede moverse

        # Cola para almacenar las acciones recibidas
        self.action_queue = Queue()

        # Inicializa el cliente MQTT
        self.client = mqtt.Client()

        # Conectar el cliente al broker y configurar callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message_received

        # Inicia la conexión al broker
        self.client.connect(self.BROKER_ADDRESS, port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al broker MQTT")
            # Suscribirse a los tópicos
            self.client.subscribe(self.ACTIONS_TOPIC)
            self.client.subscribe(self.AUDIO_TOPIC)
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
            
            # TODO: all turn in true
            agent_data = {
                "is_turn": True,
                "image": img_base64,
                "text": agent_text,
                "orientation": orientation,
                "game_started": True
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

            if message.topic == self.ACTIONS_TOPIC:
                agent_id = msg.get("agent_id")
                agent_action = msg.get("action")
                print(f"Acción recibida - Agente: {agent_id}, Acción: {agent_action}")
                self.process_agent_action(agent_id, agent_action)
            
            elif message.topic == self.AUDIO_TOPIC:
                audio_base64 = msg.get("audio")
                agent_id = msg.get("agent_id") 
                message_kind = msg.get("message_kind")
                
                # Create agent directory if not exists
                agent_dir = os.path.join(self.audio_path, f"agent_{agent_id}")
                os.makedirs(agent_dir, exist_ok=True)
                
                # Generate filename with timestamp and message kind
                timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
                filename = f"{timestamp}_{message_kind}.wav"
                filepath = os.path.join(agent_dir, filename)
                
                # Decode and save audio
                audio_bytes = base64.b64decode(audio_base64)
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)
                
                print(f"Audio saved for agent {agent_id}: {filename}")
        
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


    def wait_for_agents_to_start(self):
        agents_started = set()
        while len(agents_started) < len([player_name for player_name in self.player_names if "bot" not in player_name]):
            agent_id, action = self.get_next_action(timeout=1)
            if agent_id is not None and action == "start":
                agents_started.add(agent_id)
                print(f"Agent {agent_id} ready to start")
        print("All agents ready to start")
    def send_go_ahead_message(self):
        data_dict = {}
        for i in range(len(self.player_names)):
            agent_id = str(i+1)
            data_dict[agent_id] = {
                "is_turn": False,
                "image": "",
                "text": "go ahead",
                "orientation": 0,
                "game_started": True,
            }
        self.client.publish(self.DATA_TOPIC, json.dumps(data_dict))

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Desconectado del broker MQTT")

    def send_end_game_message(self):
        data_dict = {}
        for i in range(len(self.player_names)):
            agent_id = str(i+1)
            
            data_dict[agent_id] = {
                "is_turn": False,
                "image": "",
                "text": "",
                "orientation": 0,
                "end_game": True,
            }
        self.client.publish(self.DATA_TOPIC, json.dumps(data_dict))
