# Remote Control App by Maxime

A powerful web-based remote control application that allows you to control your computer from any device with a web browser.

## Features
- 🖱️ Full mouse control (movement, clicks, scrolling)
- 🎹 Keyboard input support
- 🖥️ Screen sharing
- 📱 Mobile and desktop friendly interface

## Prerequisites
- Windows 10 or 11
- Python 3.8+
- Stable local network connection

## Installation

### 1. Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation by opening Command Prompt and running:
   ```
   python --version
   pip --version
   ```

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/remote-control-app.git
cd remote-control-app
```

### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## Portable Setup (USB Key)

### Portable Python Options
1. **Miniconda Portable**
   - Download Miniconda Portable from [Miniconda website](https://docs.conda.io/en/latest/miniconda.html)
   - Choose the Windows installer
   - Extract to your USB key

2. **Portable Python**
   - Use distributions like [Portable Python](https://portablepython.com/)
   - Ensure compatibility with your project's Python version

### Setting Up a Portable Environment
```bash
# On the USB key
cd [USB_DRIVE_LETTER]:\PortablePython

# Create a virtual environment
python -m venv remote_control_env

# Activate the environment
remote_control_env\Scripts\activate

# Navigate to your project
cd path\to\remote_control_app

# Install dependencies
pip install -r requirements.txt
```

### Potential Challenges
⚠️ **Compatibility Considerations:**
- Ensure Python version matches your project requirements
- Some system-specific libraries might need reinstallation
- Check Windows architecture (32-bit vs 64-bit)
- Firewall and antivirus settings may differ between computers

### Recommended Workflow
1. Prepare a clean, portable Python environment
2. Copy entire project folder to USB key
3. Install dependencies on each target computer
4. Use virtual environment for isolation

## Running the Application

### 1. Start the Server
```bash
python app.py
```

### 2. Access the Application
- Open a web browser on your computer or phone
- Navigate to `http://[YOUR_COMPUTER_IP]:5000`
  
  🔍 **How to Find Your Computer's IP:**
  - Windows: Open Command Prompt
  - Type `ipconfig`
  - Look for "IPv4 Address" under your network adapter

## Security Considerations
⚠️ **Important Security Notes:**
- This app is designed for use on a trusted local network
- Do NOT expose the application to the public internet
- Recommended to use on a private, password-protected network

## Troubleshooting
- Ensure firewall allows Python and the application
- Check that all dependencies are correctly installed
- Verify network connectivity between devices

## Contributing
Contributions are welcome! Please read the contributing guidelines before submitting a pull request.

## License
[Specify your license here, e.g., MIT License]

## Support
For issues or feature requests, please open an issue on the GitHub repository.
