import re
from app import app, db
from models import Patient

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
    migrate_title_case()
    app.run(host='0.0.0.0', port=5000, debug=False)
