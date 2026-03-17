#!/usr/bin/env python3
"""
OSINT Tool GUI Interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import sys

class OSINTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced OSINT Tool")
        self.root.geometry("900x700")
        
        # Variables
        self.target_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.groq_key_var = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Target input
        ttk.Label(main_frame, text="Target (Domain/IP):").grid(row=0, column=0, sticky=tk.W, pady=5)
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=50)
        target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Output file
        ttk.Label(main_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Groq API Key
        ttk.Label(main_frame, text="Groq API Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        groq_entry = ttk.Entry(main_frame, textvariable=self.groq_key_var, width=50, show="*")
        groq_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        scan_btn = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan)
        scan_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear Output", command=self.clear_output)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_scan)
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Output area
        ttk.Label(main_frame, text="Output:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            main_frame, 
            width=80, 
            height=25,
            wrap=tk.WORD
        )
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Set default output file
        self.output_var.set("osint_results.txt")
        
    def start_scan(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target")
            return
        
        output_file = self.output_var.get().strip()
        groq_key = self.groq_key_var.get().strip()
        
        # Build command
        cmd = [sys.executable, "/home/aliz/advanced_osint_tool_v2.py", target]
        
        if output_file:
            cmd.extend(["-o", output_file])
        
        if groq_key:
            cmd.extend(["--groq-key", groq_key])
        
        # Disable scan button
        self.progress.start(10)
        
        # Run in thread
        thread = threading.Thread(target=self.run_scan, args=(cmd,))
        thread.daemon = True
        thread.start()
        
    def run_scan(self, cmd):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                self.root.after(0, self.append_output, line)
            
            process.wait()
            
            self.root.after(0, self.scan_complete, process.returncode)
            
        except Exception as e:
            self.root.after(0, self.append_output, f"Error: {str(e)}\n")
            self.root.after(0, self.scan_complete, 1)
    
    def append_output(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
    
    def scan_complete(self, returncode):
        self.progress.stop()
        if returncode == 0:
            self.append_output("\nScan completed successfully!\n")
        else:
            self.append_output(f"\nScan failed with return code: {returncode}\n")
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def stop_scan(self):
        # This would need more complex implementation to actually stop the process
        self.progress.stop()
        self.append_output("\nStop requested...\n")

def main():
    root = tk.Tk()
    app = OSINTGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
