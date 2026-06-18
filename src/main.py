from config import log
from extract import extract_all
from transform import transform_all, check_referential_integrity
from load import load_to_dwh


def main():
    dq_errors = []
    log.info("Starting ETL process")
    raw_data = extract_all()
    clean_data = transform_all(raw_data, dq_errors)
    check_referential_integrity(clean_data, dq_errors)
    log.info(f"\nData Quality Summary: {len(dq_errors)} issues found")
    for e in dq_errors:
        log.warning(
            f"[{e['source_table']}] id={e['record_id']} "
            f"| {e['error_type']}: {e['error_detail']}"
        )
    load_to_dwh(clean_data, dq_errors)
    log.info("ETL process completed")


if __name__ == "__main__":
    main()
