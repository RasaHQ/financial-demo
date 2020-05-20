## greet/bye path
* greet
  - utter_greet

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

## transfer money ask transfer charge
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

## Transfer money ask account balance
* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance{"payment_amount":"balance"}
    - slot{"payment_amount":"balance"}
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

## Transfer money ask account balance

* transfer_money
    - transfer_form
    - form{"name":"transfer_form"}
* check_balance
    - action_account_balance
    - transfer_form
    - form{"name":null}
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
    
## Fuel an entity with IXO credits
* order
    - utter_project_entity_id
    - utter_fee_description_freehosting
    - utter_ask_confirm_hosting_offer
    - utter_transaction_fee_ixo
    - utter_fuel_credit_amount
    - utter_fuel_credit_refund_policy
* send_ixo
    - fuel_entity_form
    - form{"name":"fuel_entity_form"}
    - utter_ask_fuel_entity_form_ixo_amount
    - utter_got_it
    - utter_ask_fuel_entity_form_to_wallet_address
    - utter_ask_fuel_entity_form_from_wallet_address
    - utter_wallet_balance_pre
    - utter_wallet_balance_post
* chitchat
    - utter_chitchat
    - form{"name":"fuel_entity_form"}
    - form{"name": null}
* stop
    - utter_ask_continue
* pay_cc
    - cc_payment_form
    - form{"name":"cc_payment_form"}
    - form{"name": null}
    - utter_ask_back_to_transfer
* deny
    - utter_ok
    - form{"name": null}
* success
    - utter__fuel_added
