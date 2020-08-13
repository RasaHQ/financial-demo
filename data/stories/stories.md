## greet/bye path
* greet
  - utter_greet
  - utter_help

## say goodbye
* goodbye
  - utter_goodbye

## pay credit card and check account balance
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* check_balance
    - action_account_balance

## pay credit card and check account balance inside form
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* affirm
    - cc_payment_form
    - form{"name": null}

## pay cc happy path no greet
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* thankyou
    - utter_noworries

## pay credit card happy path
* greet
    - utter_greet
    - utter_help
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}

## pay credit card no greet or thanks
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}

## transfer money
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

## is there a transfer charge
* ask_transfer_charge
    - utter_transfer_charge

## transfer money ask transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
  
## transfer money ask known recipients
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

## transfer money ask known recipients and transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

## transfer money ask known recipients and transfer charge
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_recipients
    - action_recipients
    - transfer_form
    - form{"name": "transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name": "transfer_form"} 
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name":null}
    - slot{"requested_slot":null}

## search transactions happy path
* greet
    - utter_greet
    - utter_help
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
* thankyou
    - utter_noworries

## search transactions happy path no greet
* search_transactions
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}
* thankyou
    - utter_noworries

## search transactions happy path no greet or thanks
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}

## search transactions switch to transfer money
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* affirm
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_back_to_transact
* affirm
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}

## search transactions switch to transfer money, deny
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* deny
    - transact_search_form
    - form{"name": "transact_search_form"}
    - form{"name": null}

## search transactions switch to transfer money, don't continue transactions
* search_transactions OR check_earnings
    - transact_search_form
    - form{"name": "transact_search_form"}
* transfer_money
    - utter_ask_switch_goal
* affirm
    - transfer_form
    - form{"name": "transfer_form"}
    - form{"name": null}
    - utter_ask_back_to_transact
* deny
    - utter_ok

## Transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name":null}
    - slot{"requested_slot":null}

## Pay CC ask account balance

* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* deny
    - utter_ok
    - form{"name": null}
    - slot{"requested_slot":null}

## Pay CC ask account balance

* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
* check_balance
    - action_account_balance
    - utter_ask_continue
* affirm
    - cc_payment_form
    - form{"name": null}
    - slot{"requested_slot":null}

## Transfer money pay credit card
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* affirm
    - transfer_form
    - form{"name":"transfer_form"}
    - form{"name": null}

## Transfer money pay credit card
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* deny
    - utter_ok

## Show list of known recipients
* check_recipients
    - action_recipients

## Show credit accounts
* check_balance{"account_type":"credit"}
    - action_credit_card_balance

## Show specific credit account
* check_balance{"credit_card":"emblem"}
    - action_credit_card_balance

## Show credit accounts
* check_balance{"account_type":"credit","credit_card":"emblem"}
    - action_credit_card_balance

## help
* help
    - utter_help

## acknowledge balance
* greet
    - utter_greet
    - utter_help
* check_balance
    - action_account_balance
    - slot{"payment_amount":null}
* affirm
    - utter_ok
* transfer_money
    - transfer_form


## from Rasa X 56efe3eaf7c0456db86a6669421f885c
* help
    - utter_help
* greet
    - utter_greet
    - utter_help
* thankyou
    - utter_noworries

## from Rasa X 56efe3eaf7c0456db86a6669421f885c (if intent were right)
* help
    - utter_help
* greet
    - utter_greet
    - utter_help
* affirm
    - utter_ok
