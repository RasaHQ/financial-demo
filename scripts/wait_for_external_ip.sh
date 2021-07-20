AWS_EKS_NAMEPACE=${1:-"my-namespace"}
AWS_EKS_RELEASE_NAME=${2:-"my-release"}
ATTEMPTS=${3:-100}
COUNT=1;
IP=""
while [ -z $IP ]; do
    IP=$(kubectl --namespace ${AWS_EKS_NAMEPACE} get service ${AWS_EKS_RELEASE_NAME}-rasa-x-nginx --output jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    if [[ $COUNT -eq $ATTEMPTS ]]; then
      echo "# Limit of $ATTEMPTS attempts has exceeded."
      exit 1
    fi
    if [[ -z "$IP" ]]; then
      echo -e "$(( COUNT++ ))... \c"
      sleep 2
    fi
done
echo 'Found External IP'
echo 'Login at: http://'$IP':80/login'
