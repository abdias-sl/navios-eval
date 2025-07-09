#!/usr/bin/env python3
"""
Ethereum Balance Checker with GUI
A comprehensive tool to check ETH balances using Web3 with a modern GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import json
import time
from datetime import datetime
import re
from web3 import Web3
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum
import webbrowser

# Configuration and Data Classes
@dataclass
class WalletInfo:
    address: str
    balance: float
    usd_value: float
    last_updated: datetime
    
class NetworkType(Enum):
    MAINNET = "mainnet"
    GOERLI = "goerli"
    SEPOLIA = "sepolia"
    POLYGON = "polygon"
    BSC = "bsc"

class EthereumBalanceChecker:
    """Core class for handling Ethereum balance checking"""
    
    def __init__(self):
        self.networks = {
            NetworkType.MAINNET: {
                "rpc": "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
                "explorer": "https://etherscan.io/address/",
                "name": "Ethereum Mainnet"
            },
            NetworkType.GOERLI: {
                "rpc": "https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
                "explorer": "https://goerli.etherscan.io/address/",
                "name": "Goerli Testnet"
            },
            NetworkType.SEPOLIA: {
                "rpc": "https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
                "explorer": "https://sepolia.etherscan.io/address/",
                "name": "Sepolia Testnet"
            },
            NetworkType.POLYGON: {
                "rpc": "https://polygon-rpc.com",
                "explorer": "https://polygonscan.com/address/",
                "name": "Polygon Mainnet"
            },
            NetworkType.BSC: {
                "rpc": "https://bsc-dataseed.binance.org",
                "explorer": "https://bscscan.com/address/",
                "name": "BSC Mainnet"
            }
        }
        self.current_network = NetworkType.MAINNET
        self.web3 = None
        self.eth_price = 0.0
        
    def connect_to_network(self, network: NetworkType) -> bool:
        """Connect to specified network"""
        try:
            rpc_url = self.networks[network]["rpc"]
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            self.current_network = network
            return self.web3.is_connected()
        except Exception as e:
            print(f"Failed to connect to {network.value}: {e}")
            return False
    
    def validate_address(self, address: str) -> bool:
        """Validate Ethereum address"""
        if not address:
            return False
        
        # Remove any whitespace
        address = address.strip()
        
        # Check if it's a valid hex address
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return False
            
        # Additional Web3 validation
        try:
            return Web3.is_address(address)
        except:
            return False
    
    def get_balance(self, address: str) -> Optional[float]:
        """Get ETH balance for given address"""
        if not self.web3 or not self.web3.is_connected():
            if not self.connect_to_network(self.current_network):
                return None
        
        try:
            # Get balance in Wei
            balance_wei = self.web3.eth.get_balance(address)
            # Convert to ETH
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def get_eth_price(self) -> float:
        """Get current ETH price from CoinGecko API"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                timeout=10
            )
            data = response.json()
            self.eth_price = data['ethereum']['usd']
            return self.eth_price
        except Exception as e:
            print(f"Error fetching ETH price: {e}")
            return 0.0
    
    def get_transaction_count(self, address: str) -> int:
        """Get transaction count for address"""
        if not self.web3 or not self.web3.is_connected():
            return 0
        
        try:
            return self.web3.eth.get_transaction_count(address)
        except:
            return 0
    
    def get_wallet_info(self, address: str) -> Optional[WalletInfo]:
        """Get comprehensive wallet information"""
        if not self.validate_address(address):
            return None
        
        balance = self.get_balance(address)
        if balance is None:
            return None
        
        eth_price = self.get_eth_price()
        usd_value = balance * eth_price
        
        return WalletInfo(
            address=address,
            balance=balance,
            usd_value=usd_value,
            last_updated=datetime.now()
        )

class ModernGUI:
    """Modern GUI interface for the Ethereum Balance Checker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.checker = EthereumBalanceChecker()
        self.wallet_history = []
        self.auto_refresh = False
        self.refresh_interval = 30  # seconds
        
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("Ethereum Balance Checker Pro")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
        # Configure icon (if available)
        try:
            self.root.iconbitmap("ethereum.ico")
        except:
            pass
    
    def create_styles(self):
        """Create modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#2196F3',
            'secondary': '#FFC107',
            'success': '#4CAF50',
            'danger': '#F44336',
            'warning': '#FF9800',
            'info': '#17A2B8',
            'dark': '#343A40',
            'light': '#F8F9FA'
        }
        
        # Configure styles
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))
        style.configure('Success.TLabel', foreground=self.colors['success'])
        style.configure('Danger.TLabel', foreground=self.colors['danger'])
        style.configure('Primary.TButton', font=('Helvetica', 10, 'bold'))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔗 Ethereum Balance Checker Pro", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Network selection
        network_frame = ttk.LabelFrame(main_frame, text="Network Selection", padding="10")
        network_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        network_frame.columnconfigure(1, weight=1)
        
        ttk.Label(network_frame, text="Network:").grid(row=0, column=0, sticky=tk.W)
        self.network_var = tk.StringVar(value="mainnet")
        network_combo = ttk.Combobox(network_frame, textvariable=self.network_var, 
                                   values=["mainnet", "goerli", "sepolia", "polygon", "bsc"],
                                   state="readonly", width=20)
        network_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        network_combo.bind('<<ComboboxSelected>>', self.on_network_change)
        
        # Connection status
        self.status_label = ttk.Label(network_frame, text="● Disconnected", 
                                     style='Danger.TLabel')
        self.status_label.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        
        # Address input
        input_frame = ttk.LabelFrame(main_frame, text="Wallet Address", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(input_frame, textvariable=self.address_var, 
                                      font=('Courier', 11), width=50)
        self.address_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.check_button = ttk.Button(button_frame, text="Check Balance", 
                                      command=self.check_balance, style='Primary.TButton')
        self.check_button.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="Clear", 
                                      command=self.clear_input)
        self.clear_button.grid(row=0, column=1, padx=(0, 5))
        
        self.refresh_button = ttk.Button(button_frame, text="Auto Refresh", 
                                        command=self.toggle_auto_refresh)
        self.refresh_button.grid(row=0, column=2)
        
        # Sample addresses
        sample_frame = ttk.Frame(input_frame)
        sample_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(sample_frame, text="Sample addresses:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        sample_addresses = [
            ("Vitalik's Wallet", "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"),
            ("Uniswap Router", "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
            ("USDC Contract", "0xA0b86a33E6441ba5d2e0b87b4E8b4f3c8B6d6b5f")
        ]
        
        for i, (name, addr) in enumerate(sample_addresses):
            btn = ttk.Button(sample_frame, text=name, 
                           command=lambda a=addr: self.address_var.set(a))
            btn.grid(row=1, column=i, padx=(0, 5), pady=(5, 0), sticky=tk.W)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Balance Information", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)
        
        # Balance display
        self.balance_frame = ttk.Frame(results_frame)
        self.balance_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.balance_label = ttk.Label(self.balance_frame, text="Balance: Not checked", 
                                      font=('Helvetica', 14, 'bold'))
        self.balance_label.grid(row=0, column=0, sticky=tk.W)
        
        self.usd_label = ttk.Label(self.balance_frame, text="USD Value: $0.00", 
                                  font=('Helvetica', 12), foreground='gray')
        self.usd_label.grid(row=1, column=0, sticky=tk.W)
        
        # Additional info
        info_frame = ttk.Frame(results_frame)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Address:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.addr_display = ttk.Label(info_frame, text="None", font=('Courier', 9))
        self.addr_display.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Network:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W)
        self.network_display = ttk.Label(info_frame, text="None")
        self.network_display.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Transactions:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W)
        self.tx_count_label = ttk.Label(info_frame, text="0")
        self.tx_count_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Last Updated:", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W)
        self.update_time_label = ttk.Label(info_frame, text="Never")
        self.update_time_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.explorer_button = ttk.Button(action_frame, text="View on Explorer", 
                                         command=self.open_explorer, state='disabled')
        self.explorer_button.grid(row=0, column=0, padx=(0, 5))
        
        self.copy_button = ttk.Button(action_frame, text="Copy Address", 
                                     command=self.copy_address, state='disabled')
        self.copy_button.grid(row=0, column=1, padx=(0, 5))
        
        self.save_button = ttk.Button(action_frame, text="Save to History", 
                                     command=self.save_to_history, state='disabled')
        self.save_button.grid(row=0, column=2)
        
        # History and logs
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # History frame
        history_frame = ttk.LabelFrame(bottom_frame, text="History", padding="10")
        history_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)
        
        # History treeview
        self.history_tree = ttk.Treeview(history_frame, columns=('Address', 'Balance', 'USD', 'Time'), 
                                        show='headings', height=8)
        self.history_tree.heading('Address', text='Address')
        self.history_tree.heading('Balance', text='Balance (ETH)')
        self.history_tree.heading('USD', text='USD Value')
        self.history_tree.heading('Time', text='Time')
        
        self.history_tree.column('Address', width=200)
        self.history_tree.column('Balance', width=100)
        self.history_tree.column('USD', width=100)
        self.history_tree.column('Time', width=150)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # History scrollbar
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        history_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        # History buttons
        history_btn_frame = ttk.Frame(history_frame)
        history_btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(history_btn_frame, text="Clear History", 
                  command=self.clear_history).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(history_btn_frame, text="Export History", 
                  command=self.export_history).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(history_btn_frame, text="Load Selected", 
                  command=self.load_from_history).grid(row=0, column=2)
        
        # Logs frame
        logs_frame = ttk.LabelFrame(bottom_frame, text="Logs", padding="10")
        logs_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        logs_frame.rowconfigure(0, weight=1)
        logs_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=10, width=40, 
                                                 font=('Courier', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log buttons
        log_btn_frame = ttk.Frame(logs_frame)
        log_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(log_btn_frame, text="Clear Logs", 
                  command=self.clear_logs).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(log_btn_frame, text="Save Logs", 
                  command=self.save_logs).grid(row=0, column=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Initial connection
        self.connect_to_network()
    
    def setup_bindings(self):
        """Setup keyboard bindings and events"""
        self.root.bind('<Return>', lambda e: self.check_balance())
        self.root.bind('<Control-c>', lambda e: self.copy_address())
        self.root.bind('<Control-l>', lambda e: self.clear_logs())
        self.root.bind('<F5>', lambda e: self.check_balance())
        self.address_entry.bind('<KeyRelease>', self.on_address_change)
        self.history_tree.bind('<Double-1>', lambda e: self.load_from_history())
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(f"{level}: {message}")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def connect_to_network(self):
        """Connect to selected network"""
        network_map = {
            "mainnet": NetworkType.MAINNET,
            "goerli": NetworkType.GOERLI,
            "sepolia": NetworkType.SEPOLIA,
            "polygon": NetworkType.POLYGON,
            "bsc": NetworkType.BSC
        }
        
        network = network_map.get(self.network_var.get(), NetworkType.MAINNET)
        
        def connect():
            self.update_status("Connecting to network...")
            self.progress.start()
            
            try:
                success = self.checker.connect_to_network(network)
                if success:
                    self.status_label.config(text="● Connected", style='Success.TLabel')
                    self.log_message(f"Connected to {self.checker.networks[network]['name']}")
                    self.network_display.config(text=self.checker.networks[network]['name'])
                else:
                    self.status_label.config(text="● Connection Failed", style='Danger.TLabel')
                    self.log_message("Failed to connect to network", "ERROR")
                    
            except Exception as e:
                self.status_label.config(text="● Error", style='Danger.TLabel')
                self.log_message(f"Connection error: {str(e)}", "ERROR")
            
            finally:
                self.progress.stop()
                self.update_status("Ready")
        
        threading.Thread(target=connect, daemon=True).start()
    
    def on_network_change(self, event=None):
        """Handle network change"""
        self.connect_to_network()
    
    def on_address_change(self, event=None):
        """Handle address input change"""
        address = self.address_var.get().strip()
        if address:
            is_valid = self.checker.validate_address(address)
            if is_valid:
                self.address_entry.config(style='TEntry')
            else:
                self.address_entry.config(style='TEntry')  # Could add error style
    
    def check_balance(self):
        """Check balance for entered address"""
        address = self.address_var.get().strip()
        
        if not address:
            messagebox.showwarning("Warning", "Please enter a wallet address")
            return
        
        if not self.checker.validate_address(address):
            messagebox.showerror("Error", "Invalid wallet address format")
            return
        
        def check():
            self.update_status("Checking balance...")
            self.progress.start()
            self.check_button.config(state='disabled')
            
            try:
                wallet_info = self.checker.get_wallet_info(address)
                
                if wallet_info:
                    # Update UI
                    self.balance_label.config(text=f"Balance: {wallet_info.balance:.6f} ETH")
                    self.usd_label.config(text=f"USD Value: ${wallet_info.usd_value:.2f}")
                    self.addr_display.config(text=f"{address[:20]}...{address[-20:]}")
                    self.tx_count_label.config(text=str(self.checker.get_transaction_count(address)))
                    self.update_time_label.config(text=wallet_info.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # Enable buttons
                    self.explorer_button.config(state='normal')
                    self.copy_button.config(state='normal')
                    self.save_button.config(state='normal')
                    
                    self.log_message(f"Balance checked for {address[:10]}...{address[-10:]}")
                    self.log_message(f"Balance: {wallet_info.balance:.6f} ETH (${wallet_info.usd_value:.2f})")
                    
                else:
                    messagebox.showerror("Error", "Failed to get balance")
                    self.log_message("Failed to get balance", "ERROR")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error checking balance: {str(e)}")
                self.log_message(f"Error checking balance: {str(e)}", "ERROR")
            
            finally:
                self.progress.stop()
                self.check_button.config(state='normal')
                self.update_status("Ready")
        
        threading.Thread(target=check, daemon=True).start()
    
    def clear_input(self):
        """Clear input fields"""
        self.address_var.set("")
        self.balance_label.config(text="Balance: Not checked")
        self.usd_label.config(text="USD Value: $0.00")
        self.addr_display.config(text="None")
        self.tx_count_label.config(text="0")
        self.update_time_label.config(text="Never")
        
        # Disable buttons
        self.explorer_button.config(state='disabled')
        self.copy_button.config(state='disabled')
        self.save_button.config(state='disabled')
    
    def toggle_auto_refresh(self):
        """Toggle auto refresh"""
        self.auto_refresh = not self.auto_refresh
        
        if self.auto_refresh:
            self.refresh_button.config(text="Stop Auto Refresh")
            self.start_auto_refresh()
            self.log_message("Auto refresh enabled")
        else:
            self.refresh_button.config(text="Auto Refresh")
            self.log_message("Auto refresh disabled")
    
    def start_auto_refresh(self):
        """Start auto refresh loop"""
        def refresh_loop():
            while self.auto_refresh:
                if self.address_var.get().strip():
                    self.check_balance()
                time.sleep(self.refresh_interval)
        
        threading.Thread(target=refresh_loop, daemon=True).start()
    
    def open_explorer(self):
        """Open address in blockchain explorer"""
        address = self.address_var.get().strip()
        if address:
            network = self.checker.current_network
            explorer_url = self.checker.networks[network]["explorer"] + address
            webbrowser.open(explorer_url)
            self.log_message(f"Opened explorer for {address[:10]}...{address[-10:]}")
    
    def copy_address(self):
        """Copy address to clipboard"""
        address = self.address_var.get().strip()
        if address:
            self.root.clipboard_clear()
            self.root.clipboard_append(address)
            self.log_message("Address copied to clipboard")
            messagebox.showinfo("Success", "Address copied to clipboard")
    
    def save_to_history(self):
        """Save current wallet info to history"""
        address = self.address_var.get().strip()
        if address and self.checker.validate_address(address):
            # Get current balance info
            balance_text = self.balance_label.cget('text')
            usd_text = self.usd_label.cget('text')
            time_text = self.update_time_label.cget('text')
            
            # Extract values
            balance = balance_text.replace("Balance: ", "").replace(" ETH", "")
            usd_value = usd_text.replace("USD Value: $", "")
            
            # Add to history tree
            self.history_tree.insert('', 0, values=(
                f"{address[:20]}...{address[-20:]}",
                balance,
                f"${usd_value}",
                time_text
            ))
            
            # Store full address in history
            self.wallet_history.insert(0, {
                'address': address,
                'balance': balance,
                'usd_value': usd_value,
                'time': time_text
            })
            
            self.log_message("Wallet info saved to history")
    
    def clear_history(self):
        """Clear wallet history"""
        self.history_tree.delete(*self.history_tree.get_children())
        self.wallet_history.clear()
                self.log_message("History cleared")

    def export_history(self):
        """Export wallet history to a JSON file"""
        if not self.wallet_history:
            messagebox.showinfo("Info", "No history to export.")
            return
        
        try:
            with open("wallet_history.json", "w") as f:
                json.dump(self.wallet_history, f, indent=4)
            messagebox.showinfo("Success", "History exported to wallet_history.json")
            self.log_message("History exported to wallet_history.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history: {e}")
            self.log_message(f"Export error: {e}", "ERROR")

    def load_from_history(self):
        """Load selected entry from history into input"""
        selected_item = self.history_tree.selection()
        if selected_item:
            values = self.history_tree.item(selected_item, "values")
            if values:
                full_address = next((entry['address'] for entry in self.wallet_history 
                                     if entry['address'].startswith(values[0][:20]) and entry['address'].endswith(values[0][-20:])), None)
                if full_address:
                    self.address_var.set(full_address)
                    self.log_message("Loaded address from history")

    def clear_logs(self):
        """Clear log output"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Logs cleared")

    def save_logs(self):
        """Save logs to a text file"""
        try:
            log_content = self.log_text.get(1.0, tk.END).strip()
            if not log_content:
                messagebox.showinfo("Info", "No logs to save.")
                return
            with open("logs.txt", "w") as f:
                f.write(log_content)
            messagebox.showinfo("Success", "Logs saved to logs.txt")
            self.log_message("Logs saved to logs.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
            self.log_message(f"Log save error: {e}", "ERROR")

    def run(self):
        """Run the main application loop"""
        self.root.mainloop()


if __name__ == "__main__":
    gui = ModernGUI()
    gui.run()
