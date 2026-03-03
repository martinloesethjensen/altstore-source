import json
import os
import sys
from datetime import datetime

# Define the source identifier as a constant for consistency
# This must match what is in your apps.json
SOURCE_ID = "dev.martin.apps"


def update_json(app_id, version, download_url, size):
    try:
        with open("apps.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: apps.json not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: apps.json is not valid JSON.")
        sys.exit(1)

    # 1. Verify/Update the top-level source identifier
    # AltStore uses this to uniquely track your source
    if "identifier" not in data or data["identifier"] != SOURCE_ID:
        data["identifier"] = SOURCE_ID
        print(f"Updated source identifier to {SOURCE_ID}")

    found_app = False
    clean_version = version.lstrip("v")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # AltStore requires the size to be an integer (bytes)
    try:
        size_int = int(size)
    except ValueError:
        print(f"Error: Size '{size}' is not an integer.")
        sys.exit(1)

    for app in data["apps"]:
        if app["bundleIdentifier"] == app_id:
            found_app = True

            # Create the new version entry
            new_version_entry = {
                "version": clean_version,
                "date": current_date,
                "localizedDescription": f"Update to {version}",
                "downloadURL": download_url,
                "size": size_int,
            }

            # 2. MANDATORY: Update top-level app fields for compatibility
            # AltStore relies on these for quick lookups of the latest version
            app["version"] = new_version_entry["version"]
            app["versionDate"] = new_version_entry["date"]
            app["versionDescription"] = new_version_entry["localizedDescription"]
            app["downloadURL"] = new_version_entry["downloadURL"]
            app["size"] = new_version_entry["size"]

            # 3. Handle the versions array (plural)
            if "versions" not in app:
                app["versions"] = []

            # Check if this exact version number is already present in the history
            version_exists = any(
                v["version"] == new_version_entry["version"] for v in app["versions"]
            )

            if not version_exists:
                # Prepend to the versions array
                # AltStore treats the first item as the latest
                app["versions"].insert(0, new_version_entry)
                print(f"Prepended version {clean_version} to history for {app_id}.")
            else:
                # If it exists (e.g., a re-release), just update the existing top entry
                # This logic assumes the array is properly sorted (latest first)
                if app["versions"][0]["version"] == clean_version:
                    app["versions"][0] = new_version_entry
                    print(
                        f"Updated existing top-level version {clean_version} entry for {app_id}."
                    )
                else:
                    print(
                        f"Warning: Version {clean_version} already exists in history but is not the latest. Skipping prepend."
                    )

            # 4. Update the News section to highlight this release
            # AltStore displays this as a featured banner
            new_announcement = {
                "title": f"{app['name']} {version} Released!",
                # Unique identifier for this news item
                "identifier": f"update-{app_id}-{clean_version}",
                "caption": f"Version {version} of {app['name']} is now available. Check out the new features!",
                "date": current_date,
                # Link this news directly to the app's page
                "appID": app_id,
                # Tint color for the UI (FF5733 is orange/red)
                "tintColor": "FF5733",
                # The notification flag can trigger a push style notice
                "notify": True,
            }

            # This keeps only the single latest announcement.
            # You can append instead if you want a history of news.
            data["news"] = [new_announcement]
            print(f"Updated News section for {app_id} {version}.")

            break

    if not found_app:
        print(f"Error: App with bundleIdentifier '{app_id}' not found in apps.json.")
        sys.exit(1)

    # Save the modified JSON with indentation for readability
    with open("apps.json", "w") as f:
        json.dump(data, f, indent=2)
        # Ensure a trailing newline for Git compatibility
        f.write("\n")
    print("Successfully updated apps.json.")


if __name__ == "__main__":
    # Expects 4 arguments: app_id, version, download_url, size
    if len(sys.argv) != 5:
        print("Usage: python update_json.py <app_id> <version> <download_url> <size>")
        sys.exit(1)
    update_json(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
