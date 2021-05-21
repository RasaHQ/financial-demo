chat() {
    d="{\"sender\": \"tester\", \"message\": \"$@\"}" ;
    echo $d ;
    curl --request POST \
        --url http://localhost:5002/core/webhooks/rest/webhook \
        --data $d \
        -H "Content-type: application/json" ;
}
