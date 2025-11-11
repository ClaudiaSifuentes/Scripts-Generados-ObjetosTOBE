from __future__ import annotations
import argparse
import csv
import random
import string
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List


FINAL_HEADER_LABELS: List[str] = [
	"Account Currency",
	"Deleted",
	"Cuenta de socio",
	"Important",
	"Account Name",
	"Afiliado al RDE",
	"Reparto Digital",
	"Suscripción Recibo Digital",
	"Sín Reparto Recibo FiSíco",
	"Tiene Contactos Relacionados",
	"¿Es autoridad?",
	"Es Influyente",
	"Es Municipalidad",
	"Directory Listed",
	"Foreign Exchange",
	"Gaming or Gambling",
	"Money Lending/Pawning",
	"Enable Autopay",
	"Fraud",
	"Is Person Account",
	"Is Root Resolved",
]

LABEL_TO_API: Dict[str, str] = {
	"Account Currency": "CurrencyIsoCode",
	"Deleted": "IsDeleted",
	"Cuenta de socio": "IsPartner",
	"Important": "IsPriorityRecord",
	"Account Name": "Name",
	"Afiliado al RDE": "pz_AffiliatedRDE__c",
	"Reparto Digital": "pz_DigitalCast__c",
	"Suscripción Recibo Digital": "pz_DigitalReceiptSubscription__c",
	"Sín Reparto Recibo FiSíco": "pz_DistributionPhysicalMoney__c",
	"Tiene Contactos Relacionados": "pz_HasRelatedContacts__c",
	"¿Es autoridad?": "pz_IsAuthority__c",
	"Es Influyente": "pz_isInfluential__c",
	"Es Municipalidad": "pz_isMunicipality__c",
	"Directory Listed": "vlocity_cmt__DirectoryListed__c",
	"Foreign Exchange": "vlocity_cmt__Disclosure1__c",
	"Gaming or Gambling": "vlocity_cmt__Disclosure2__c",
	"Money Lending/Pawning": "vlocity_cmt__Disclosure3__c",
	"Enable Autopay": "vlocity_cmt__EnableAutopay__c",
	"Fraud": "vlocity_cmt__HasFraud__c",
	"Is Person Account": "vlocity_cmt__IsPersonAccount__c",
	"Is Root Resolved": "vlocity_cmt__IsRootResolved__c",
}


def bool_str(p_true: float = 0.2) -> str:
	return "true" if random.random() < p_true else "false"


def pick_currency() -> str:
	return random.choices(["PEN"])[0]


FIRST_NAMES = [
	"ANA",
	"GENUINE",
	"JUAN",
	"MARIA",
	"JORGE",
	"LUIS",
	"CARLOS",
	"SONIA",
	"ELENA",
]

COMPANY_SUFFIX = ["SAC", "S.R.L.", "SA", "LLC", "GMBH", "CORP"]


def account_name(i: int) -> str:
	if random.random() < 0.45:
		name = f"{random.choice(FIRST_NAMES)} {random.choice(FIRST_NAMES)} {random.choice(FIRST_NAMES)}"
		return name.title()
	else:
		return f"{random.choice(FIRST_NAMES).title()} {random.choice(COMPANY_SUFFIX)}"


def gen_row(i: int) -> Dict[str, str]:

	row: Dict[str, str] = {}
	row["Account Currency"] = pick_currency()
	row["Deleted"] = "false" if random.random() < 0.98 else "true"
	row["Cuenta de socio"] = bool_str(0.08)
	row["Important"] = bool_str(0.05)
	row["Account Name"] = account_name(i)
	row["Afiliado al RDE"] = bool_str(0.05)
	row["Reparto Digital"] = bool_str(0.35)
	row["Suscripción Recibo Digital"] = bool_str(0.30)
	row["Sín Reparto Recibo FiSíco"] = bool_str(0.20)
	row["Tiene Contactos Relacionados"] = bool_str(0.25)
	row["¿Es autoridad?"] = bool_str(0.02)
	row["Es Influyente"] = bool_str(0.04)
	row["Es Municipalidad"] = bool_str(0.01)
	row["Directory Listed"] = bool_str(0.15)
	row["Foreign Exchange"] = bool_str(0.03)
	row["Gaming or Gambling"] = bool_str(0.01)
	row["Money Lending/Pawning"] = bool_str(0.01)
	row["Enable Autopay"] = bool_str(0.12)
	row["Fraud"] = bool_str(0.005)
	row["Is Person Account"] = bool_str(0.25)
	row["Is Root Resolved"] = bool_str(0.02)

	return row


def main(argv: List[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Generate example Account CSV with LABEL headers")
	parser.add_argument("--n", "-n", type=int, default=100, help="number of rows to generate")
	parser.add_argument("--out", "-o", type=str, default="accounts.csv", help="output CSV file")
	parser.add_argument("--seed", type=int, help="random seed (optional)")
	args = parser.parse_args(argv)

	if args.seed is not None:
		random.seed(args.seed)

	rows = [gen_row(i) for i in range(1, args.n + 1)]

	out_arg = Path(args.out)
	script_dir = Path(__file__).resolve().parent
	repo_scripts_dir = script_dir.parent
	default_outputs_dir = repo_scripts_dir / "outputs"
	default_outputs_dir.mkdir(parents=True, exist_ok=True)

	if out_arg.parent == Path('.'):
		out_path = default_outputs_dir / out_arg.name
	else:
		out_path = out_arg

	with open(out_path, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=FINAL_HEADER_LABELS, extrasaction="ignore")
		writer.writeheader()
		for r in rows:
			writer.writerow(r)

	print(f"Wrote {len(rows)} records to {out_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

