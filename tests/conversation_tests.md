## Story from conversation with cd79f02b4a20404aa254b11f2a798592 on April 2nd 2020

* greet: hello
    - utter_greet
* transfer_money: i want to transfer money
    - transfer_form
    - form{"name":"transfer_form"}
    - slot{"requested_slot":"PERSON"}
* affirm: [Melinda](PERSON)
    - slot{"PERSON":"Melinda"}
    - transfer_form
    - slot{"PERSON":"Melinda"}
    - slot{"requested_slot":"amount-of-money"}
* inform: [5000](number)
    - transfer_form
    - slot{"amount-of-money":5000}
    - slot{"requested_slot":"confirm"}
* affirm: /affirm
    - transfer_form
    - slot{"confirm":true}
    - slot{"amount_transferred":5000}
    - form{"name":null}
    - slot{"requested_slot":null}
* thankyou: thanks!
