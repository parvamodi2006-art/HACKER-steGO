#!/usr/bin/env python3
"""
LSB Steganography Tool with Encryption - Complete Implementation
Combines GUI, CLI, and core functionality in one file
Supports AES encryption for enhanced security
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
import struct
import argparse
import sys
from pathlib import Path
from typing import Tuple, Optional
import base64
import hashlib

# Try to import encryption library, make it optional
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


# ============================================================================
# ENCRYPTION CLASS
# ============================================================================

class EncryptionManager:
    """Handles encryption and decryption of messages"""
    
    @staticmethod
    def generate_key(password: str) -> bytes:
        """Generate encryption key from password"""
        if not ENCRYPTION_AVAILABLE:
            raise Exception("Encryption not available. Install: pip install cryptography")
        
        # Hash password to create a consistent key
        hash_obj = hashlib.sha256(password.encode())
        key = base64.urlsafe_b64encode(hash_obj.digest())
        return key
    
    @staticmethod
    def encrypt_message(message: str, password: str) -> str:
        """Encrypt message with password"""
        if not ENCRYPTION_AVAILABLE:
            raise Exception("Encryption not available. Install: pip install cryptography")
        
        try:
            key = EncryptionManager.generate_key(password)
            cipher = Fernet(key)
            encrypted = cipher.encrypt(message.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise Exception(f"Encryption error: {str(e)}")
    
    @staticmethod
    def decrypt_message(encrypted_message: str, password: str) -> str:
        """Decrypt message with password"""
        if not ENCRYPTION_AVAILABLE:
            raise Exception("Encryption not available. Install: pip install cryptography")
        
        try:
            key = EncryptionManager.generate_key(password)
            cipher = Fernet(key)
            encrypted = base64.b64decode(encrypted_message.encode('utf-8'))
            decrypted = cipher.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption error: {str(e)}")


# ============================================================================
# CORE STEGANOGRAPHY CLASS
# ============================================================================

class LSBSteganography:
    """Handles LSB steganography encoding and decoding"""
    
    @staticmethod
    def encode_message(image_path: str, message: str, output_path: str, 
                      password: str = None) -> bool:
        """
        Encode a message into an image using LSB technique
        
        Args:
            image_path: Path to the source image
            message: Message to hide
            output_path: Path to save the encoded image
            password: Optional password for encryption
            
        Returns:
            True if successful, False otherwise
        """
        # Encrypt message if password provided
        if password:
            message = EncryptionManager.encrypt_message(message, password)
        try:
            img = Image.open(image_path).convert('RGB')
            pixels = img.load()
            width, height = img.size
            max_bytes = (width * height * 3) // 8
            
            # Prepare message with length header
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes)
            
            if message_length > max_bytes - 4:
                raise ValueError(f"Message too long. Max: {max_bytes - 4} bytes")
            
            # Convert message length to 4-byte header
            length_bytes = struct.pack('>I', message_length)
            full_message = length_bytes + message_bytes
            
            # Convert message to binary
            binary_message = ''.join(format(byte, '08b') for byte in full_message)
            
            # Encode message into LSBs
            bit_index = 0
            for y in range(height):
                for x in range(width):
                    if bit_index >= len(binary_message):
                        break
                    
                    r, g, b = pixels[x, y]
                    
                    # Modify LSB of R channel
                    if bit_index < len(binary_message):
                        r = (r & 0xFE) | int(binary_message[bit_index])
                        bit_index += 1
                    
                    # Modify LSB of G channel
                    if bit_index < len(binary_message):
                        g = (g & 0xFE) | int(binary_message[bit_index])
                        bit_index += 1
                    
                    # Modify LSB of B channel
                    if bit_index < len(binary_message):
                        b = (b & 0xFE) | int(binary_message[bit_index])
                        bit_index += 1
                    
                    pixels[x, y] = (r, g, b)
                
                if bit_index >= len(binary_message):
                    break
            
            img.save(output_path)
            return True
            
        except Exception as e:
            raise Exception(f"Encoding error: {str(e)}")
    
    @staticmethod
    def decode_message(image_path: str, password: str = None) -> str:
        """
        Extract a hidden message from an image using LSB technique
        
        Args:
            image_path: Path to the image containing hidden message
            password: Optional password for decryption
            
        Returns:
            The decoded message
        """
        try:
            img = Image.open(image_path).convert('RGB')
            pixels = img.load()
            width, height = img.size
            
            # Extract all LSBs
            binary_message = ''
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    binary_message += str(r & 1)
                    binary_message += str(g & 1)
                    binary_message += str(b & 1)
            
            # Extract message length (first 4 bytes = 32 bits)
            if len(binary_message) < 32:
                raise ValueError("Image too small or no hidden message found")
            
            length_binary = binary_message[:32]
            message_length = struct.unpack('>I', bytes(int(length_binary[i:i+8], 2) 
                                                       for i in range(0, 32, 8)))[0]
            
            # Extract message
            if message_length > 1000000:  # Sanity check
                raise ValueError("Invalid message length detected")
            
            message_bits = binary_message[32:32 + (message_length * 8)]
            message_bytes = bytes(int(message_bits[i:i+8], 2) 
                                 for i in range(0, len(message_bits), 8))
            
            message = message_bytes.decode('utf-8')
            
            # Decrypt message if password provided
            if password:
                message = EncryptionManager.decrypt_message(message, password)
            
            return message
            
        except Exception as e:
            raise Exception(f"Decoding error: {str(e)}")


# ============================================================================
# GUI APPLICATION CLASS
# ============================================================================

class SteganographyGUI:
    """Main GUI application for LSB steganography"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography Tool")
        self.root.geometry("900x750")
        self.root.configure(bg='#0F1419')
        
        # Configure style
        self.setup_styles()
        
        # Current image path
        self.current_image = None
        self.current_image_tk = None
        
        # Create main container
        self.create_widgets()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.bg_primary = '#0F1419'
        self.bg_secondary = '#1A202C'
        self.accent = '#00D9FF'
        self.accent_dark = '#0099BB'
        self.text_primary = '#FFFFFF'
        self.text_secondary = '#A0AEC0'
        self.success = '#48BB78'
        self.danger = '#F56565'
        
        # Configure styles
        style.configure('TFrame', background=self.bg_primary)
        style.configure('Title.TLabel', background=self.bg_primary, 
                       foreground=self.text_primary, font=('Helvetica', 16, 'bold'))
        style.configure('Subtitle.TLabel', background=self.bg_secondary, 
                       foreground=self.text_primary, font=('Helvetica', 12, 'bold'))
        style.configure('TLabel', background=self.bg_primary, 
                       foreground=self.text_secondary, font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'),
                       padding=10)
        style.map('TButton',
                 background=[('active', self.accent_dark)],
                 foreground=[('active', '#FFFFFF')])
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.bg_secondary, height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🔐 LSB Steganography",
                        font=('Helvetica', 20, 'bold'),
                        bg=self.bg_secondary, fg=self.accent)
        title.pack(pady=12)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook (tabs)
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Encode Tab
        self.encode_frame = ttk.Frame(notebook)
        notebook.add(self.encode_frame, text='Hide Message')
        self.create_encode_tab()
        
        # Decode Tab
        self.decode_frame = ttk.Frame(notebook)
        notebook.add(self.decode_frame, text='Extract Message')
        self.create_decode_tab()
    
    def create_encode_tab(self):
        """Create the message encoding tab"""
        # Image selection
        img_section = tk.Frame(self.encode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        img_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(img_section, text="Step 1: Select Image", 
                font=('Helvetica', 12, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        button_frame = tk.Frame(img_section, bg=self.bg_secondary)
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        tk.Button(button_frame, text="Browse Image", command=self.select_image_encode,
                 bg=self.accent, fg='#000', font=('Helvetica', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        self.encode_image_label = tk.Label(button_frame, text="No image selected",
                                          bg=self.bg_secondary, fg=self.text_secondary,
                                          font=('Helvetica', 9))
        self.encode_image_label.pack(side=tk.LEFT, padx=10)
        
        # Image preview
        preview_frame = tk.Frame(self.encode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(preview_frame, text="Preview", font=('Helvetica', 11, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        self.preview_label = tk.Label(preview_frame, bg=self.bg_secondary, 
                                     fg=self.text_secondary, text="Image preview will appear here",
                                     font=('Helvetica', 10), padx=12, pady=30)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Message input
        msg_section = tk.Frame(self.encode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        msg_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(msg_section, text="Step 2: Enter Secret Message",
                font=('Helvetica', 12, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        self.encode_message_text = scrolledtext.ScrolledText(msg_section, height=4, 
                                                            bg='#2D3748', fg=self.text_primary,
                                                            font=('Courier', 10),
                                                            insertbackground=self.accent,
                                                            relief=tk.FLAT, padx=10, pady=10)
        self.encode_message_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        # Encryption option
        crypto_section = tk.Frame(self.encode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        crypto_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(crypto_section, text="Step 3: Optional Encryption",
                font=('Helvetica', 12, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        # Checkbox for encryption
        self.encode_use_crypto = tk.BooleanVar(value=False)
        crypto_check = tk.Checkbutton(crypto_section, text="Encrypt message with password",
                                     variable=self.encode_use_crypto,
                                     command=self.toggle_encode_password,
                                     bg=self.bg_secondary, fg=self.text_primary,
                                     selectcolor=self.accent, font=('Helvetica', 10))
        crypto_check.pack(anchor='w', padx=12, pady=(0, 8))
        
        # Password entry
        pwd_frame = tk.Frame(crypto_section, bg=self.bg_secondary)
        pwd_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        tk.Label(pwd_frame, text="Password:", bg=self.bg_secondary, 
                fg=self.text_secondary, font=('Helvetica', 9)).pack(side=tk.LEFT, padx=5)
        
        self.encode_password = tk.Entry(pwd_frame, bg='#2D3748', fg=self.text_primary,
                                       font=('Courier', 10), show='*', relief=tk.FLAT)
        self.encode_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.encode_password.config(state=tk.DISABLED)
        
        # Encode button
        button_section = tk.Frame(self.encode_frame, bg=self.bg_primary)
        button_section.pack(fill=tk.X, pady=10)
        
        tk.Button(button_section, text="Hide Message in Image", command=self.encode_message,
                 bg=self.success, fg='#000', font=('Helvetica', 11, 'bold'),
                 relief=tk.FLAT, padx=20, pady=10, cursor='hand2',
                 activebackground='#38A169').pack(side=tk.LEFT, padx=5)
    
    def create_decode_tab(self):
        """Create the message decoding tab"""
        # Image selection
        img_section = tk.Frame(self.decode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        img_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(img_section, text="Step 1: Select Encoded Image",
                font=('Helvetica', 12, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        button_frame = tk.Frame(img_section, bg=self.bg_secondary)
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        tk.Button(button_frame, text="Browse Image", command=self.select_image_decode,
                 bg=self.accent, fg='#000', font=('Helvetica', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        self.decode_image_label = tk.Label(button_frame, text="No image selected",
                                          bg=self.bg_secondary, fg=self.text_secondary,
                                          font=('Helvetica', 9))
        self.decode_image_label.pack(side=tk.LEFT, padx=10)
        
        # Extract button
        extract_section = tk.Frame(self.decode_frame, bg=self.bg_primary)
        extract_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(extract_section, text="Extract Hidden Message", command=self.decode_message,
                 bg=self.success, fg='#000', font=('Helvetica', 11, 'bold'),
                 relief=tk.FLAT, padx=20, pady=10, cursor='hand2',
                 activebackground='#38A169').pack(side=tk.LEFT, padx=5)
        
        # Decryption option
        decrypt_section = tk.Frame(self.decode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        decrypt_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(decrypt_section, text="Decryption (If Encrypted)",
                font=('Helvetica', 11, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        # Checkbox for decryption
        self.decode_use_crypto = tk.BooleanVar(value=False)
        decrypt_check = tk.Checkbutton(decrypt_section, text="Decrypt with password",
                                      variable=self.decode_use_crypto,
                                      command=self.toggle_decode_password,
                                      bg=self.bg_secondary, fg=self.text_primary,
                                      selectcolor=self.accent, font=('Helvetica', 10))
        decrypt_check.pack(anchor='w', padx=12, pady=(0, 8))
        
        # Password entry
        pwd_frame = tk.Frame(decrypt_section, bg=self.bg_secondary)
        pwd_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        tk.Label(pwd_frame, text="Password:", bg=self.bg_secondary,
                fg=self.text_secondary, font=('Helvetica', 9)).pack(side=tk.LEFT, padx=5)
        
        self.decode_password = tk.Entry(pwd_frame, bg='#2D3748', fg=self.text_primary,
                                       font=('Courier', 10), show='*', relief=tk.FLAT)
        self.decode_password.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.decode_password.config(state=tk.DISABLED)
        
        # Extracted message
        msg_section = tk.Frame(self.decode_frame, bg=self.bg_secondary, relief=tk.FLAT)
        msg_section.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(msg_section, text="Step 2: View Extracted Message",
                font=('Helvetica', 12, 'bold'),
                bg=self.bg_secondary, fg=self.text_primary).pack(anchor='w', padx=12, pady=8)
        
        self.decode_message_text = scrolledtext.ScrolledText(msg_section, height=10,
                                                            bg='#2D3748', fg=self.text_primary,
                                                            font=('Courier', 10),
                                                            relief=tk.FLAT, padx=10, pady=10,
                                                            state=tk.DISABLED)
        self.decode_message_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        # Copy button
        button_frame = tk.Frame(msg_section, bg=self.bg_secondary)
        button_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        tk.Button(button_frame, text="Copy Message", command=self.copy_decoded_message,
                 bg='#4299E1', fg='#000', font=('Helvetica', 10, 'bold'),
                 relief=tk.FLAT, padx=15, pady=8, cursor='hand2',
                 activebackground='#3182CE').pack(side=tk.LEFT, padx=5)
    
    def select_image_encode(self):
        """Select image for encoding"""
        filetypes = (("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Select image", filetypes=filetypes)
        
        if filename:
            self.current_image = filename
            self.encode_image_label.config(text=f"Selected: {Path(filename).name}")
            self.display_preview(filename)
    
    def select_image_decode(self):
        """Select image for decoding"""
        filetypes = (("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Select encoded image", filetypes=filetypes)
        
        if filename:
            self.current_image = filename
            self.decode_image_label.config(text=f"Selected: {Path(filename).name}")
    
    def display_preview(self, image_path: str):
        """Display image preview"""
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            self.current_image_tk = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.current_image_tk, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def toggle_encode_password(self):
        """Toggle password field enable/disable"""
        if self.encode_use_crypto.get():
            self.encode_password.config(state=tk.NORMAL)
        else:
            self.encode_password.config(state=tk.DISABLED)
            self.encode_password.delete(0, tk.END)
    
    def toggle_decode_password(self):
        """Toggle password field enable/disable"""
        if self.decode_use_crypto.get():
            self.decode_password.config(state=tk.NORMAL)
        else:
            self.decode_password.config(state=tk.DISABLED)
            self.decode_password.delete(0, tk.END)
    
    def encode_message(self):
        """Encode message into image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        message = self.encode_message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        password = None
        if self.encode_use_crypto.get():
            password = self.encode_password.get()
            if not password:
                messagebox.showwarning("Warning", "Please enter a password for encryption")
                return
            if not ENCRYPTION_AVAILABLE:
                messagebox.showerror("Error", "Encryption not available. Install: pip install cryptography")
                return
        
        # Get output filename
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=(("PNG files", "*.png"), ("All files", "*.*")),
            initialfile="encoded_image.png"
        )
        
        if not output_path:
            return
        
        try:
            LSBSteganography.encode_message(self.current_image, message, output_path, password)
            status = "Message hidden successfully!"
            if password:
                status += "\n\n🔐 Encrypted with password"
            status += f"\n\nSaved to: {Path(output_path).name}"
            messagebox.showinfo("Success", status)
        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed: {str(e)}")
    
    def decode_message(self):
        """Decode message from image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        password = None
        if self.decode_use_crypto.get():
            password = self.decode_password.get()
            if not password:
                messagebox.showwarning("Warning", "Please enter the password for decryption")
                return
            if not ENCRYPTION_AVAILABLE:
                messagebox.showerror("Error", "Encryption not available. Install: pip install cryptography")
                return
        
        try:
            message = LSBSteganography.decode_message(self.current_image, password)
            self.decode_message_text.config(state=tk.NORMAL)
            self.decode_message_text.delete("1.0", tk.END)
            self.decode_message_text.insert("1.0", message)
            self.decode_message_text.config(state=tk.DISABLED)
            status = "Message extracted successfully!"
            if password:
                status += "\n\n🔓 Decrypted with password"
            messagebox.showinfo("Success", status)
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed: {str(e)}")
    
    def copy_decoded_message(self):
        """Copy decoded message to clipboard"""
        try:
            message = self.decode_message_text.get("1.0", tk.END).strip()
            if message:
                self.root.clipboard_clear()
                self.root.clipboard_append(message)
                messagebox.showinfo("Success", "Message copied to clipboard!")
            else:
                messagebox.showwarning("Warning", "No message to copy")
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {str(e)}")


# ============================================================================
# CLI APPLICATION
# ============================================================================

class CLI:
    """Command-line interface for steganography"""
    
    @staticmethod
    def main():
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description='Hide and extract secret messages in images using LSB steganography',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  Hide a message:
    python steganography.py hide image.png "Secret message" output.png
  
  Hide encrypted message:
    python steganography.py hide image.png "Secret message" output.png -p "MyPassword"
  
  Extract a message:
    python steganography.py extract encoded_image.png

  Extract encrypted message:
    python steganography.py extract encoded_image.png -p "MyPassword"

  Launch GUI:
    python steganography.py gui
        '''
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Hide command
        hide_parser = subparsers.add_parser('hide', help='Hide a message in an image')
        hide_parser.add_argument('image', help='Path to source image')
        hide_parser.add_argument('message', help='Message to hide')
        hide_parser.add_argument('output', help='Path to save encoded image')
        hide_parser.add_argument('-p', '--password', help='Password for encryption (optional)')
        
        # Extract command
        extract_parser = subparsers.add_parser('extract', help='Extract a hidden message from an image')
        extract_parser.add_argument('image', help='Path to encoded image')
        extract_parser.add_argument('-p', '--password', help='Password for decryption (if encrypted)')
        
        # GUI command
        gui_parser = subparsers.add_parser('gui', help='Launch graphical interface')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            sys.exit(1)
        
        if args.command == 'hide':
            if not Path(args.image).exists():
                print(f"✗ Error: Image file not found: {args.image}", file=sys.stderr)
                sys.exit(1)
            CLI.hide(args.image, args.message, args.output, args.password)
        
        elif args.command == 'extract':
            if not Path(args.image).exists():
                print(f"✗ Error: Image file not found: {args.image}", file=sys.stderr)
                sys.exit(1)
            CLI.extract(args.image, args.password)
        
        elif args.command == 'gui':
            CLI.launch_gui()
    
    @staticmethod
    def hide(image_path: str, message: str, output_path: str, password: str = None):
        """Hide a message in an image"""
        try:
            if password and not ENCRYPTION_AVAILABLE:
                print(f"✗ Error: Encryption not available. Install: pip install cryptography", file=sys.stderr)
                sys.exit(1)
            
            LSBSteganography.encode_message(image_path, message, output_path, password)
            print(f"✓ Message encoded successfully!")
            if password:
                print(f"🔐 Encrypted with password")
            print(f"  Output: {output_path}")
            msg_size = len(message.encode('utf-8'))
            if password:
                # Encrypted message will be base64 encoded, larger
                from cryptography.fernet import Fernet
                import base64
                key = EncryptionManager.generate_key(password)
                cipher = Fernet(key)
                encrypted = cipher.encrypt(message.encode('utf-8'))
                msg_size = len(base64.b64encode(encrypted))
            print(f"  Message size: {msg_size} bytes")
            img = Image.open(image_path)
            width, height = img.size
            max_bytes = (width * height * 3) // 8
            print(f"  Capacity: {max_bytes} bytes")
        except Exception as e:
            print(f"✗ Encoding error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    @staticmethod
    def extract(image_path: str, password: str = None):
        """Extract a message from an image"""
        try:
            if password and not ENCRYPTION_AVAILABLE:
                print(f"✗ Error: Encryption not available. Install: pip install cryptography", file=sys.stderr)
                sys.exit(1)
            
            message = LSBSteganography.decode_message(image_path, password)
            print(f"✓ Message extracted successfully!")
            if password:
                print(f"🔓 Decrypted with password")
            print(f"\n--- Hidden Message ---")
            print(message)
            print(f"--- End of Message ---\n")
        except Exception as e:
            print(f"✗ Decoding error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    @staticmethod
    def launch_gui():
        """Launch the GUI application"""
        root = tk.Tk()
        app = SteganographyGUI(root)
        root.mainloop()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point - determine mode (CLI or GUI)"""
    # If no arguments, launch GUI
    if len(sys.argv) == 1:
        print("Launching GUI...")
        root = tk.Tk()
        app = SteganographyGUI(root)
        root.mainloop()
    else:
        # Use CLI
        CLI.main()


if __name__ == "__main__":
    main()
