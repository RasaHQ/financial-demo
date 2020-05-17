# ixo Assistant
This is the reference contextual AI assistant for ixo networks.

## To install the dependencies:

Run:
```bash
pip install -r requirements.txt
```

## To run the assistant:

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window:
```bash
rasa run actions
```

In another window, run the duckling server (for entity extraction):
```bash
docker run -p 8000:8000 rasa/duckling
```

Then to talk to the assistant, run:
```
rasa shell --debug
```


Note that `--debug` mode will produce a lot of output meant to help you understand how the assistant is working 
under the hood. To simply talk to the assistant, you can remove this flag.


## Overview of the files

`data/core.md` - contains stories 

`data/nlu.md` - contains NLU training data

`actions.py` - contains custom action/api code

`domain.yml` - the domain file, including bot response templates

`config.yml` - training configurations for the NLU pipeline and policy ensemble

`tests/e2e.md` - end-to-end test stories


## Things you can ask the bot

The assistant currently has five skills. You can ask it to:
1. 

It also has a limited ability to switch skills mid-transaction and then return to the transaction at hand.

For the purposes of illustration, the assistant recognises the following entitites:

- `entity `

It recognises the following payment amounts (besides actual currency amounts):

- `minimum balance`
- `current balance`

It recognises the following services (for fee history):

- ` `
- ` `
- ` `

You can change any of these by modifying `actions.py` and the corresponding NLU data.

## Testing the assistant

You can test the assistant on the test conversations by running  `rasa test`. 
Note that if duckling is running when you do this, you'll probably see some "failures" because of entities; that's ok! 
