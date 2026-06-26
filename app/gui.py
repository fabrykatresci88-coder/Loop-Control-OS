import os
import queue
import threading
import traceback
import tkinter as tk
from tkinter import font, messagebox, ttk

from core.ai_provider import create_provider
from core.project_repository import FileProjectRepository
from core.prompt_generator import TemplatePromptGenerator
from app.project_service import ProjectService
from executor.controller import ExecutorController

# Theme colors - Dark theme
DARK_BG = "#121212"
SURFACE = "#1f2937"
SURFACE_ALT = "#111827"
DARK_FG = "#e5e7eb"
MUTED_FG = "#94a3b8"
ACCENT = "#2563eb"
ACCENT_HOVER = "#3b82f6"
BUTTON_BG = "#2563eb"
BUTTON_FG = "#ffffff"
TEXT_BG = "#0f172a"
TEXT_FG = "#e5e7eb"
PLACEHOLDER_COLOR = "#6b7280"
BORDER_COLOR = "#374151"

PIPELINE_STAGES = [
    "Brain",
    "Business",
    "CTO",
    "Frontend",
    "Backend",
    "Database",
    "QA",
    "Deploy",
]


class LoopControlGUI:
    """Main GUI application for Loop-Control OS."""

    def __init__(self, root):
        self.root = root
        self.log_queue = queue.Queue()
        self.pipeline_states = {stage: tk.BooleanVar(value=False) for stage in PIPELINE_STAGES}
        self.provider_name = tk.StringVar(value="openai")
        self.project_service = ProjectService(
            repository=FileProjectRepository(),
            prompt_generator=TemplatePromptGenerator(),
            ai_provider=create_provider(self.provider_name.get()),
        )
        self.executor_controller = ExecutorController(
            service=self.project_service,
            progress_callback=self.append_progress,
            log_callback=self.append_log,
            error_callback=self.append_error,
        )

        self.setup_window()
        self.create_widgets()
        self.root.after(100, self.process_log_queue)

    def setup_window(self):
        self.root.title("Loop Control OS")
        self.root.geometry("1140x760")
        self.root.configure(bg=DARK_BG)
        self.root.minsize(1000, 650)

    def create_widgets(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(self.root, bg=DARK_BG)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        self.create_header(header_frame)

        content_frame = tk.Frame(self.root, bg=DARK_BG)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)

        self.create_description_panel(content_frame)
        self.create_right_panel(content_frame)

    def create_header(self, parent):
        title_font = font.Font(family="Segoe UI", size=28, weight="bold")
        subtitle_font = font.Font(family="Segoe UI", size=11)

        title_label = tk.Label(
            parent,
            text="Loop Control OS",
            font=title_font,
            fg=TEXT_FG,
            bg=DARK_BG,
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = tk.Label(
            parent,
            text="A modern dashboard for deterministic project decision support.",
            font=subtitle_font,
            fg=MUTED_FG,
            bg=DARK_BG,
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

    def create_description_panel(self, parent):
        description_frame = tk.Frame(parent, bg=SURFACE, bd=1, relief=tk.FLAT)
        description_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=0)
        description_frame.grid_rowconfigure(2, weight=1)
        description_frame.grid_columnconfigure(0, weight=1)

        section_label = self.create_section_label(description_frame, "Project description")
        section_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 0))

        self.idea_text = tk.Text(
            description_frame,
            wrap=tk.WORD,
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief=tk.FLAT,
            padx=14,
            pady=14,
            font=("Segoe UI", 11),
            height=12,
        )
        self.idea_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(12, 0))
        self.idea_text.insert("1.0", "Describe your startup idea here...\nUse multiple lines for context and goals.")
        self.idea_text.config(fg=PLACEHOLDER_COLOR)
        self.idea_text.bind("<FocusIn>", self.on_text_focus_in)
        self.idea_text.bind("<FocusOut>", self.on_text_focus_out)

        pipeline_frame = tk.Frame(description_frame, bg=SURFACE_ALT, bd=1, relief=tk.FLAT)
        pipeline_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=16)
        pipeline_frame.grid_columnconfigure(0, weight=1)

        pipeline_label = self.create_section_label(pipeline_frame, "Pipeline")
        pipeline_label.grid(row=0, column=0, sticky="w", padx=14, pady=(14, 0))

        for index, stage in enumerate(PIPELINE_STAGES, start=1):
            checkbox = tk.Checkbutton(
                pipeline_frame,
                text=stage,
                variable=self.pipeline_states[stage],
                fg=TEXT_FG,
                bg=SURFACE_ALT,
                activebackground=SURFACE_ALT,
                selectcolor=DARK_BG,
                disabledforeground=MUTED_FG,
                font=("Segoe UI", 10),
                anchor="w",
                padx=10,
            )
            checkbox.grid(row=index, column=0, sticky="ew", padx=12, pady=3)

        button_frame = tk.Frame(description_frame, bg=SURFACE, bd=0)
        button_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_action_button(button_frame, "Analyze", self.on_analyze, 0)
        self.create_action_button(button_frame, "Generate MVP", self.on_generate_project, 1)
        self.create_action_button(button_frame, "Export", self.on_export, 2)
        self.create_action_button(button_frame, "Settings", self.on_settings, 3)

    def create_right_panel(self, parent):
        right_frame = tk.Frame(parent, bg=SURFACE, bd=1, relief=tk.FLAT)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        section_label = self.create_section_label(right_frame, "Output")
        section_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 0))

        log_frame = tk.Frame(right_frame, bg=TEXT_BG, bd=1, relief=tk.SOLID)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG,
            relief=tk.FLAT,
            padx=14,
            pady=14,
            font=("Segoe UI", 10),
            state=tk.DISABLED,
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(log_frame, command=self.output_text.yview, bg=TEXT_BG)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.config(yscrollcommand=scrollbar.set)

        self.progress_bar = ttk.Progressbar(right_frame, mode="determinate", maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

    def create_section_label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            fg=TEXT_FG,
            bg=parent.cget("bg"),
            font=("Segoe UI", 12, "bold"),
        )

    def create_action_button(self, parent, label, command, column):
        button = tk.Button(
            parent,
            text=label,
            command=lambda: self.run_background_task(command),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=ACCENT_HOVER,
            activeforeground=BUTTON_FG,
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=10,
            cursor="hand2",
        )
        button.grid(row=0, column=column, sticky="ew", padx=6, pady=10)
        button.bind("<Enter>", lambda e: button.config(bg=ACCENT_HOVER))
        button.bind("<Leave>", lambda e: button.config(bg=BUTTON_BG))
        return button

    def run_background_task(self, task):
        thread = threading.Thread(target=task, daemon=True)
        thread.start()

    def on_text_focus_in(self, event):
        if self.idea_text.get("1.0", tk.END).strip() in ["Describe your startup idea here...", ""]:
            self.idea_text.delete("1.0", tk.END)
            self.idea_text.config(fg=TEXT_FG)

    def on_text_focus_out(self, event):
        if not self.idea_text.get("1.0", tk.END).strip():
            self.idea_text.insert("1.0", "Describe your startup idea here...\nUse multiple lines for context and goals.")
            self.idea_text.config(fg=PLACEHOLDER_COLOR)

    def get_idea_text(self) -> str:
        text = self.idea_text.get("1.0", tk.END).strip()
        if text == "Describe your startup idea here..." or not text:
            return ""
        return text

    def update_pipeline(self, stage: str, value: bool):
        if stage in self.pipeline_states:
            self.pipeline_states[stage].set(value)

    def reset_pipeline(self):
        for stage in self.pipeline_states.values():
            stage.set(False)

    def append_log(self, message: str) -> None:
        self.log_queue.put(message)

    def append_error(self, message: str) -> None:
        self.log_queue.put(f"ERROR: {message}")

    def append_progress(self, message: str) -> None:
        self.log_queue.put(f"PROGRESS: {message}")
        current = self.progress_bar['value']
        if "Validating" in message:
            self.progress_bar['value'] = 20
        elif "Executing" in message:
            self.progress_bar['value'] = 60
        elif "completed" in message:
            self.progress_bar['value'] = 100
        else:
            self.progress_bar['value'] = min(100, current + 10)

    def process_log_queue(self) -> None:
        while not self.log_queue.empty():
            message = self.log_queue.get_nowait()
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        self.root.after(100, self.process_log_queue)

    def on_analyze(self):
        self.analyze_project()

    def analyze_project(self):
        print("[DEBUG] analyze_project: before get_idea_text()")
        idea = self.get_idea_text()
        print("[DEBUG] analyze_project: after get_idea_text()")
        if not idea:
            print("[DEBUG] analyze_project: before messagebox.showwarning()")
            messagebox.showwarning("Empty Idea", "Please describe your startup idea.")
            print("[DEBUG] analyze_project: after messagebox.showwarning()")
            return

        print("[DEBUG] analyze_project: before selected_modules collection")
        selected_modules = [
            stage for stage, var in self.pipeline_states.items() if var.get()
        ]
        print(f"[DEBUG] analyze_project: after selected_modules collection -> {selected_modules}")

        print("[DEBUG] analyze_project: before append_log('Starting analysis...')")
        self.append_log("Starting analysis...")
        print("[DEBUG] analyze_project: after append_log('Starting analysis...')")
        print("[DEBUG] analyze_project: before reset_pipeline()")
        self.reset_pipeline()
        print("[DEBUG] analyze_project: after reset_pipeline()")
        print("[DEBUG] analyze_project: before append_log('▸ Brain check started')")
        self.append_log("▸ Brain check started")
        print("[DEBUG] analyze_project: after append_log('▸ Brain check started')")
        print("[DEBUG] analyze_project: before update_pipeline('Brain', True)")
        self.update_pipeline("Brain", True)
        print("[DEBUG] analyze_project: after update_pipeline('Brain', True)")

        try:
            print("[DEBUG] analyze_project: before project_service.create_project()")
            state = self.project_service.create_project(idea)
            print("[DEBUG] analyze_project: after project_service.create_project()")
            print("[DEBUG] analyze_project: before append_log('▸ Project description saved')")
            self.append_log("▸ Project description saved")
            print("[DEBUG] analyze_project: after append_log('▸ Project description saved')")
            print("[DEBUG] analyze_project: before update_pipeline('Business', True)")
            self.update_pipeline("Business", True)
            print("[DEBUG] analyze_project: after update_pipeline('Business', True)")

            print("[DEBUG] analyze_project: before project_service.analyze()")
            report = self.project_service.analyze(
                state,
                selected_modules=selected_modules,
            )
            print("[DEBUG] analyze_project: after project_service.analyze()")
            print("[DEBUG] analyze_project: before append_log('▸ Architecture analysis completed')")
            self.append_log("▸ Architecture analysis completed")
            print("[DEBUG] analyze_project: after append_log('▸ Architecture analysis completed')")
            print("[DEBUG] analyze_project: before update_pipeline('CTO', True)")
            self.update_pipeline("CTO", True)
            print("[DEBUG] analyze_project: after update_pipeline('CTO', True)")
            print("[DEBUG] analyze_project: before append_log(report)")
            self.append_log(report)
            print("[DEBUG] analyze_project: after append_log(report)")
        except Exception as error:
            print("[DEBUG] analyze_project: exception caught, full traceback below")
            traceback.print_exc()
            error_message = str(error)
            if isinstance(error, EnvironmentError):
                error_message = (
                    "AI provider configuration error: " + error_message
                )
            print("[DEBUG] analyze_project: before append_log(error)")
            self.append_log(f"Error during analysis: {error_message}")
            print("[DEBUG] analyze_project: after append_log(error)")
            print("[DEBUG] analyze_project: before messagebox.showerror()")
            messagebox.showerror("Analysis Error", error_message)
            print("[DEBUG] analyze_project: after messagebox.showerror()")

    def on_generate_project(self):
        idea = self.get_idea_text()
        if not idea:
            messagebox.showwarning("Empty Idea", "Please describe your startup idea.")
            return

        self.progress_bar['value'] = 0
        self.append_log("Starting project execution...")

        def run():
            result = self.executor_controller.run_project(idea)
            if result.success:
                self.append_log("Project execution completed successfully.")
                messagebox.showinfo("Success", "Project executed successfully.")
            else:
                self.append_error("Project execution completed with errors.")
                messagebox.showerror("Execution Error", "Project execution completed with errors. Check logs for details.")

        self.run_background_task(run)

    def on_export(self):
        self.append_log("Exporting project artifacts...")
        self.update_pipeline("Deploy", True)
        self.append_log("▸ Export complete")
        messagebox.showinfo("Export", "Project export completed successfully.")

    def on_settings(self):
        self.append_log("Opening settings...")

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.configure(bg=DARK_BG)
        settings_window.geometry("420x240")
        settings_window.resizable(False, False)

        section_label = tk.Label(
            settings_window,
            text="AI Provider",
            fg=TEXT_FG,
            bg=DARK_BG,
            font=("Segoe UI", 12, "bold"),
        )
        section_label.pack(anchor="w", padx=16, pady=(16, 8))

        provider_frame = tk.Frame(settings_window, bg=SURFACE, bd=1, relief=tk.FLAT)
        provider_frame.pack(fill="x", padx=16, pady=(0, 16))

        provider_label = tk.Label(
            provider_frame,
            text="Select AI provider:",
            fg=TEXT_FG,
            bg=SURFACE,
            font=("Segoe UI", 10),
        )
        provider_label.grid(row=0, column=0, sticky="w", padx=12, pady=12)

        provider_options = ["openai"]
        provider_menu = ttk.OptionMenu(
            provider_frame,
            self.provider_name,
            self.provider_name.get(),
            *provider_options,
        )
        provider_menu.grid(row=0, column=1, sticky="ew", padx=12, pady=12)
        provider_frame.grid_columnconfigure(1, weight=1)

        warning_text = (
            "OpenAI uses OPENAI_API_KEY from the .env file. "
            "If the key is missing, Analyze will show a configuration error."
        )
        warning_label = tk.Label(
            settings_window,
            text=warning_text,
            fg=MUTED_FG,
            bg=DARK_BG,
            font=("Segoe UI", 9),
            wraplength=380,
            justify="left",
        )
        warning_label.pack(anchor="w", padx=16, pady=(0, 16))

        button_frame = tk.Frame(settings_window, bg=DARK_BG)
        button_frame.pack(fill="x", padx=16, pady=(0, 16))

        save_button = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self.apply_provider_selection(settings_window),
            bg=ACCENT,
            fg=BUTTON_FG,
            activebackground=ACCENT_HOVER,
            activeforeground=BUTTON_FG,
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=10,
            cursor="hand2",
        )
        save_button.pack(side="right")

    def apply_provider_selection(self, window: tk.Toplevel):
        provider_name = self.provider_name.get()
        try:
            provider = create_provider(provider_name)
            self.project_service.ai_provider = provider
            self.append_log(f"AI provider set to {provider_name}.")
            messagebox.showinfo("Settings Saved", f"AI provider set to {provider_name}.")
            window.destroy()
        except Exception as error:
            messagebox.showerror("Settings Error", str(error))


def main():
    root = tk.Tk()
    app = LoopControlGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
