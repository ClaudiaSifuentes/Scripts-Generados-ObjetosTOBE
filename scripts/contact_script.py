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
    'Name': 'Name',
    'Partner': 'vlocity_cmt__IsPartner__c',
    'Recibir notificaciones push': 'pz_ReceivePushNotifications__c',
    'Legacy Contact Id': 'Legacy_Contact_Id__c',
}

FINAL_HEADER_LABELS = list(LABEL_TO_API.keys())


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


def gen_row(i: int):
    name = random_person_name()
    owner = sf18()
    created_by = sf18()
    last_modified_by = sf18()

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
        'Name': name,
        'vlocity_cmt__IsPartner__c': bool_str(0.02),
        'pz_ReceivePushNotifications__c': bool_str(0.2),
        'Legacy_Contact_Id__c': f"CONTACT00{ i:08d}",
    }

    final = {}
    for label, api in LABEL_TO_API.items():
        final[label] = row.get(api, '')
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--out', type=str, default='contacts_filtered.csv')
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    random.seed(args.seed)
    rows = [gen_row(i) for i in range(1, args.n + 1)]

    out_arg = Path(args.out)
    script_dir = Path(__file__).resolve().parent
    repo_scripts_dir = script_dir.parent
    default_outputs_dir = repo_scripts_dir / 'outputs'
    default_outputs_dir.mkdir(parents=True, exist_ok=True)

    if out_arg.parent == Path('.'):
        out_path = default_outputs_dir / out_arg.name
    else:
        out_path = out_arg

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FINAL_HEADER_LABELS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in FINAL_HEADER_LABELS})

    print(f"Wrote {len(rows)} records to {out_path}")


if __name__ == '__main__':
    main()