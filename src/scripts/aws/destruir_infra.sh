#!/usr/bin/env bash
# Remove tudo que criar_infra.sh criou (para parar a cobranca).
set -euo pipefail
NOME="lastmile-ap2"
source ~/${NOME}.info
export AWS_DEFAULT_REGION="$REGIAO"
read -r -p "Apagar EC2 $INSTANCE_ID, Elastic IP e Security Group? Os dados do banco serao perdidos. (digite sim) " R
[ "$R" = "sim" ] || exit 0
aws ec2 terminate-instances --instance-ids "$INSTANCE_ID" >/dev/null
aws ec2 wait instance-terminated --instance-ids "$INSTANCE_ID"
aws ec2 release-address --allocation-id "$ALLOC_ID"
aws ec2 delete-security-group --group-id "$SG_ID"
aws ec2 delete-key-pair --key-name "${NOME}-key"
echo "Removido."
