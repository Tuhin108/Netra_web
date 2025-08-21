import sys
import os

from ui.app import MainApp
from custom_platform.android_bridge import AndroidHandler

def main():
    """
    Application entrypoint for Android.
    """
    url_to_scan = None
    platform_handler = None

    try:
        handler = AndroidHandler()
        url_to_scan = handler.get_url_from_intent()
        platform_handler = handler
        print(f"Android platform detected. URL to scan: {url_to_scan}")
    except Exception as e:
        print(f"Could not initialize Android handler: {e}")
        # Fallback for testing on desktop
        if len(sys.argv) > 1:
            url_to_scan = sys.argv[1]
        print("Running in desktop test mode.")

    # For testing purposes, if no URL is provided, use a default one.
    if not url_to_scan:
        url_to_scan = "https://www.google.com"
        print(f"No URL provided, using test URL: {url_to_scan}")

    app = MainApp(url_to_scan=url_to_scan, platform_handler=platform_handler)
    app.run()

if __name__ == '__main__':
    main()
