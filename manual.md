📘 Manual de Operações: NeuroSIEM 2.0

Autor: DevSecOps Dyon
Projeto: SIEM Automatizado com IA Local (Wazuh + Ollama + Python)

🟢 1. Ritual de Inicialização (Start-up)

Sempre execute nesta ordem ao ligar o computador.

Passo 1: O "Pedágio" de Memória (Obrigatório)

Abrir PowerShell acessar o linux via wsl

sudo sysctl -w vm.max_map_count=262144


Passo 2: Acordar a Infraestrutura (Backend)

Inicia os containers que foram congelados (Stopped).

cd ~/NeuroSIEM_2.0/wazuh-docker/single-node
docker compose start


Verificação de Saúde Rode: docker compose ps
Todos devem estar com status "Up". Se algum estiver "Restarting", investigue.

Passo 3: Ativar o Frontend (Dashboard)

Abre o painel de comando visual.

# 1. Navegue para a pasta do painel
cd ~/NeuroSIEM_2.0/dashboard

# 2. Ative o ambiente virtual isolado
source venv_dash/bin/activate

# 3. Inicie a aplicação e mantenha esse terminal aberto, usará ele apenas para encerrar ao final do dia
streamlit run app.py


Isso abrirá automaticamente o navegador em http://localhost:8501.

🔴 2. Ritual de Encerramento (Shutdown)

Siga rigorosamente para evitar corrupção de dados!

Passo 1: Parar o Dashboard

No terminal onde o Streamlit está rodando, pressione:
Ctrl + C

Passo 2: Congelar a Infraestrutura (Graceful Stop)

⚠️ NUNCA use docker compose down neste projeto, pois perderemos as bibliotecas Python instaladas manualmente dentro do container. Use sempre STOP.

# Navegue até a pasta onde está o docker-compose.yml
# Opção A (Padrão):
cd ~/NeuroSIEM_2.0/wazuh-docker/single-node

# Comando de parada
docker compose stop


Aguarde a mensagem "Stopped" ou "Exited" para todos os serviços.

🛠️ 3. Comandos de Manutenção e Debug

Monitorar a IA em Tempo Real

Para ver o script Python trabalhando e a resposta do Ollama ao vivo:

docker exec -it single-node-wazuh.manager-1 tail -f /var/ossec/logs/integrations.log


Simular um Ataque (Teste de Fogo)

Gera logs de falha de autenticação SSH para disparar o gatilho:

# Dica: Use 'docker exec' para rodar o comando logger DENTRO do container
docker exec single-node-wazuh.manager-1 bash -c 'for i in {1..8}; do logger "Dec 11 22:00:00 server sshd[1234]: Failed password for root from 192.168.66.66 port 22 ssh2"; done'


Reinstalar Dependências (Em caso de desastre/Reset)

Se por acidente o container for deletado (down), rode isto para recuperar o cérebro:

# 1. Instalar pip e requests
docker exec -u 0 single-node-wazuh.manager-1 dnf install -y python3-pip
docker exec -u 0 single-node-wazuh.manager-1 pip3 install requests

# 2. Reenviar o script local
docker cp ~/NeuroSIEM_2.0/src/integrator.py single-node-wazuh.manager-1:/var/ossec/integrations/custom-neurosiem

# 3. Arrumar permissões
docker exec -u 0 single-node-wazuh.manager-1 chmod 750 /var/ossec/integrations/custom-neurosiem
docker exec -u 0 single-node-wazuh.manager-1 chown root:wazuh /var/ossec/integrations/custom-neurosiem


💡 Dica Pro: Alias de Atalho

Adicione no seu ~/.bashrc para iniciar tudo com uma palavra:
alias start-soc='sudo sysctl -w vm.max_map_count=262144 && cd ~/NeuroSIEM_2.0/wazuh-docker/single-node && docker compose start && echo "✅ SOC Iniciado!"'