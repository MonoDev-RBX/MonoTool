import zlib, os, time
from getpass import getpass
from SubTools.Enforce_Extension import enforce_extension
from SubTools.Encryptor import Encryptor

class MonoPL:
    def __init__(self):
        os.makedirs("_MONOTEMP", exist_ok=True)

    def convert_txt_to_monopl(self, txt, out):
        enforce_extension(txt, [".txt"])
        enforce_extension(out, [".monopl"])
        data = open(txt, "rb").read()
        compressed = zlib.compress(data)

        if input("🔐 Encrypt .monopl? (y/n): ").lower() == "y":
            password = getpass("Enter password: ")
            compressed = Encryptor.encrypt(compressed, password)

        with open(out, "wb") as f:
            f.write(compressed)
        print(f"✅ Saved .monopl: {out}")

    def convert_monopl_to_txt(self, monopl, out):
        enforce_extension(monopl, [".monopl"])
        enforce_extension(out, [".txt"])
        data = open(monopl, "rb").read()

        try:
            data = Encryptor.decrypt(data, getpass("Enter password to decrypt .monopl: "))
        except:
            print("🔓 Decryption failed or not encrypted. Using raw data.")

        decompressed = zlib.decompress(data)
        with open(out, "wb") as f:
            f.write(decompressed)
        print(f"✅ Restored TXT: {out}")

    def check_size(self, path):
        print(f"📦 Size of '{path}': {os.path.getsize(path)} bytes")

    def monoplview(self, path):
        tmp = "_MONOTEMP/monoplview.txt"
        self.convert_monopl_to_txt(path, tmp)
        os.system(f"open {tmp}")
        time.sleep(1)
        os.remove(tmp)

    def run(self):
        print("📄 MonoPL Tool: txttomonopl, monopltotxt, size, monoplview, quit")
        while True:
            cmd = input("monopl> ").strip().lower()
            if cmd == "txttomonopl":
                self.convert_txt_to_monopl(input("TXT path: "), input("Output .monopl path: "))
            elif cmd == "monopltotxt":
                self.convert_monopl_to_txt(input(".monopl path: "), input("Output .txt path: "))
            elif cmd == "size":
                self.check_size(input("File path: "))
            elif cmd == "monoplview":
                self.monoplview(input("Input .monopl path: "))
            elif cmd == "quit":
                print("👋 Returning to Mono Tool...")
                break
            else:
                print("❌ Invalid command.")
