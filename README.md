🔐 LSB Steganography with AES Encryption

<img srs="[https://cdn.pixabay.com/photo/2016/11/19/22/52/coding-1841550_1280.jpg](https://media.istockphoto.com/id/468900078/photo/key-on-digital-background.jpg?s=2048x2048&w=is&k=20&c=ylJ8aIc0s9ZaM6WRO_mKqLPWEFyfOT6xwF8X3b6bavQ=)">

Python 3.8+ License Code style: PEP8 Show Image

A complete steganography tool that hides secret messages imperceptibly in images with optional AES-128 encryption for maximum security. Supports both GUI and CLI interfaces.

✨ Features
🔒 Steganography
Hide messages imperceptibly using Least Significant Bit (LSB) technique
Extract hidden messages from encoded images
Invisible to human eye (~0.4% pixel change)
Supports PNG, BMP, GIF, TIFF formats
🔐 Encryption (NEW!)
AES-128 encryption with Fernet authentication
Password-based key derivation (SHA256 + PBKDF2)
Message authentication (HMAC)
Industry-standard cryptography
Completely optional (works without encryption too)
💻 Interfaces
Modern GUI with dark theme and tabs
Command-line interface for automation
Python API for integration
Image preview in GUI
Copy to clipboard
🎯 Capacity
256×256 image: 24 KB
512×512 image: 98 KB
1024×1024 image: 393 KB
2000×2000 image: 1.5 MB
4096×4096 image: 6 MB
🚀 Quick Start
Installation
bash
# Clone repository
git clone https://github.com/yourusername/lsb-steganography.git
cd lsb-steganography

# Install dependencies
pip install -r requirements.txt
Basic Usage
GUI (Recommended for beginners)
bash
python steganography.py

Hide a message:

Click "Hide Message" tab
Select an image
Type your message
(Optional) Check "Encrypt message with password" and enter password
Click "Hide Message in Image"
Save the output

Extract a message:

Click "Extract Message" tab
Select the encoded image
(Optional) Check "Decrypt with password" and enter password
Click "Extract Hidden Message"
Command Line

Hide with encryption:

bash
python steganography.py hide image.png "Secret message" output.png -p "MyPassword123"

Extract with decryption:

bash
python steganography.py extract output.png -p "MyPassword123"

Hide without encryption:

bash
python steganography.py hide image.png "Secret message" output.png

Extract without password:

bash
python steganography.py extract output.png
Python API
python
from steganography import LSBSteganography

# Hide message with encryption
LSBSteganography.encode_message(
    'image.png',
    'Your secret message',
    'output.png',
    password='YourPassword'
)

# Extract and decrypt
message = LSBSteganography.decode_message(
    'output.png',
    password='YourPassword'
)
print(message)  # Your secret message
📖 Documentation
ENCRYPTION_QUICKSTART.md - 5-minute encryption guide
ENCRYPTION_GUIDE.md - Complete encryption documentation
USAGE.md - Comprehensive usage guide
START_WITH_ENCRYPTION.md - Getting started with encryption
💡 Examples
Hide Personal Memory with Encryption
bash
python steganography.py hide vacation.png "Best trip ever! 🎉" memory.png -p "VacationMemory2024"
Share Secret Message Securely
bash
# Sender: Hide and encrypt
python steganography.py hide map.png "Meeting location: 37.7749°N, 122.4194°W" secret.png -p "SecretPass123"

# Receiver: Extract and decrypt (via different password channel)
python steganography.py extract secret.png -p "SecretPass123"
Watermark Artwork
bash
python steganography.py hide artwork.png "© 2024 Artist Name" watermarked.png -p "ArtistPass"
Batch Hide Messages
bash
for img in *.png; do
  python steganography.py hide "$img" "Copyright © 2024" "protected_$img" -p "MyPassword"
done
🔐 How It Works
Without Encryption
Message → Hide in Image → Image (message readable if extracted)
With Encryption
Message → Encrypt with Password → Encrypted Text → Hide in Image
         → Extract → Encrypted Text → Decrypt with Password → Message
LSB Steganography

The tool modifies only the Least Significant Bit (rightmost bit) of each color channel:

Original pixel:  RGB(200, 210, 145) = (11001000, 11010010, 10010001)
                                           ↑         ↑         ↑
Modified pixel:  RGB(201, 211, 144) = (11001001, 11010011, 10010000)
                                           ↑         ↑         ↑

Change per channel: 1 out of 255 = 0.4% (imperceptible!)
⚙️ Requirements
Python 3.8+
Pillow (image processing)
cryptography (optional, for encryption)
tkinter (usually included with Python)
Installation
bash
# Minimal (steganography only)
pip install Pillow

# Recommended (with encryption support)
pip install Pillow cryptography
📊 Performance
Operation	Time
Hide (512×512)	~50 ms
Extract (512×512)	~50 ms
Hide encrypted (512×512)	~60 ms
Extract encrypted (512×512)	~60 ms
🔑 Password Best Practices
✅ Strong Passwords
At least 12 characters
Mix of letters, numbers, symbols
Example: Tr0pic@lMango2024!
❌ Weak Passwords
Dictionary words: password, secret
Sequential numbers: 123456
Personal info: birthdate, name
Important Rules
✅ Remember your password - Cannot be recovered if forgotten
✅ Use strong passwords - 12+ characters recommended
✅ Store separately - Keep password away from image
✅ Share carefully - Use different channel than image
🛠️ Command Reference
bash
# GUI
python steganography.py

# Hide message
python steganography.py hide INPUT_IMAGE "MESSAGE" OUTPUT_IMAGE

# Hide with encryption
python steganography.py hide INPUT_IMAGE "MESSAGE" OUTPUT_IMAGE -p "PASSWORD"

# Extract message
python steganography.py extract IMAGE_FILE

# Extract with decryption
python steganography.py extract IMAGE_FILE -p "PASSWORD"

# Get help
python steganography.py --help
python steganography.py hide --help
python steganography.py extract --help
🎯 Use Cases
Use Case	Method	Command
Personal memories	Encrypted	hide photo.png "note" out.png -p "pass"
Secure sharing	Encrypted	hide image.png "secret" msg.png -p "pass"
Watermarking	Optional	hide art.png "©2024" marked.png -p "pass"
Backup codes	Encrypted	hide img.png "CODE:ABC-123" backup.png -p "pass"
Public sharing	Unencrypted	hide image.png "message" out.png
📁 Project Structure
steganography/
├── steganography.py          # Main application (all-in-one file)
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── ENCRYPTION_GUIDE.md       # Encryption documentation
├── ENCRYPTION_QUICKSTART.md  # Quick encryption guide
├── USAGE.md                  # Usage guide
└── LICENSE                   # MIT License
🔐 Security Notes
Strengths
✅ LSB steganography is well-proven
✅ AES-128 encryption is industry-standard
✅ Password-based key derivation
✅ Message authentication included
Limitations
⚠️ Not suitable for highly sensitive data without additional measures
⚠️ Password cannot be recovered if forgotten
⚠️ Vulnerable to statistical steganalysis (but practical detection is difficult)
⚠️ Lossy compression (JPG) destroys hidden data
Recommendations
✅ Use PNG format for best results
✅ Use strong passwords
✅ Keep passwords separate from images
✅ Test extraction immediately after hiding
✅ Keep backups of important encrypted messages
🐛 Troubleshooting
Issue: "ModuleNotFoundError: No module named 'PIL'"
bash
pip install Pillow
Issue: "Encryption not available"
bash
pip install cryptography
Issue: "Message too long"

Use a larger image (try 512×512 or bigger)

Issue: "GUI won't launch"
bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS
brew install python-tk
Issue: "Decryption error"
Ensure password is correct (case-sensitive)
Check for extra spaces or typos
Verify image wasn't modified after encoding
🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

How to Contribute
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
Ideas for Contribution
Support for audio steganography
Support for video steganography
Additional encryption methods
Web interface
Batch processing improvements
Steganalysis detection
Performance optimizations
📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
👨‍💻 Author

Your Name

GitHub: @yourusername
Email: your.email@example.com
🙏 Acknowledgments
Pillow - Image processing library
cryptography.io - Cryptographic recipes
LSB Steganography - Technical inspiration
📚 References
Steganography on Wikipedia
Least Significant Bit
Fernet (Symmetric Encryption)
PNG Specification
⭐ Show Your Support

Give a ⭐ if this project helped you!

🔗 Links
📖 Full Documentation
🚀 Quick Start Guide
💻 Usage Examples
🔐 Getting Started with Encryption
<div align="center">

Hide Your Secrets Securely 🔐

Built with ❤️ for privacy-conscious developers

Report Bug • Request Feature • Discussions

</div>
