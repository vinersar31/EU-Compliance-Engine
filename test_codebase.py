import sys
import os
from eu_compliance_engine.auditor import audit_codebase

def main():
    print("Running compliance audit on the codebase...")

    # We should exclude the auditor itself and its tests, otherwise it will flag itself!
    # Let's run it specifically on directories while filtering files inside audit_codebase
    # or just filtering the results here.

    # Since audit_codebase doesn't take exclusions, we filter the results manually
    results = audit_codebase(".")

    exclusions = [
        "eu_compliance_engine/auditor.py",
        "tests/test_auditor.py",
        "eu_compliance_engine/compliance_engine.py", # it contains the string 'biometric_scraping' in its definition list
        "test_codebase.py"
    ]

    filtered_red = [f for f in results["FLAG RED"] if not any(exc in f.replace("\\", "/") for exc in exclusions)]
    filtered_yellow = [f for f in results["FLAG YELLOW"] if not any(exc in f.replace("\\", "/") for exc in exclusions)]
    filtered_blue = [f for f in results["FLAG BLUE"] if not any(exc in f.replace("\\", "/") for exc in exclusions)]

    has_errors = False

    if filtered_red:
        print("\n❌ UNACCEPTABLE RISK (FLAG RED) DETECTED:")
        for f in filtered_red:
            print(f"  - {f}")
        has_errors = True

    if filtered_yellow:
        print("\n⚠️ HIGH RISK (FLAG YELLOW) DETECTED:")
        for f in filtered_yellow:
            print(f"  - {f}")

    if filtered_blue:
        print("\nℹ️ TRANSPARENCY OBLIGATION (FLAG BLUE) DETECTED:")
        for f in filtered_blue:
            print(f"  - {f}")

    if not (filtered_red or filtered_yellow or filtered_blue):
        print("\n✅ NO COMPLIANCE ISSUES DETECTED IN APPLICATION LOGIC.")

    if has_errors:
        print("\nCI failed due to prohibited code patterns.")
        sys.exit(1)

    print("\nCompliance audit passed successfully.")

if __name__ == '__main__':
    main()
