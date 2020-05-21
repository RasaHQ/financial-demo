## greet/bye path
* greet
  - utter_greet

## say goodbye
* goodbye
  - utter_goodbye

## Fuel an entity with IXO credits
* order
    - utter_add_fuel
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
* stop
    - utter_ask_continue
* deny
    - utter_ok
    - form{"name": null}
* success
    - utter_adding_fuel
