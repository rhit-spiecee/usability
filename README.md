A small web app for managing a contact list. You can add, edit, and delete contacts, and delete several at once.

## Files
- `app.py`: Flask API and SQLite database operations.
- `static/app.js`: Contacts table, buttons, and requests to the API.
- `static/index.html`: Page layout.
- `static/style.css`: Page styling.
- `contacts.db`: Database created when the app first starts.

## Run it
You need Python 3.9 or newer. Clone the repository and open a terminal in the project folder.

Create your own branch first:
```sh
git checkout -b <your-rose-hulman-username>
```

**Windows PowerShell:**
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000 in your browser.

## Reset sample contacts
The SQLite database (`contacts.db`) is created and filled with sample contacts on first run.
To reset the data, stop the app, delete `contacts.db`, and start the app again.

- Windows PowerShell: `Remove-Item contacts.db`
- macOS / Linux: `rm contacts.db`

This removes any contacts or edits you made during testing.
