"""Select a stable pseudo-random half-hour slot per day in Asia/Kolkata."""
import hashlib
import os
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def chosen_slot(date_key: str, repository: str) -> int:
    digest = hashlib.sha256(f"{repository}:{date_key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 48

def main() -> None:
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    now = datetime.now(IST)
    slot = chosen_slot(now.strftime("%Y-%m-%d"), os.environ.get("GITHUB_REPOSITORY", "repo"))
    current_slot = now.hour * 2 + (1 if now.minute >= 30 else 0)
    run_now = event == "workflow_dispatch" or current_slot == slot
    selected_time = f"{slot // 2:02d}:{'30' if slot % 2 else '00'} IST"
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"run={'true' if run_now else 'false'}\n")
            handle.write(f"selected_time={selected_time}\n")
            handle.write(f"date={now:%Y-%m-%d}\n")
    print(f"Date (IST): {now:%Y-%m-%d}; selected daily slot: {selected_time}")
    print(f"Workflow event: {event}; execute AI developer: {run_now}")

if __name__ == "__main__":
    main()
