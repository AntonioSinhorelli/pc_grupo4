#!/usr/bin/env bash
# Cria a infraestrutura da AP2 na AWS: Security Group (22 e 8000), EC2 Ubuntu 24.04 e Elastic IP.
# Rodar no AWS CloudShell (ja autenticado) ou com o AWS CLI configurado.
# Uso: ./criar_infra.sh [tipo_instancia]      (padrao: t3.medium)
set -euo pipefail

REGIAO="${AWS_REGION:-us-east-1}"
TIPO="${1:-t3.medium}"
NOME="lastmile-ap2"
CHAVE="${NOME}-key"
export AWS_DEFAULT_REGION="$REGIAO"

echo ">> conta/regiao"; aws sts get-caller-identity --query Account --output text; echo "$REGIAO"

# Seu IP publico (para liberar o SSH apenas para voce). No CloudShell esse IP e o da AWS,
# entao informe o SEU IP: MEU_IP=200.1.2.3 ./criar_infra.sh
MEU_IP="${MEU_IP:-}"
if [ -z "$MEU_IP" ]; then
  echo "ERRO: informe seu IP publico (veja em https://checkip.amazonaws.com no seu PC):"
  echo "      MEU_IP=SEU.IP.AQUI ./criar_infra.sh"; exit 1
fi
# Origem da porta 8000: por padrao, so o seu IP. Para o avaliador acessar: ORIGEM_API=0.0.0.0/0
ORIGEM_API="${ORIGEM_API:-${MEU_IP}/32}"

VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
[ "$VPC_ID" != "None" ] || { echo "ERRO: sem VPC padrao nesta regiao"; exit 1; }

echo ">> Security Group"
SG_ID=$(aws ec2 create-security-group --group-name "${NOME}-sg" \
  --description "AP2 lastmile: SSH 22 e API 8000 (5432 fechada)" --vpc-id "$VPC_ID" \
  --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22   --cidr "${MEU_IP}/32" >/dev/null
aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 8000 --cidr "$ORIGEM_API"   >/dev/null

echo ">> Key pair (salva em ~/${CHAVE}.pem)"
aws ec2 create-key-pair --key-name "$CHAVE" --query KeyMaterial --output text > ~/"${CHAVE}.pem"
chmod 400 ~/"${CHAVE}.pem"

echo ">> AMI Ubuntu 24.04"
AMI=$(aws ssm get-parameter \
  --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query Parameter.Value --output text)

# Instala Docker, Compose e Git no primeiro boot.
cat > /tmp/user-data.sh <<'UD'
#!/bin/bash
set -eux
apt-get update -y
apt-get install -y git ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
usermod -aG docker ubuntu
touch /var/lib/cloud/instance/docker-pronto
UD

echo ">> EC2 $TIPO"
INSTANCE_ID=$(aws ec2 run-instances --image-id "$AMI" --instance-type "$TIPO" \
  --key-name "$CHAVE" --security-group-ids "$SG_ID" --user-data file:///tmp/user-data.sh \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}' \
  --metadata-options HttpTokens=required \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${NOME}}]" \
  --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

echo ">> Elastic IP"
ALLOC=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
aws ec2 associate-address --instance-id "$INSTANCE_ID" --allocation-id "$ALLOC" >/dev/null
IP=$(aws ec2 describe-addresses --allocation-ids "$ALLOC" --query 'Addresses[0].PublicIp' --output text)

cat > ~/${NOME}.info <<INFO
REGIAO=$REGIAO
SG_ID=$SG_ID
INSTANCE_ID=$INSTANCE_ID
ALLOC_ID=$ALLOC
IP=$IP
INFO

cat <<FIM

======================================================
Infraestrutura criada.
  IP publico (Elastic IP): $IP
  Chave: ~/${CHAVE}.pem   (baixe pelo menu Acoes do CloudShell)
  SSH:   ssh -i ${CHAVE}.pem ubuntu@$IP
  Aguarde ~3 min o Docker instalar; confira com:
         ssh ... 'ls /var/lib/cloud/instance/docker-pronto && docker compose version'
  Ids salvos em ~/${NOME}.info (usados por destruir_infra.sh)
======================================================
FIM
