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

## happy path fraud story
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* affirm+inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else


## happy path fraud story, filter by time & vendor
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else

## happy path fraud story, filter by time
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else

## happy path fraud story, filter by vendor
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else

## happy path fraud story, no fraudulent transactions
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* deny
  - utter_missing_card
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else

## fraud story, fraudulent transaction list is not correct, reprompt for transactions
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* deny
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions

## fraud story, user corrects their address
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else


## fraud story, user denies address confirmation, prompt is given to update address
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* deny
  - utter_ask_address
* inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else


## fraud story, user denies & corrects their address
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* deny+inform{"address": "123 Main Street, Lewis Center, OH 43035"}
  - action_update_address
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else


## fraud story, user asks for delivery time
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* delivery_time
  - utter_delivery_time
  - utter_confirm_address
* affirm
  - utter_sent_replacement
  - utter_anything_else


## fraud story, user confirms address and asks for delivery time
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - utter_confirm_address
* affirm+delivery_time
  - utter_delivery_time
  - utter_confirm_delivery
* affirm
  - utter_sent_replacement
  - utter_anything_else


## fraud story, user confirms address, asks for delivery time, and asks for priority delivery
* card_lost
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
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
