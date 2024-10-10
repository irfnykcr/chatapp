
# file to text
This project is for chatting without logging. This app does not store any data. Data that stored in memory is encrypted.

## why

Just trying things. This app is not safe to use.

## Run Locally

Go to the project directory
```bash
cd chatapp
```

Add required modules and libraries
```bash
python -m pip install -r requirements.txt
```

Configure the script && Change the key
```bash
cd config
vim config.json
*make changes*
vim key.key
*change key*
cd ..
```

Run the server
```bash
python test_server.py
```
Run the script
```bash
python tui.py
```