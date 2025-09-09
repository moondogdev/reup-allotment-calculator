import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import webbrowser
import sys, os

# Import the core calculation logic from our other file
from reup_calculator import calculate_purchase_for_cycle

class Tooltip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"), wraplength=250)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class ReUpApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Theme Data ---
        self.themes = {
            "light": {
                "bg": "#F0F0F0", "fg": "black", "entry_bg": "white", "tree_bg": "white", "tree_fg": "black", "highlight": "lightblue", "link_fg": "blue"
            },
            "dark": {
                "bg": "#2E2E2E", "fg": "white", "entry_bg": "#555555", "tree_bg": "#3C3C3C", "tree_fg": "white", "highlight": "#00405A", "link_fg": "#58A6FF"
            }
        }
        self.theme_var = tk.StringVar(value="light")


        # --- Dispensary Data ---
        self.dispensaries = {
            "Sunnyside": "https://www.sunnyside.shop",
            "Curaleaf": "https://curaleaf.com",
            "Trulieve": "https://www.trulieve.com"
        }

        # --- Window Setup ---
        self.title("ReUp v0.1")
        self.geometry("450x720")
        self.resizable(False, False)
        try:
            # Set the window icon. This is separate from the .exe icon.
            self.iconbitmap(resource_path('reup_icon.ico'))
        except tk.TclError:
            print("Icon file 'reup_icon.ico' not found. Skipping.")

        # --- Style ---
        style = ttk.Style(self)
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"))
        style.configure("TEntry", font=("Helvetica", 10))

        # --- Main Frame ---
        self.main_frame = ttk.Frame(self, padding="15 15 15 15")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=1)

        # --- Load Config and Set Variables ---
        config = self._load_config()
        self.allotment_var = tk.StringVar(value=config.get("allotment", "3.25"))
        self.theme_var.set(config.get("theme", "light"))
        self.start_date_var = tk.StringVar(value=config.get("start_date", datetime.date.today().strftime('%Y-%m-%d')))

        # --- Input Fields ---
        # Allotment        
        allotment_label_frame = ttk.Frame(self.main_frame)
        allotment_label_frame.grid(row=0, column=0, columnspan=2, sticky="w")
        
        ttk.Label(allotment_label_frame, text="Total 35-Day Allotment (oz):").pack(side="left")
        self.allotment_tooltip_label = ttk.Label(allotment_label_frame, text="What is this?", cursor="hand2")
        self.allotment_tooltip_label.pack(side="left", padx=5)
        Tooltip(self.allotment_tooltip_label, "Get your 35-day allotment total from the Medical Marijuana Use Registry, your doctor, or the dispensary if you are unsure.")

        self.allotment_entry = ttk.Entry(self.main_frame, textvariable=self.allotment_var)
        self.allotment_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 10))

        # Start Date
        start_date_label_frame = ttk.Frame(self.main_frame)
        start_date_label_frame.grid(row=2, column=0, columnspan=2, sticky="w")

        ttk.Label(start_date_label_frame, text="Cycle Start Date (YYYY-MM-DD):").pack(side="left")
        self.start_date_tooltip_label = ttk.Label(start_date_label_frame, text="What is this?", cursor="hand2")
        self.start_date_tooltip_label.pack(side="left", padx=5)
        Tooltip(self.start_date_tooltip_label, "This is the first day of your 35-day allotment period. You can find this date in the Medical Marijuana Use Registry.")
        self.start_date_entry = ttk.Entry(self.main_frame, textvariable=self.start_date_var)
        self.start_date_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 10))

        # --- Calculate Button ---
        self.calc_button = ttk.Button(self.main_frame, text="ReUp", command=self.get_recommendation)
        self.calc_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10,5))

        # --- Result Display ---
        self.result_var = tk.StringVar(value="Enter your details and click the button")
        self.result_label = ttk.Label(self.main_frame, textvariable=self.result_var, font=("Helvetica", 11, "bold"), wraplength=400, justify="center")
        self.result_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 5))

        # --- Full Plan Display (Treeview) ---
        columns = ('week', 'units', 'grams')
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=5)
        self.tree.heading('week', text='Week')
        self.tree.heading('units', text='8ths to Buy')
        self.tree.heading('grams', text='Grams')
        self.tree.column('week', width=80, anchor='center')
        self.tree.column('units', width=120, anchor='center')
        self.tree.column('grams', width=120, anchor='center')
        
        # Tag for highlighting the current week
        self.tree.tag_configure('current_week', font=('Helvetica', 10, 'bold'))
        
        self.tree.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(5, 10))

        # --- Details Section ---
        details_frame = ttk.LabelFrame(self.main_frame, text="Details", padding="10")
        details_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        details_frame.columnconfigure(0, weight=1)

        self.details_grams_var = tk.StringVar(value="Total Grams in Allotment: -")
        self.details_grams_label = ttk.Label(details_frame, textvariable=self.details_grams_var)
        self.details_grams_label.grid(row=0, column=0, sticky="w")

        self.details_purchased_var = tk.StringVar(value="Total Grams in Plan: -")
        self.details_purchased_label = ttk.Label(details_frame, textvariable=self.details_purchased_var)
        self.details_purchased_label.grid(row=1, column=0, sticky="w")
        self.details_leftover_var = tk.StringVar(value="Grams Left Unused: -")
        self.details_leftover_label = ttk.Label(details_frame, textvariable=self.details_leftover_var)
        self.details_leftover_label.grid(row=2, column=0, sticky="w")

        # --- Dispensary Section ---
        dispensary_frame = ttk.LabelFrame(self.main_frame, text="Dispensary Quick Shop", padding="10")
        dispensary_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        dispensary_frame.columnconfigure(0, weight=3)
        dispensary_frame.columnconfigure(1, weight=1)
        
        self.dispensary_var = tk.StringVar()
        self.dispensary_combo = ttk.Combobox(dispensary_frame, textvariable=self.dispensary_var, values=list(self.dispensaries.keys()), state="readonly")
        self.dispensary_combo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        if self.dispensaries:
            self.dispensary_combo.current(0)

        self.shop_button = ttk.Button(dispensary_frame, text="Shop", command=self._open_shop_website)
        self.shop_button.grid(row=0, column=1, sticky="ew")

        # --- Resources Section ---
        resources_frame = ttk.LabelFrame(self.main_frame, text="Resources", padding="10")
        resources_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        resources_frame.columnconfigure(0, weight=1)

        self.mmur_label = ttk.Label(resources_frame, text="Florida MMU Registry", cursor="hand2")
        self.mmur_label.grid(row=0, column=0, sticky="w")
        self.mmur_label.bind("<Button-1>", lambda e: self._open_url("https://mmuregistry.flhealth.gov/"))

        self.norml_label = ttk.Label(resources_frame, text="NORML Florida Chapter", cursor="hand2")
        self.norml_label.grid(row=1, column=0, sticky="w")
        self.norml_label.bind("<Button-1>", lambda e: self._open_url("https://norml.org/florida/"))

        self.mmjhealth_label = ttk.Label(resources_frame, text="MMJ Health", cursor="hand2")
        self.mmjhealth_label.grid(row=2, column=0, sticky="w")
        self.mmjhealth_label.bind("<Button-1>", lambda e: self._open_url("https://mmjhealth.com/"))

        # --- Footer and Theme Toggle ---
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        footer_frame.columnconfigure(1, weight=1) # Allow center column to expand

        self.theme_button = ttk.Button(footer_frame, text="\u263C", width=3, command=self._toggle_theme)
        self.theme_button.grid(row=0, column=0, sticky="w")

        # Privacy & Terms Link
        self.privacy_label = ttk.Label(footer_frame, text="Privacy & Terms", foreground="grey", cursor="hand2")
        self.privacy_label.grid(row=0, column=1, sticky="w", padx=10)
        # Using a placeholder URL, you can change this to the correct one.
        self.privacy_label.bind("<Button-1>", lambda e: self._open_url("https://moondogdevelopment.com/privacy"))

        current_year = datetime.date.today().year
        footer_text = f"© {current_year} Moondog Development"
        self.footer_label = ttk.Label(footer_frame, text=footer_text, cursor="hand2")
        self.footer_label.grid(row=0, column=2, sticky="e")
        self.footer_label.bind("<Button-1>", lambda e: self._open_url("https://moondogdevelopment.com"))

        # --- Protocol for saving on close ---
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Apply initial theme ---
        self._apply_theme()

        # Force the UI to draw itself and process pending events.
        self.update_idletasks()
        # Now that the UI is ready, run the initial calculation.
        self.get_recommendation()

    def get_recommendation(self, event=None): # Add event=None to handle button clicks
        self.tree.delete(*self.tree.get_children()) # Clear previous results
        try:
            allotment_oz = float(self.allotment_var.get())
            start_date = self.start_date_var.get()

            recommendation = calculate_purchase_for_cycle(allotment_oz, start_date)

            if "error" in recommendation: # Handle errors from the calculator
                raise ValueError(recommendation["error"])

            # Update the details section
            self.details_grams_var.set(f"Total Grams in Allotment: {recommendation['total_allotment_grams']:.2f}g")
            self.details_purchased_var.set(f"Total Grams in Plan: {recommendation['total_grams_purchased_in_cycle']:.2f}g")
            
            leftover_grams = recommendation['grams_leftover_at_end_of_cycle']
            leftover_text = f"Grams Left Unused: {leftover_grams:.2f}g"
            # if leftover_grams >= 1.0:
            #     leftover_text += " (Buy a 1g Pre-Roll!)"
            self.details_leftover_var.set(leftover_text)

            # Populate the 5-week plan
            for week_plan in recommendation['full_5_week_plan']:
                tags = ()
                if recommendation.get("current_week_recommendation") and week_plan['week'] == recommendation['current_week_recommendation']['week']:
                    tags = ('current_week',)
                self.tree.insert('', tk.END, values=(week_plan['week'], week_plan['units_to_buy'], f"{week_plan['grams_to_buy']:.2f}g"), tags=tags)

            # Update the summary text
            current_rec = recommendation.get("current_week_recommendation")
            if current_rec:
                units = current_rec['units_to_buy']
                self.result_var.set(f"8ths to Purchase this week: {units}")
            else:
                self.result_var.set("You are outside the 35-day cycle.")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            self.result_var.set("Calculation failed. Check inputs.")

    def _open_shop_website(self):
        selected_dispensary = self.dispensary_var.get()
        if not selected_dispensary:
            messagebox.showwarning("No Selection", "Please select a dispensary from the list.")
            return
        
        url = self.dispensaries.get(selected_dispensary)
        webbrowser.open_new_tab(url)

    def _open_url(self, url):
        webbrowser.open_new_tab(url)

    def _load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} # Return empty dict if file doesn't exist or is invalid

    def _on_closing(self):
        config_data = {
            "allotment": self.allotment_var.get(),
            "start_date": self.start_date_var.get(),
            "theme": self.theme_var.get()
        }
        with open("config.json", "w") as f:
            json.dump(config_data, f, indent=4)
        self.destroy()

    def _toggle_theme(self):
        if self.theme_var.get() == "light":
            self.theme_var.set("dark")
        else:
            self.theme_var.set("light")
        self._apply_theme()

    def _apply_theme(self):
        theme_name = self.theme_var.get()
        colors = self.themes[theme_name]

        # Update button icon
        self.theme_button.config(text="\u263D" if theme_name == "light" else "\u263C")

        # Configure root window and frames
        self.config(bg=colors["bg"])
        self.main_frame.config(style="TFrame")
        
        # Configure styles for all widgets
        style = ttk.Style(self)
        style.theme_use('clam') # Use a theme that allows for more customization

        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TLabelframe", background=colors["bg"], bordercolor=colors["fg"])
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])

        # Configure complex widgets like Entry, Button, and Combobox
        style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["fg"], insertcolor=colors["fg"], borderwidth=0)
        style.configure("TButton", foreground=colors["fg"], background=colors["entry_bg"], borderwidth=0)
        style.map("TButton", background=[('active', colors["highlight"])])
        style.configure("TCombobox", foreground=colors["fg"])
        style.map("TCombobox", fieldbackground=[('readonly', colors["entry_bg"])], selectbackground=[('readonly', colors["entry_bg"])], selectforeground=[('readonly', colors["fg"])])

        # Update special link labels
        self.allotment_tooltip_label.config(foreground=colors["link_fg"])
        self.start_date_tooltip_label.config(foreground=colors["link_fg"])
        self.mmur_label.config(foreground=colors["link_fg"])
        self.norml_label.config(foreground=colors["link_fg"])
        self.mmjhealth_label.config(foreground=colors["link_fg"])
        self.footer_label.config(foreground="grey") # Keep footer subtle
        self.privacy_label.config(foreground="grey") # Keep privacy link subtle

        style.configure("Treeview", background=colors["tree_bg"], fieldbackground=colors["tree_bg"], foreground=colors["tree_fg"])
        self.tree.tag_configure('current_week', background=colors["highlight"], foreground=colors["fg"])

if __name__ == "__main__":
    app = ReUpApp()
    app.mainloop()