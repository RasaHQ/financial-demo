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
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## happy path fraud story, no transactions found initially
* card_lost{"account_type": "credit", "time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## happy path fraud story, no transactions found initially
* card_lost{"account_type": "credit"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## happy path fraud story, no transactions found initially
* card_lost{"time": "2020-08-10T00:00:00.000-07:00"}
  - utter_card_locked
  - spending_history_form
  - form{"name": "spending_history_form"}
  - form{"name": null}
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

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
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## no transactions found in search
  - utter_ask_fraudulent_transactions
* inform{"vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## no transactions found in search
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04"}
  - action_update_transactions
  - slot{"reviewed_transactions": null}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## search transactions by time & vendor
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04", "vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## search transactions by time
  - utter_ask_fraudulent_transactions
* inform{"time": "2021-08-04"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## search transactions by vendor
  - utter_ask_fraudulent_transactions
* inform{"vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## inform all transactions
  - utter_ask_fraudulent_transactions
* inform
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## inform all (every one) transactions
  - utter_ask_fraudulent_transactions
* inform{"number": "1"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## search transactions by negation
  - utter_ask_fraudulent_transactions
* inform{"negation": "except", "vendor_name": "starbucks"}
  - action_update_transactions
  - slot{"reviewed_transactions": ["target", "starbucks"]}
* affirm
  - utter_confirm_transaction_dispute
  - utter_replace_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## denies fraudulent transactions prompt
  - utter_ask_fraudulent_transactions
* deny
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## denies fraudulent transactions prompt
  - utter_ask_fraudulent_transactions
* deny{"number": "0"}
  - utter_missing_card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

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
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* delivery_time
  - utter_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## user confirms address and asks for delivery time
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* affirm+delivery_time
  - utter_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else


## user asks for priority delivery
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* priority_delivery
  - utter_priority_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## user asks for delivery time and then for priority delivery
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* delivery_time
  - utter_delivery_time
  - mailing_address_form
* priority_delivery
  - utter_priority_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_anything_else

## Follow-on intent for paying credit card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* pay_cc
  - utter_can_do
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_ask_pay_cc

## Affirm credit card payment prompt
  - utter_ask_pay_cc
* affirm
  - cc_payment_form
  - form{"name": "cc_payment_form"}
  - form{"name": null}

## Deny credit card payment prompt
  - utter_ask_pay_cc
* deny
  - utter_ok
  - utter_anything_else

## Follow-on story for paying credit card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* pay_cc
  - utter_can_do
  - mailing_address_form
* delivery_time
  - utter_delivery_time
  - mailing_address_form
* priority_delivery
  - utter_priority_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_ask_pay_cc


## Follow-on story for paying credit card
  - mailing_address_form
  - form{"name": "mailing_address_form"}
* pay_cc
  - utter_can_do
  - mailing_address_form
* affirm+delivery_time
  - utter_delivery_time
  - mailing_address_form
* priority_delivery
  - utter_priority_delivery_time
  - mailing_address_form
  - form{"name": null}
  - utter_sent_replacement
  - utter_ask_pay_cc


