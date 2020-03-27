## greet/bye path
* greet: hi
    - utter_greet
* goodbye: bye
    - utter_goodbye

## say goodbye
* goodbye: bye
    - utter_goodbye

## pay credit card happy path
* greet: hi
    - utter_greet
* pay_cc: i want to pay off my [gringots](credit_card) credit card
    - slot{"credit_card":"gringots"}
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - slot{"requested_slot":"payment_amount"}
* form: inform: my [current balance](payment_amount)
    - slot{"payment_amount":"current balance"}
    - form: cc_payment_form
    - slot{"payment_amount":550}
    - slot{"payment_amount_type":" (your current balance)"}
    - slot{"requested_slot":"time"}
* form: inform: [next week tuesday](time:2020-02-25T00:00:00.000-08:00)
    - slot{"time":"2020-02-25T00:00:00.000-08:00"}
    - form: cc_payment_form
    - slot{"time":"12:00AM, Tuesday Feb 25, 2020"}
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: cc_payment_form
    - slot{"confirm":true}
    - form{"name":null}
    - slot{"requested_slot":null}


## pay credit card and check account balance inside form
* pay_cc: i want to pay off my [justice bank](credit_card) credit card
    - slot{"credit_card":"justice bank"}
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - slot{"requested_slot":"payment_amount"}
* form: inform: my [current balance](payment_amount)
    - slot{"payment_amount":"current balance"}
    - form: cc_payment_form
    - slot{"payment_amount":550}
    - slot{"payment_amount_type":" (your current balance)"}
    - slot{"requested_slot":"time"}
* check_balance: what's my account balance?
    - action_account_balance
    - utter_ask_continue
* affirm: yes
    - cc_payment_form
    - slot{"requested_slot":"time"}
* form: inform: [8am on Friday February 21 2020](time:2020-02-21T08:00:00.000-08:00)
    - slot{"time":"2020-02-21T08:00:00.000-08:00"}
    - form: cc_payment_form
    - slot{"time":"08:00AM, Friday Feb 21, 2020"}
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: cc_payment_form
    - slot{"confirm":true}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money
* transfer_money: I want to transfer money to [John](PERSON)
    - slot{"PERSON":"John"}
    - transfer_form
    - form{"name":"transfer_form"}
    - slot{"requested_slot":"amount-of-money"}
* form: inform: [$60](amount-of-money:60)
    - slot{"amount-of-money":60}
    - form: transfer_form
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: transfer_form
    - slot{"confirm":true}
    - slot{"amount_transferred":60}
    - form{"name":null}
    - slot{"requested_slot":null}

## is there a transfer charge
* ask_transfer_charge: is there a transfer charge
    - utter_transfer_charge

## transfer money
* transfer_money: i want to transfer money to [Percy](PERSON)
    - slot{"PERSON":"Percy"}
    - transfer_form
    - form{"name":"transfer_form"}
    - slot{"requested_slot":"amount-of-money"}
* ask_transfer_charge: is there a transfer charge?
    - utter_transfer_charge
    - transfer_form
    - slot{"requested_slot":"amount-of-money"}
* form: inform: [600](number)
    - form: transfer_form
    - slot{"amount-of-money":600}
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: transfer_form
    - slot{"confirm":true}
    - slot{"amount_transferred":600}
    - form{"name":null}
    - slot{"requested_slot":null}

## search transactions happy path
* search_transactions: I want to search my spending history
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"search_type":"spend"}
    - slot{"requested_slot":"time"}
* form: inform: [Jan 2019](time:2019-01-01T00:00:00.000-08:00)
    - slot{"time":"2019-01-01T00:00:00.000-08:00"}
    - form: transact_search_form
    - slot{"time":"2019-01-01T00:00:00.000-08:00"}
    - slot{"start_time":"Tuesday Jan 01, 2019"}
    - slot{"end_time":"Wednesday Jan 01, 2020"}
    - slot{"transact_grain":"year"}
    - form{"name":null}
    - slot{"requested_slot":null}
* thankyou: thank you
    - utter_noworries


## search transactions happy path no greet or thanks
* check_earnings: how much did I earn [in Jan 2019](time:2019-01-01T00:00:00.000-08:00)?
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - slot{"start_time":"Wednesday Jan 01, 2020"}
    - slot{"end_time":"Saturday Feb 01, 2020"}
    - slot{"transact_grain":"month"}
    - slot{"search_type":"deposit"}
    - form{"name":null}
    - slot{"requested_slot":null}



## search transactions switch to transfer money, deny
* check_earnings: how much did i earn?
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"search_type":"deposit"}
    - slot{"requested_slot":"time"}
* transfer_money: actually I want to transfer money
    - utter_ask_switch_goal
* deny: no
    - transact_search_form
    - slot{"requested_slot":"time"}
* form: inform: [january 2020](time:2020-01-01T00:00:00.000-08:00)
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - form: transact_search_form
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - slot{"start_time":"Wednesday Jan 01, 2020"}
    - slot{"end_time":"Saturday Feb 01, 2020"}
    - slot{"transact_grain":"month"}
    - form{"name":null}
    - slot{"requested_slot":null}

## search transactions switch to transfer money, don't continue transactions
* check_earnings: How much did i earn
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"search_type":"deposit"}
    - slot{"requested_slot":"time"}
* transfer_money: i want to transfer money
    - utter_ask_switch_goal
* affirm: yes
    - transfer_form
    - form{"name":"transfer_form"}
    - slot{"requested_slot":"PERSON"}
* form: inform: to [Paul](PERSON)
    - slot{"PERSON":"Paul"}
    - form: transfer_form
    - slot{"requested_slot":"amount-of-money"}
* form: inform: [$45](amount-of-money:45)
    - slot{"amount-of-money":45}
    - form: transfer_form
    - slot{"amount-of-money":45}
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: transfer_form
    - slot{"confirm":true}
    - slot{"amount_transferred":45}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_back_to_transact
* deny: no
    - utter_ok


<!--This story is not working; once it goes back to transact_search_form it just does action_listen and doesn't prompt for anything-->
## search transactions switch to transfer money
* search_transactions: I want to search my spending history
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"search_type":"spend"}
    - slot{"requested_slot":"time"}
* transfer_money: actually I want to transfer money to [Lisa](PERSON)
    - slot{"PERSON":"Lisa"}
    - utter_ask_switch_goal
* affirm: yes
    - transfer_form
    - form{"name":"transfer_form"}
    - slot{"PERSON":"Lisa"}
    - slot{"requested_slot":"amount-of-money"}
* form: inform: [$35](amount-of-money:35)
    - slot{"amount-of-money":35}
    - form: transfer_form
    - slot{"amount-of-money":35}
    - slot{"requested_slot":"confirm"}
* form: affirm: /affirm
    - form: transfer_form
    - slot{"confirm":true}
    - slot{"amount_transferred":35}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_ask_back_to_transact
* affirm: yes
    - transact_search_form
    - form{"name":"transact_search_form"}
    - slot{"requested_slot":"time"}
* form: inform: [january 2020](time:2020-01-01T00:00:00.000-08:00)
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - form: transact_search_form
    - slot{"time":"2020-01-01T00:00:00.000-08:00"}
    - slot{"start_time":"Wednesday Jan 01, 2020"}
    - slot{"end_time":"Saturday Feb 01, 2020"}
    - slot{"transact_grain":"month"}
    - form{"name":null}
    - slot{"requested_slot":null}
