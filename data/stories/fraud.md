## delivery time FAQ
* delivery_time
  - utter_delivery_time

## Follow up prompt
  - utter_anything_else
* affirm
  - utter_help

## Follow up prompt, user responds with deny
  - utter_anything_else
* deny
  - utter_ok

## happy path fraud story, no transactions found initially
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address


## happy path fraud story, no transactions found initially
* card_lost{"account_type": "credit", "time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address

## happy path fraud story, no transactions found initially
* card_lost{"account_type": "credit"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address

## happy path fraud story, no transactions found initially
* card_lost{"time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address

## happy path fraud story
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": ["target", "starbucks"]}
  - utter_ask_fraudulent_transactions

## happy path fraud story
* card_lost{"account_type": "credit", "time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": ["target", "starbucks"]}
  - utter_ask_fraudulent_transactions

## happy path fraud story
* card_lost{"account_type": "credit"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": ["target", "starbucks"]}
  - utter_ask_fraudulent_transactions

## happy path fraud story
* card_lost{"time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": ["target", "starbucks"]}
  - utter_ask_fraudulent_transactions


## no transactions found in search
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address


## no transactions found in search
  - utter_ask_fraudulent_transactions
* inform{"vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address


## no transactions found in search
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04"}
  - action_update_transactions
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - utter_confirm_address


## search transactions by time & vendor
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address

## search transactions by time
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address

## search transactions by vendor
  - utter_ask_fraudulent_transactions
* inform{"vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address


## inform all transactions
  - utter_ask_fraudulent_transactions
* inform
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address


## search transactions by negation
  - utter_ask_fraudulent_transactions
* inform{"negation": "except", "vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address


## denies fraudulent transactions prompt
  - utter_ask_fraudulent_transactions
* deny
  - utter_missing_card
  - utter_confirm_address


## fraudulent transaction list is not correct, reprompt for transactions
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* deny
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": ["target", "starbucks"]}
  - utter_ask_fraudulent_transactions

## user asks for delivery time
  - utter_confirm_address
* delivery_time
  - utter_delivery_time
  - utter_confirm_address


## user confirms address and asks for delivery time
  - utter_confirm_address
* affirm+delivery_time
  - utter_delivery_time
  - utter_confirm_delivery
* affirm
  - utter_sent_replacement
  - utter_anything_else


## user confirms address, asks for delivery time, and asks for priority delivery
  - utter_confirm_address
* affirm+delivery_time
  - utter_delivery_time
  - utter_confirm_delivery
* priority_delivery
  - utter_priority_delivery_time
  - utter_confirm_delivery
* affirm
  - utter_sent_replacement
  - utter_anything_else

## user affirms address
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else

## user corrects their address
  - utter_confirm_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address

## user corrects their address
  - utter_confirm_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035", "number": "123"}
  - action_update_address
  - utter_confirm_address

## user denies prompt and then corrects their address
  - utter_confirm_address
* deny
  - utter_ask_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address

## user denies prompt and then corrects their address
  - utter_confirm_address
* deny
  - utter_ask_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035", "number": "123"}
  - action_update_address
  - utter_confirm_address


## user denies and corrects their address in single response
  - utter_confirm_address
* deny+inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address


## user denies and corrects their address in single response
  - utter_confirm_address
* deny+inform{"address": "123 Main Street, Lewis Center, OH 43035", "number": "123"}
  - action_update_address
  - utter_confirm_address
