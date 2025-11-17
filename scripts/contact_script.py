import csv
import random
import string
import argparse
from datetime import datetime, timedelta
import re
from pathlib import Path

LABEL_TO_API = {
    'Active': 'vlocity_cmt__IsActive__c',
    'Asesor': 'pz_Processor__c',
    'Authorized': 'vlocity_cmt__Authorized__c',
    'Cliente Especial': 'pz_SpecialClient__c',
    'Cliente recurrente': 'pz_ReturningCustomer__c',
    'Consentimiento condiciones de privacidad': 'pz_ConsentConditionsAndPrivacy__c',
    'Consentimiento terminos y condiciones': 'pz_ConsentTermsAndConditions__c',
    'Consentimientos para otras finalidades': 'pz_ConsentTermsAditionals__c',
    'Contacto Recurrente': 'pz_RecurringContact__c',
    'Employee': 'vlocity_cmt__IsEmployee__c',
    'Fraud': 'vlocity_cmt__HasFraud__c',
    'Is Person Account': 'vlocity_cmt__IsPersonAccount__c',
    'Marca Legal': 'PZ_LegalBrand__c',
    'Mobile Opt Out': 'et4ae5__HasOptedOutOfMobile__c',
    'Last Name': 'LastName',
    'First Name': 'FirstName',
    'Salutation': 'Salutation',
    'Middle Name': 'MiddleName',
    'Suffix': 'Suffix',
    'Partner': 'vlocity_cmt__IsPartner__c',
    'Recibir notificaciones push': 'pz_ReceivePushNotifications__c',
    'pz_ExternalAccountId__c': 'pz_ExternalAccountId__c'
}

FINAL_HEADER_LABELS = list(LABEL_TO_API.keys())
API_HEADER_NAMES = [LABEL_TO_API[label] for label in FINAL_HEADER_LABELS]


def sf15(n=15):
    cs = string.ascii_letters + string.digits
    return "".join(random.choice(cs) for _ in range(n))


def sf18_from_15(id15: str):
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    suffix = []
    for i in range(3):
        chunk = id15[i*5:(i+1)*5]
        bits = sum(1 for c in chunk if c.isupper())
        suffix.append(base[bits % len(base)])
    return id15 + "".join(suffix)


def sf18():
    return sf18_from_15(sf15())


def bool_str(p=0.5):
    return 'true' if random.random() < p else 'false'


def random_person_name():
    first = random.choice(['Natalia', 'Ana', 'Pedro', 'Luis', 'María', 'Carlos', 'Andrea', 'Jorge', 'Lucia'])
    middle = random.choice(['Lucia', 'Carlos', 'María', 'Rosa', 'Alonso', 'Jose'])
    last = random.choice(['Vargas', 'Perez', 'Gonzalez', 'Ramirez', 'Flores', 'Rojas'])
    return f"{first} {middle} {last}"


def random_person():
    first = random.choice(['Natalia','Ana','Pedro','Luis','María','Carlos','Andrea','Jorge','Lucia'])
    middle = random.choice(['Lucia','Carlos','María','Rosa','Alonso','Jose'])
    last = random.choice(['Vargas','Perez','Gonzalez','Ramirez','Flores','Rojas'])
    return first, middle, last

def gen_row(i: int, used_ext_ids=None, accounts_list=None, unique_accounts=False):
    first, middle, last = random_person()
    salutation = random.choice(['Sr.', 'Sra.', 'Dr.', ''])
    ID_Account = random.choice(['ACCOUNT0000000001', 'ACCOUNT0000000002', 'ACCOUNT0000000003', 'ACCOUNT0000000005', 'ACCOUNT0043464097', 'ACCOUNT0038870700', 'ACCOUNT0010986393', 'ACCOUNT0036230636', 'ACCOUNT0037290936'])
    suffix = random.choice(['', 'Jr.', 'Sr.'])
    name = f"{first} {middle} {last}".strip()

    owner = sf18()
    created_by = sf18()
    last_modified_by = sf18()

    # Determine external account id from picklist if provided, otherwise generate one
    ext_id = ''
    if accounts_list and len(accounts_list) > 0:
        if unique_accounts:
            # pick an unused id if possible
            choices = [a for a in accounts_list if (used_ext_ids is None or a not in used_ext_ids)]
            if choices:
                ext_id = random.choice(choices)
                if used_ext_ids is not None:
                    used_ext_ids.add(ext_id)
            else:
                num = random.randint(0, 99999999)
                if used_ext_ids is not None:
                    used_ext_ids.add(num)
                ext_id = f"ACCOUNT00{num:08d}"
        else:
            ext_id = random.choice(accounts_list)
    else:
        while True:
            num = random.randint(0, 99999999)
            if used_ext_ids is None or num not in used_ext_ids:
                if used_ext_ids is not None:
                    used_ext_ids.add(num)
                ext_id = f"ACCOUNT00{num:08d}"
                break

    row = {
        'vlocity_cmt__IsActive__c': bool_str(0.9),
        'pz_Processor__c': bool_str(0.05),
        'vlocity_cmt__Authorized__c': bool_str(0.2),
        'pz_SpecialClient__c': bool_str(0.05),
        'pz_ReturningCustomer__c': bool_str(0.12),
        'pz_ConsentConditionsAndPrivacy__c': bool_str(0.6),
        'pz_ConsentTermsAndConditions__c': bool_str(0.6),
        'pz_ConsentTermsAditionals__c': bool_str(0.2),
        'pz_RecurringContact__c': bool_str(0.15),
        'vlocity_cmt__IsEmployee__c': bool_str(0.05),
        'vlocity_cmt__HasFraud__c': bool_str(0.03),
        'vlocity_cmt__IsPersonAccount__c': bool_str(0.01),
        'PZ_LegalBrand__c': bool_str(0.02),
        'et4ae5__HasOptedOutOfMobile__c': bool_str(0.05),
        'LastName': last,
        'FirstName': first,
        'Salutation': salutation,
        'MiddleName': middle,
        'Suffix': suffix,
        'Name': name,
        'vlocity_cmt__IsPartner__c': bool_str(0.02),
        'pz_ReceivePushNotifications__c': bool_str(0.2),
        'pz_ExternalAccountId__c': ID_Account
    }

    final = {}
    for label, api in LABEL_TO_API.items():
        final[api] = row.get(api, '')
    return final




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--out', type=str, default='contacts_filtered.csv')
    ap.add_argument('--accounts', type=str, default=None,
                    help='CSV file containing account external IDs to use as a picklist (first column or header pz_ExternalAccountId__c).')
    ap.add_argument('--unique-accounts', action='store_true',
                    help='Pick unique account ids from the picklist (no replacement)')
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)

    out_arg = Path(args.out)
    script_dir = Path(__file__).resolve().parent
    repo_scripts_dir = script_dir.parent
    default_outputs_dir = repo_scripts_dir / 'outputs'
    default_outputs_dir.mkdir(parents=True, exist_ok=True)

    accounts_list = []
    accounts_path = None
    if args.accounts:
        accounts_path = Path(args.accounts)
    else:
        candidate = default_outputs_dir / 'accounts_rows.csv'
        if candidate.exists():
            accounts_path = candidate

    if accounts_path and accounts_path.exists():
        try:
            with open(accounts_path, newline='', encoding='utf-8') as af:
                dr = csv.DictReader(af)
                if 'pz_ExternalAccountId__c' in dr.fieldnames:
                    accounts_list = [r['pz_ExternalAccountId__c'].strip() for r in dr if r.get('pz_ExternalAccountId__c')]
                else:
                    first_field = dr.fieldnames[0]
                    accounts_list = [r[first_field].strip() for r in dr if r.get(first_field)]
        except Exception:
            accounts_list = []

    used_ids = set()
    rows = [gen_row(i, used_ids, accounts_list=accounts_list, unique_accounts=args.unique_accounts) for i in range(1, args.n + 1)]

    if out_arg.parent == Path('.'):
        out_path = default_outputs_dir / out_arg.name
    else:
        out_path = out_arg

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=API_HEADER_NAMES, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in API_HEADER_NAMES})

    print(f"Wrote {len(rows)} records to {out_path}")


if __name__ == '__main__':
    main()