#!/usr/bin/env python3
import os
import subprocess
import platform
import sys

def generate_self_signed_cert():
    """Generate self-signed SSL certificates for local development"""
    print("Generating self-signed SSL certificates for HTTPS support...")
    
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        print("Certificate files already exist. Do you want to override them?")
        response = input("Enter [y/n]: ").lower()
        if response != 'y':
            print("Aborted. Using existing certificates.")
            return
    
    # Detect OS for command variations
    system = platform.system()
    
    try:
        if system == 'Windows':
            # First check if OpenSSL is available
            try:
                subprocess.run(["where", "openssl"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("OpenSSL not found in PATH. Please install OpenSSL to generate certificates.")
                print("Download OpenSSL for Windows from: https://slproweb.com/products/Win32OpenSSL.html")
                return
            
            # Run OpenSSL command
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
                "-out", "cert.pem", "-keyout", "key.pem", "-days", "365",
                "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
            ], check=True)
        else:  # Linux, macOS, etc.
            # First check if OpenSSL is available
            try:
                subprocess.run(["which", "openssl"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("OpenSSL not found. Please install OpenSSL to generate certificates.")
                return
            
            # Run OpenSSL command
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
                "-out", "cert.pem", "-keyout", "key.pem", "-days", "365",
                "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
            ], check=True)
        
        print("SSL certificates generated successfully!")
        print("cert.pem and key.pem created in the current directory.")
        print("\nNOTE: Since these are self-signed certificates, browsers will show a security warning.")
        print("In a production environment, use certificates from a trusted certificate authority.")
        
        # For localhost testing, provide instructions for browser trust
        if system == 'Windows':
            print("\nTo trust this certificate in Windows:")
            print("1. Double-click cert.pem and select 'Install Certificate'")
            print("2. Select 'Current User' and click 'Next'")
            print("3. Select 'Place all certificates in the following store' and click 'Browse'")
            print("4. Select 'Trusted Root Certification Authorities' and click 'OK'")
            print("5. Click 'Next' and then 'Finish'")
        elif system == 'Darwin':  # macOS
            print("\nTo trust this certificate in macOS:")
            print("1. Double-click cert.pem to add it to Keychain Access")
            print("2. Open Keychain Access, find the certificate (under 'localhost')")
            print("3. Double-click it, expand 'Trust', and set 'When using this certificate' to 'Always Trust'")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    generate_self_signed_cert()