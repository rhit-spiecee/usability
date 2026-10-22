A small web app for managing a contact list. You can add, edit, and delete contacts, and delete several at once.
## Run it
You need Python 3.9 or newer. From the project folder in PowerShell:
git checkout -b <your-rose-hulman-username>

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

Visit http://localhost:5000

The SQLite database (`contacts.db`) is created and filled with sample contacts on first run. 
To reset the data, stop the app and run `Remove-Item contacts.db`.