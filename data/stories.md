## greet/bye path
* greet
  - utter_greet
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## pay credit card happy path
* greet
    - utter_greet
* pay_cc
    - cc_payment_form
    - form{"name": "cc_payment_form"}
    - form{"name": null}
* thankyou
    - utter_noworries

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

## transfer money
* transfer_money
    - transfer_form
    - form{"name": "transfer_form"}
* ask_transfer_charge
    - utter_transfer_charge
    - transfer_form
    - form{"name": null}

## search transactions happy path
* greet
    - utter_greet
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
