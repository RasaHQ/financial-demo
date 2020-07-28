## greet/bye path
* greet: hi
    - utter_greet
* goodbye: bye
    - utter_goodbye

## say goodbye
* goodbye: bye
    - utter_goodbye

## search transactions happy path
* greet: hi
    - utter_greet
* search_transactions: how much did I spend at [Target](vendor_name)?
    - action_search_transact
* thankyou: thank you
    - utter_noworries

## account balance happy path 
* greet: hello
  - utter_greet
* check_balance: what's my account balance?
  - action_account_balance
* thankyou: thanks
  - utter_noworries