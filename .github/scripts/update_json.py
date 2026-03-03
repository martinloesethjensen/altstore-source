import json
import os
import sys
from datetime import datetime


def update_json(app_id, version, download_url, size):
    with open("apps.json", "r") as f:
        data = json.load(f)

    found = False
    for app in data["apps"]:
        if app["bundleIdentifier"] == app_id:
            # Create the new version entry
            new_version = {
                "version": version.lstrip("v"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "localizedDescription": f"Update to {version}",
                "downloadURL": download_url,
                "size": int(size),
            }

            # 1. Update top-level fields for compatibility
            app["version"] = new_version["version"]
            app["versionDate"] = new_version["date"]
            app["versionDescription"] = new_version["localizedDescription"]
            app["downloadURL"] = new_version["downloadURL"]
            app["size"] = new_version["size"]

            # 2. Prepend to versions array (if it exists)
            if "versions" not in app:
                app["versions"] = []

            # Avoid duplicate versions
            if not any(v["version"] == new_version["version"] for v in app["versions"]):
                app["versions"].insert(0, new_version)

            found = True
            break

    if not found:
        print(f"App with ID {app_id} not found in apps.json")
        sys.exit(1)

    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    update_json(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
