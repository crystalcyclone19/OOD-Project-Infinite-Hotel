import sys
import unittest
import csv
import os

RESULT_CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "CSV", "test_functions_csv")
SUMMARY_CSV_PATH = os.path.join(RESULT_CSV_DIR, "overall_summary.csv")

def write_overall_summary(result: unittest.TestResult):
    total   = result.testsRun
    failed  = len(result.failures)
    errored = len(result.errors)
    skipped = len(result.skipped)
    passed  = total - failed - errored - skipped

    # ---- Terminal ----
    sep = "=" * 60
    print(f"\n{sep}")
    print("  Overall Test Summary")
    print(sep)
    print(f"  {'Total tests run':<20}: {total}")
    print(f"  {'Passed':<20}: {passed}")
    print(f"  {'Failed':<20}: {failed}")
    print(f"  {'Errors':<20}: {errored}")
    print(f"  {'Skipped':<20}: {skipped}")
    print(f"  {'Result':<20}: {'OK' if result.wasSuccessful() else 'FAILED'}")
    print(sep)

    # ---- detailed failure/error list ----
    detail_rows = []
    for test, traceback in result.failures:
        detail_rows.append([str(test), "FAILED", traceback.splitlines()[-1]])
    for test, traceback in result.errors:
        detail_rows.append([str(test), "ERROR",  traceback.splitlines()[-1]])

    if detail_rows:
        print("\n  Failed / Error detail:")
        for row in detail_rows:
            print(f"    [{row[1]}] {row[0]}")
            print(f"           {row[2]}")

    print(f"\n  CSV saved at: {SUMMARY_CSV_PATH}\n")

    # ---- CSV ----
    os.makedirs(RESULT_CSV_DIR, exist_ok=True)
    with open(SUMMARY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["total",   total])
        w.writerow(["passed",  passed])
        w.writerow(["failed",  failed])
        w.writerow(["errors",  errored])
        w.writerow(["skipped", skipped])
        w.writerow(["result",  "OK" if result.wasSuccessful() else "FAILED"])
        if detail_rows:
            w.writerow([])
            w.writerow(["test_case", "status", "last_line"])
            w.writerows(detail_rows)


if __name__ == '__main__':
    test_loader = unittest.defaultTestLoader
    test_suite  = test_loader.discover(
        start_dir='test/test_functions', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    write_overall_summary(result)
    sys.exit(not result.wasSuccessful())


