import datetime

input_name = "Roger"

# passes the input_name variable into entername.py

exec(open("entername.py").read(), {'datetime': datetime}, {
    'input': lambda prompt: input_name
})