## greet/bye path
* greet: hi
    - utter_greet
    - utter_help
* goodbye: bye
    - utter_goodbye

## say goodbye
* goodbye: bye
    - utter_goodbye

## pay credit card happy path
* greet: hi
    - utter_greet
    - utter_help
* pay_cc: i want to pay off my [emblm]{"entity": "credit_card", "value": "emblem"}
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* form: inform: my [current balance](payment_amount)
    - form: cc_payment_form
* form: inform: next week tuesday
    - form: cc_payment_form
* form: affirm: /affirm
    - form: cc_payment_form
    - form{"name":null}


## pay credit card and check account balance inside form
* pay_cc: i want to pay off my [justice bank](credit_card) [credit card]{"entity":"account_type","value":"credit"}
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* form: inform: my [current balance](payment_amount)
    - form: cc_payment_form
* check_balance: what's my account balance?
    - action_account_balance
    - utter_ask_continue
* affirm: Yes
    - cc_payment_form
* form: inform: 8am on Friday February 21 2020
    - form: cc_payment_form
* form: affirm: /affirm
    - form: cc_payment_form
    - form{"name":null}

## transfer money
* transfer_money: I want to transfer money to [John](PERSON)
    - transfer_form
    - form{"name":"transfer_form"}
* form: inform: [$60](amount-of-money:60)
    - form: transfer_form
* form: affirm: /affirm
    - form: transfer_form
    - form{"name":null}

## is there a transfer charge
* ask_transfer_charge: is there a transfer charge
    - utter_transfer_charge

## transfer money
* transfer_money: i want to transfer money to [Percy](PERSON)
    - transfer_form
    - form{"name":"transfer_form"}
* ask_transfer_charge: is there a transfer charge?
    - utter_transfer_charge
    - transfer_form
* form: inform: [600](number)
    - form: transfer_form
* form: affirm: /affirm
    - form: transfer_form
    - form{"name":null}

## search transactions happy path
* search_transactions: I want to search my spending history
    - transact_search_form
    - form{"name":"transact_search_form"}
* form: inform: Jan 2019
    - form: transact_search_form
    - form{"name":null}
* thankyou: thank you
    - utter_noworries


## search transactions happy path no greet or thanks
* check_earnings: how much did I earn [in Jan 2019]{"entity": "time", "value": "2019-01-01T00:00:00.000-08:00"}?
    - transact_search_form
    - form{"name":"transact_search_form"}
    - form{"name":null}



## search transactions switch to transfer money, deny
* check_earnings: how much did i earn?
    - transact_search_form
    - form{"name":"transact_search_form"}
* transfer_money: actually I want to transfer money
    - utter_ask_switch_goal
* deny: no
    - transact_search_form
* form: inform: january 2020
    - form: transact_search_form
    - form{"name":null}

## search transactions switch to transfer money, don't continue transactions
* check_earnings: How much did i earn
    - transact_search_form
    - form{"name":"transact_search_form"}
* transfer_money: i want to transfer money
    - utter_ask_switch_goal
* affirm: yes
    - transfer_form
    - form{"name":"transfer_form"}
* form: inform: to [Paul](PERSON)
    - form: transfer_form
* form: inform: [$45](amount-of-money:45)
    - form: transfer_form
* form: affirm: /affirm
    - form: transfer_form
    - form{"name":null}
    - utter_ask_back_to_transact
* deny: no
    - utter_ok


## search transactions switch to transfer money
* search_transactions: I want to search my spending history
    - transact_search_form
    - form{"name":"transact_search_form"}
* transfer_money: actually I want to transfer money to [Lisa](PERSON)
    - utter_ask_switch_goal
* affirm: yes
    - transfer_form
    - form{"name":"transfer_form"}
* form: inform: [$35](amount-of-money:35)
    - form: transfer_form
* form: affirm: /affirm
    - form: transfer_form
    - form{"name":null}
    - utter_ask_back_to_transact
* affirm: yes
    - transact_search_form
    - form{"name":"transact_search_form"}
* form: inform: january 2020
    - form: transact_search_form
    - form{"name":null}


## check credit account balance
* check_balance: What are my [credit accounts]{"entity":"account_type","value":"credit"}
    - action_credit_card_balance


## check list of known recipients
* check_recipients: Show me my list of recipients
    - action_recipients
