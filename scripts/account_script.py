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
	"pz_ExternalAccountId__c",
	"Account Currency",
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
	"pz_ExternalAccountId__c": "pz_ExternalAccountId__c",
	"Legacy_Contact_Id__c": "Legacy_Contact_Id__c",
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

LABEL_TO_API["Legacy Contact Id"] = "Legacy_Contact_Id__c"

API_HEADER_NAMES: List[str] = [LABEL_TO_API[label] for label in FINAL_HEADER_LABELS]


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


def gen_row(i: int, used_ext_ids=None) -> Dict[str, str]:

	row: Dict[str, str] = {}
	while True:
		num = random.randint(0, 99999999)
		if used_ext_ids is None or num not in used_ext_ids:
			if used_ext_ids is not None:
				used_ext_ids.add(num)
			row[LABEL_TO_API["pz_ExternalAccountId__c"]] = f"ACCOUNT00{num:08d}"
			break
	row[LABEL_TO_API["Account Currency"]] = pick_currency()
	row[LABEL_TO_API["Deleted"]] = "false" if random.random() < 0.98 else "true"
	row[LABEL_TO_API["Cuenta de socio"]] = bool_str(0.08)
	row[LABEL_TO_API["Important"]] = bool_str(0.05)
	row[LABEL_TO_API["Account Name"]] = account_name(i)
	row[LABEL_TO_API["Afiliado al RDE"]] = bool_str(0.05)
	row[LABEL_TO_API["Reparto Digital"]] = bool_str(0.35)
	row[LABEL_TO_API["Suscripción Recibo Digital"]] = bool_str(0.30)
	row[LABEL_TO_API["Sín Reparto Recibo FiSíco"]] = bool_str(0.20)
	row[LABEL_TO_API["Tiene Contactos Relacionados"]] = bool_str(0.25)
	row[LABEL_TO_API["¿Es autoridad?"]] = bool_str(0.02)
	row[LABEL_TO_API["Es Influyente"]] = bool_str(0.04)
	row[LABEL_TO_API["Es Municipalidad"]] = bool_str(0.01)
	row[LABEL_TO_API["Directory Listed"]] = bool_str(0.15)
	row[LABEL_TO_API["Foreign Exchange"]] = bool_str(0.03)
	row[LABEL_TO_API["Gaming or Gambling"]] = bool_str(0.01)
	row[LABEL_TO_API["Money Lending/Pawning"]] = bool_str(0.01)
	row[LABEL_TO_API["Enable Autopay"]] = "false"
	row[LABEL_TO_API["Fraud"]] = bool_str(0.005)
	row[LABEL_TO_API["Is Person Account"]] = bool_str(0.25)
	row[LABEL_TO_API["Is Root Resolved"]] = bool_str(0.02)

	return row


def main(argv: List[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="Generate example Account CSV with API-name headers")
	parser.add_argument("--n", "-n", type=int, default=100, help="number of rows to generate")
	parser.add_argument("--out", "-o", type=str, default="accounts.csv", help="output CSV file")
	parser.add_argument("--seed", type=int, help="random seed (optional)")
	args = parser.parse_args(argv)

	if args.seed is not None:
		random.seed(args.seed)

	used_ids = set()
	rows = [gen_row(i, used_ids) for i in range(1, args.n + 1)]

	out_arg = Path(args.out)
	script_dir = Path(__file__).resolve().parent
	repo_scripts_dir = script_dir.parent
	default_outputs_dir = repo_scripts_dir / "outputs"
	default_outputs_dir.mkdir(parents=True, exist_ok=True)

	if out_arg.parent == Path('.'):
		out_path = default_outputs_dir / out_arg.name
	else:
		out_path = out_arg

	try:
		with open(out_path, "w", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=API_HEADER_NAMES, extrasaction="ignore")
			writer.writeheader()
			for r in rows:
				writer.writerow({k: r.get(k, "") for k in API_HEADER_NAMES})

		print(f"Wrote {len(rows)} records to {out_path}")
	except PermissionError:
		try:
			print(f"PermissionError writing to {out_path}")
			print(f"- Exists: {out_path.exists()}")
			print(f"- Is symlink/junction: {out_path.is_symlink()}")
			try:
				print(f"- Writable by process (os.access): {os.access(out_path, os.W_OK)}")
			except Exception:
				pass
		except Exception:
			pass

		timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
		alt_in_outputs = out_path.with_name(f"{out_path.stem}_{timestamp}{out_path.suffix}")
		try:
			with open(alt_in_outputs, "w", newline="", encoding="utf-8") as f:
				writer = csv.DictWriter(f, fieldnames=API_HEADER_NAMES, extrasaction="ignore")
				writer.writeheader()
				for r in rows:
					writer.writerow({k: r.get(k, "") for k in API_HEADER_NAMES})
			print(f"Wrote {len(rows)} records to {alt_in_outputs} (timestamped fallback in outputs)")
			return
		except PermissionError:
			pass

		fallback = Path.cwd() / out_arg.name
		try:
			with open(fallback, "w", newline="", encoding="utf-8") as f:
				writer = csv.DictWriter(f, fieldnames=API_HEADER_NAMES, extrasaction="ignore")
				writer.writeheader()
				for r in rows:
					writer.writerow({k: r.get(k, "") for k in API_HEADER_NAMES})
			print(f"Wrote {len(rows)} records to {fallback} (final fallback due to PermissionError writing to {out_path})")
		except Exception as e:
			print(f"Failed to write CSV to {out_path}, {alt_in_outputs}, and fallback {fallback}: {e}")
			raise
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

