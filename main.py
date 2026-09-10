import os
import re
import sys
from app import app, db
from models import Patient

def check_folder_writable():
    """Confirm this Windows account can actually write to the app folder.

    A common failure mode: the folder ends up inside a *different*
    Windows account's profile (e.g. C:\\Users\\SomeoneElse\\kidsclinic)
    rather than a shared location. Windows locks each profile folder to
    its own account, so whoever is logged in today gets silently denied
    - which otherwise surfaces as a raw SQLite "readonly database"
    traceback with no server ever starting. Catch it up front instead.
    """
    folder = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(folder, '.write_test.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except OSError:
        print('=' * 64)
        print('  ERROR: Cannot write to the clinic folder.')
        print('=' * 64)
        print(f'  Folder: {folder}')
        print()
        print('  Two common causes:')
        print('   1. clinic.db has the Windows "Read-only" file attribute')
        print('      set - right-click it -> Properties -> untick')
        print('      Read-only -> Apply.')
        print('   2. This folder is inside a DIFFERENT Windows user\'s')
        print('      profile than the account you are logged in as now.')
        print('      Move the whole folder to a neutral location such as')
        print('      C:\\KidsClinic (not inside C:\\Users\\...), then')
        print('      re-run install_server.bat.')
        print('=' * 64)
        return False

def _tc(s):
    """Lowercase everything, then capitalize after start/whitespace/punctuation."""
    if not s:
        return s
    return re.sub(r'(^|[\s,.\-/\\])([a-z])', lambda m: m.group(1) + m.group(2).upper(), s.lower())

def migrate_title_case():
    """One-time idempotent migration: title-case all patient name/address fields."""
    with app.app_context():
        patients = Patient.query.all()
        changed = 0
        for p in patients:
            new_name    = _tc(p.full_name)
            new_parent  = _tc(p.parent_name)
            new_address = _tc(p.address)
            if new_name != p.full_name or new_parent != p.parent_name or new_address != p.address:
                p.full_name   = new_name
                p.parent_name = new_parent
                p.address     = new_address
                changed += 1
        if changed:
            db.session.commit()
            print(f'[STARTUP] Title-cased {changed} patient record(s).')

if __name__ == '__main__':
    if not check_folder_writable():
        input('Press Enter to exit...')
        sys.exit(1)
    migrate_title_case()
    app.run(host='0.0.0.0', port=5000, debug=False)
