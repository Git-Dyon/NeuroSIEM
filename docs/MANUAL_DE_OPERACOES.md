📘 Manual de Operações: NeuroSIEM 2.0

Autor: Dyon
Projeto: SIEM Automatizado com IA Local (Wazuh + Ollama + Python)

Este documento descreve os procedimentos padrão para iniciar, operar e encerrar o laboratório NeuroSIEM, garantindo a integridade dos dados e o funcionamento correto da integração com a IA.

🟢 1. Ritual de Inicialização (Start-up)

Sempre execute nesta ordem ao ligar o computador.

Passo 1: O "Pedágio" de Memória (Obrigatório)

O Windows/WSL reseta essa configuração a cada reinicialização. Sem isso, o banco de dados do Wazuh (Indexer) trava e não sobe.

sudo sysctl -w vm.max_map_count=262144


Passo 2: Acordar a Infraestrutura (Backend)

Inicia os containers do Wazuh.

cd ~/NeuroSIEM_2.0/wazuh-docker/single-node
docker compose start


(Caso seja a primeira vez ou tenha usado down, use docker compose up -d).

Verificação de Saúde:
Rode docker compose ps. Todos os serviços devem estar com status "Up".

Passo 3: Ativar o Frontend (Dashboard)

Abre o painel de comando visual.

cd ~/NeuroSIEM_2.0/dashboard
source venv_dash/bin/activate
streamlit run app.py


Isso abrirá automaticamente o navegador em http://localhost:8501.

⚙️ 2. Configuração da Integração (Primeira Vez)

Se você recriou os containers, é necessário injetar o script e configurar o Wazuh novamente.

A. Injeção do Script

# Instalar dependências no container
docker exec -u 0 single-node-wazuh.manager-1 dnf install -y python3-pip
docker exec -u 0 single-node-wazuh.manager-1 pip3 install requests

# Copiar script local para dentro do container
docker cp ~/NeuroSIEM_2.0/src/integrator.py single-node-wazuh.manager-1:/var/ossec/integrations/custom-neurosiem

# Ajustar permissões
docker exec -u 0 single-node-wazuh.manager-1 chmod 750 /var/ossec/integrations/custom-neurosiem
docker exec -u 0 single-node-wazuh.manager-1 chown root:wazuh /var/ossec/integrations/custom-neurosiem


B. Configuração do Gatilho (ossec.conf) lembre-se de alterar o nivel para o desejado:

Adicione este bloco ao final do arquivo /var/ossec/etc/ossec.conf do container:

<integration>
  <name>custom-neurosiem</name>
  <hook_url>[https://google.com](https://google.com)</hook_url>
  <level>3</level>
  <alert_format>json</alert_format>
</integration>


Após editar, reinicie o manager: docker exec -u 0 single-node-wazuh.manager-1 /var/ossec/bin/wazuh-control restart

🔴 3. Ritual de Encerramento (Shutdown)

Siga rigorosamente para evitar corrupção do banco de dados.

Parar o Dashboard: No terminal do Streamlit, pressione Ctrl + C.

Congelar a Infraestrutura:

cd ~/NeuroSIEM_2.0/wazuh-docker/single-node
docker compose stop


⚠️ Nota: Evite usar docker compose down para não perder as bibliotecas instaladas manualmente no container.

🛠️ 4. Testes e Debug

Monitorar a IA em Tempo Real

Para ver o script Python trabalhando e a resposta do Ollama ao vivo:

docker exec -it single-node-wazuh.manager-1 tail -f /var/ossec/logs/integrations.log


Simular um Ataque (Teste de Fogo)

Gera logs de falha de autenticação SSH para disparar o gatilho:

docker exec single-node-wazuh.manager-1 bash -c 'for i in {1..8}; do logger "Dec 11 22:00:00 server sshd[1234]: Failed password for root from 192.168.66.66 port 22 ssh2"; done'
