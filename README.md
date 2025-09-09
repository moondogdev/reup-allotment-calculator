# ReUp - Medical Allotment Calculator

ReUp is a simple, user-friendly desktop application designed to help Florida medical marijuana patients manage their 35-day rolling allotment. It takes the guesswork out of purchasing by providing a clear, week-by-week plan to help you stay within your prescribed limits.

Built with Python and Tkinter, this tool aims to provide a straightforward utility for the patient community.

## Who Is This For?

This application is for any medical marijuana patient in Florida who finds it challenging to track their purchases against their 35-day allotment. If you've ever been unsure how much you can buy in a given week without exceeding your limit, ReUp is for you.

## Features

- **Weekly Purchase Plan:** Enter your total allotment and cycle start date to get a 5-week purchasing schedule.
- **Current Week Highlight:** The app automatically identifies the current week in your cycle and highlights your recommended purchase.
- **Allotment Details:** See a breakdown of your total allotment in grams, the total planned purchases, and any leftover amount.
- **Dispensary Quick Links:** Quickly access the websites of popular dispensaries.
- **Light & Dark Modes:** Toggle between themes for your viewing comfort.
- **Persistent Settings:** Your allotment, start date, and theme preference are saved locally for your convenience.

## How to Use

### For Users

1.  Download the `ReUp.exe` file from the Releases page. <!-- Update this link -->
2.  Run the executable. No installation is required.
3.  Enter your **Total 35-Day Allotment** (in ounces) and your **Cycle Start Date**. You can find this information on the Florida MMU Registry.
4.  Click the **"ReUp"** button.
5.  The app will display your recommended purchase for the current week and a full 5-week plan.

### For Developers

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd reup-allotment-calculator
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Run the application:**
    The application uses only standard Python libraries, so no external packages are required.
    ```bash
    python reup_app.py
    ```

## Disclaimer

This tool is for informational and planning purposes only. It is not a substitute for official tracking via the Medical Marijuana Use Registry (MMUR). Always verify your available allotment with the dispensary or the official registry before making a purchase. The developer is not liable for any discrepancies or issues arising from the use of this application.

---

*© 2025 Moondog Development*