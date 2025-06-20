import os, zlib, time, tempfile
from PIL import Image
from getpass import getpass
from SubTools.MonoPL import MonoPL
from SubTools.Encryptor import Encryptor
from SubTools.Enforce_Extension import enforce_extension

def apply_filter(raw, width, height, channels, filter_type):
    filtered = bytearray()
    stride = width * channels
    for y in range(height):
        row_start = y * stride
        row = list(raw[row_start:row_start + stride])
        filtered.append(filter_type)
        if filter_type == 0:
            filtered.extend(row)
        elif filter_type == 1:
            for i in range(len(row)):
                prior = row[i - channels] if i >= channels else 0
                filtered.append((row[i] - prior) % 256)
        elif filter_type == 2:
            for i in range(len(row)):
                above = raw[row_start + i - stride] if y > 0 else 0
                filtered.append((row[i] - above) % 256)
        elif filter_type == 3:
            for i in range(len(row)):
                prior = row[i - channels] if i >= channels else 0
                above = raw[row_start + i - stride] if y > 0 else 0
                avg = (prior + above) // 2
                filtered.append((row[i] - avg) % 256)
        elif filter_type == 4:
            for i in range(len(row)):
                a = row[i - channels] if i >= channels else 0
                b = raw[row_start + i - stride] if y > 0 else 0
                c = raw[row_start + i - stride - channels] if y > 0 and i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                filtered.append((row[i] - pr) % 256)
    return filtered

def reverse_filter(filtered, width, height, channels, filter_type):
    raw = bytearray()
    stride = width * channels
    i = 0
    for y in range(height):
        f = filtered[i]
        i += 1
        row = list(filtered[i:i + stride])
        i += stride
        if f == 0:
            pass
        elif f == 1:
            for j in range(len(row)):
                prior = row[j - channels] if j >= channels else 0
                row[j] = (row[j] + prior) % 256
        elif f == 2:
            for j in range(len(row)):
                above = raw[(y - 1) * stride + j] if y > 0 else 0
                row[j] = (row[j] + above) % 256
        elif f == 3:
            for j in range(len(row)):
                prior = row[j - channels] if j >= channels else 0
                above = raw[(y - 1) * stride + j] if y > 0 else 0
                avg = (prior + above) // 2
                row[j] = (row[j] + avg) % 256
        elif f == 4:
            for j in range(len(row)):
                a = row[j - channels] if j >= channels else 0
                b = raw[(y - 1) * stride + j] if y > 0 else 0
                c = raw[(y - 1) * stride + j - channels] if y > 0 and j >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[j] = (row[j] + pr) % 256
        raw.extend(row)
    return raw

def convert_png_to_mono(png, out):
    enforce_extension(png, [".png"])
    enforce_extension(out, [".mono"])
    image = Image.open(png).convert("RGBA")
    width, height = image.size
    raw = image.tobytes()
    channels = 4

    # Find best filter type (0–4)
    best_compressed = None
    best_filter = 0
    min_size = float('inf')
    for ftype in range(5):
        filtered = apply_filter(raw, width, height, channels, ftype)
        compressed = zlib.compress(bytes(filtered), level=9)
        if len(compressed) < min_size:
            min_size = len(compressed)
            best_compressed = compressed
            best_filter = ftype

    if input("🔐 Encrypt file? (y/n): ").lower() == "y":
        password = getpass("Enter password: ")
        best_compressed = Encryptor.encrypt(best_compressed, password)

    with open(out, "wb") as f:
        f.write(width.to_bytes(4, "big"))
        f.write(height.to_bytes(4, "big"))
        f.write(bytes([best_filter]))
        f.write(best_compressed)# type: ignore
    print(f"✅ Saved .mono: {out}")

def convert_mono_bytes_to_png(mono_path, png_path):
    enforce_extension(mono_path, [".mono"])
    enforce_extension(png_path, [".png"])
    with open(mono_path, "rb") as f:
        width = int.from_bytes(f.read(4), "big")
        height = int.from_bytes(f.read(4), "big")
        filter_type = int.from_bytes(f.read(1), "big")
        data = f.read()

    try:
        data = Encryptor.decrypt(data, getpass("Enter password (leave blank if not encrypted): "))
    except:
        print("🔓 Decryption failed or not encrypted. Using raw data.")

    filtered = zlib.decompress(data)
    raw = reverse_filter(filtered, width, height, 4, filter_type)
    img = Image.frombytes("RGBA", (width, height), bytes(raw))
    img.save(png_path)
    print(f"✅ Restored PNG: {png_path}")

def view_mono_file(path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        convert_mono_bytes_to_png(path, tmp.name)
        Image.open(tmp.name).show()
        time.sleep(1.5)
        os.remove(tmp.name)

def main():
    print("🎨 Mono Image Tool with Max Compression")
    print("Commands: pngtomono, monotopng, monoview, compare, monopl, quit")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "pngtomono":
            convert_png_to_mono(input("PNG path: "), input("Output .mono path: "))
        elif cmd == "monotopng":
            convert_mono_bytes_to_png(input(".mono path: "), input("Output PNG path: "))
        elif cmd == "monoview":
            view_mono_file(input(".mono path: "))
        elif cmd == "monopl":
            MonoPL().run()
        elif cmd == "compare":
            os.makedirs("_MONOTEMP", exist_ok=True)
            png_path = input("PNG Path: ")
            temp_path = "_MONOTEMP/TEMPCOMPARE.mono"
            convert_png_to_mono(png_path, temp_path)
            mono_size = os.path.getsize(temp_path)
            png_size = os.path.getsize(png_path)
            print(f"PNG SIZE: {png_size}")
            print(f"MONO SIZE: {mono_size}")
            if mono_size < png_size:
                print(".Mono is more storage efficient!")
            else:
                print(".Mono is less storage efficient..")
            os.remove(temp_path)
        elif cmd == "quit":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Unknown command. Commands: pngtomono, monotopng, monoview, compare, monopl, quit")

if __name__ == "__main__":
    main()
