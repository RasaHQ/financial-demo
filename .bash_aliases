generate_post_data()
{
  cat <<EOF
{
  "message": "$@",
  "sender": "$GITPOD_WORKSPACE_ID",
}
EOF
}

chat() {
    curl  \
    -H "Accept: application/json" \
    -H "Content-Type:application/json" \
    -X POST \
    --data "$(generate_post_data $@)" \
    --url "http://localhost:5005/webhooks/rest/webhook"
}