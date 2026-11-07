"""
app.py — ส่วนติดต่อผู้ใช้แบบข้อความ (Text UI) ของโรงแรมอนันต์แบบกระจาย

วิธีรัน (จากโฟลเดอร์ OOD-Project):
    python app.py

หลักการออกแบบ
- ตรรกะทั้งหมดอยู่ใน HotelSystem ไฟล์นี้ทำหน้าที่รับคำสั่ง แสดงผล และบันทึกไฟล์เท่านั้น
- ข้อมูลจริงอยู่ในหน่วยความจำ (AVL Tree) ส่วน CSV เป็น "สำเนาที่บันทึกไว้"
  โหลดตอนเปิดโปรแกรม และบันทึกหลังทุกคำสั่งที่เปลี่ยนข้อมูล (ปิดได้)
- ตอนโหลด อ่านเฉพาะรหัสแขก (c, s) แล้วคำนวณอาคารใหม่จากวงแหวนเสมอ
  (กติกา 4.1 ข้อ 2: ห้ามอาศัยตารางคำตอบที่บันทึกไว้) node_id ในไฟล์ใช้ตรวจสอบเท่านั้น

ไฟล์ที่ใช้เก็บข้อมูล (โฟลเดอร์ data/)
    config.json     ค่า hash_type, V, salt ของอาคารและแขก
    buildings.csv   building_id เรียงตามลำดับที่เพิ่ม (จำเป็นสำหรับ hash mod N)
    guests.csv      channel_id, sequence_id, node_id, room_no
"""

import contextlib
import csv
import io
import json
import math
import os
import sys
import time
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)                 # csv_sys เขียนไฟล์แบบอ้างอิง "CSV/..." จาก cwd
sys.path.insert(0, str(BASE_DIR))

from hotel_sys import HotelSystem  # noqa: E402
from util.csv_sys import (         # noqa: E402
    create_customer_csv,
    create_moved_customer_csv,
    create_node_csv,
    count_line_csv,
)

DATA_DIR = BASE_DIR / "data"
EXPORT_SUBDIR = "app_output"       # ส่งออกไปที่ CSV/app_output/
PAGE_SIZE = 20                     # จำนวนแถวต่อหน้าเวลาแสดงรายการ
PREVIEW = 20                       # จำนวนรายการย้ายที่แสดงบนจอ

HASH_LABEL = {"consistent": "Consistent Hashing", "mod_n": "hash mod N"}


# ════════════════════════════════════════════════════════════════════
#  การแสดงผล
# ════════════════════════════════════════════════════════════════════

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass
if os.name == "nt":
    os.system("")                  # เปิดโหมดสี ANSI บน Windows Terminal / cmd

USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def ok(text):     print(_c("32", "✔ " + text))
def err(text):    print(_c("31", "✘ " + text))
def warn(text):   print(_c("33", "! " + text))
def info(text):   print(_c("36", text))
def dim(text):    return _c("2", text)


def header(text):
    print("\n" + _c("1;35", f"── {text} ──"))


def display_width(text):
    """ความกว้างบนจอ — สระ/วรรณยุกต์ไทยที่อยู่บนหรือล่างบรรทัดไม่กินที่"""
    return sum(0 if unicodedata.category(ch) in ("Mn", "Me", "Cf") else 1 for ch in text)


def pad(text, width, right=False):
    text = str(text)
    space = " " * max(0, width - display_width(text))
    return space + text if right else text + space


def print_table(headers, rows, right_cols=()):
    rows = [[str(x) for x in r] for r in rows]
    widths = [display_width(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], display_width(cell))
    line = "  ".join(pad(h, widths[i], i in right_cols) for i, h in enumerate(headers))
    print("  " + _c("1", line))
    print("  " + "  ".join("─" * w for w in widths))
    for r in rows:
        print("  " + "  ".join(pad(cell, widths[i], i in right_cols) for i, cell in enumerate(r)))


def fmt_ms(seconds):
    return f"{seconds * 1000:,.2f} ms"


@contextlib.contextmanager
def quiet():
    """ปิดข้อความ [INVALID] ที่ HotelSystem พิมพ์เอง แล้วให้ app แสดงข้อความภาษาไทยแทน"""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ════════════════════════════════════════════════════════════════════
#  การรับข้อมูล
# ════════════════════════════════════════════════════════════════════

class Cancel(Exception):
    """ผู้ใช้เว้นว่างเพื่อยกเลิกคำสั่ง แล้วกลับเมนูหลัก"""


def ask(prompt, default=None, optional=False):
    hint = f" [{default}]" if default is not None else ""
    raw = input(f"  {prompt}{hint}: ").strip()
    if raw == "":
        if default is not None:
            return str(default)
        if optional:
            return None
        raise Cancel
    return raw


def ask_int(prompt, min_value=None, max_value=None, default=None, optional=False):
    while True:
        raw = ask(prompt, default, optional)
        if raw is None:
            return None
        try:
            value = int(raw)
        except ValueError:
            err("กรุณาใส่จำนวนเต็ม")
            continue
        if min_value is not None and value < min_value:
            err(f"ค่าต้องไม่น้อยกว่า {min_value}")
            continue
        if max_value is not None and value > max_value:
            err(f"ค่าต้องไม่เกิน {max_value}")
            continue
        return value


def ask_yes_no(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"  {prompt} ({hint}): ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes", "ใช่"):
            return True
        if raw in ("n", "no", "ไม่"):
            return False
        err("กรุณาตอบ y หรือ n")


def cancel_hint():
    print(dim("  (เว้นว่างแล้วกด Enter เพื่อยกเลิก)"))


# ════════════════════════════════════════════════════════════════════
#  การบันทึก/โหลดไฟล์ CSV
# ════════════════════════════════════════════════════════════════════

def _atomic_write(path, write_fn):
    """เขียนลงไฟล์ชั่วคราวก่อน แล้วค่อยแทนที่ไฟล์จริง ถ้าโปรแกรมล่มกลางคัน ไฟล์เดิมไม่เสีย"""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        write_fn(f)
    os.replace(tmp, path)


GUEST_COLUMNS = ["channel_id", "sequence_id", "node_id", "room_no"]


class Store:
    def __init__(self, data_dir):
        self.dir = data_dir
        self.config_file = data_dir / "config.json"
        self.buildings_file = data_dir / "buildings.csv"
        self.guests_file = data_dir / "guests.csv"

    def exists(self):
        return self.config_file.exists() and self.buildings_file.exists()

    def save_config(self, cfg):
        self.dir.mkdir(parents=True, exist_ok=True)
        _atomic_write(self.config_file,
                      lambda f: json.dump(cfg, f, ensure_ascii=False, indent=2))

    def save_buildings(self, building_ids):
        self.dir.mkdir(parents=True, exist_ok=True)

        def write(f):
            w = csv.writer(f)
            w.writerow(["building_id"])
            w.writerows([b] for b in building_ids)
        _atomic_write(self.buildings_file, write)

    def save_guests(self, customers):
        """เขียนใหม่ทั้งไฟล์ — O(K)"""
        self.dir.mkdir(parents=True, exist_ok=True)

        def write(f):
            w = csv.writer(f)
            w.writerow(GUEST_COLUMNS)
            for c in customers:
                w.writerow([c.id[0], c.id[1], c.node_id, c.room_no])
        _atomic_write(self.guests_file, write)

    def append_guests(self, customers):
        """ต่อท้ายไฟล์ — O(จำนวนแขกที่เพิ่ม)"""
        self.dir.mkdir(parents=True, exist_ok=True)
        new_file = not self.guests_file.exists()
        with open(self.guests_file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(GUEST_COLUMNS)
            for c in customers:
                w.writerow([c.id[0], c.id[1], c.node_id, c.room_no])

    def load(self):
        with open(self.config_file, encoding="utf-8") as f:
            cfg = json.load(f)
        for key in ("hash_type", "V", "building_salt", "customer_salt"):
            if key not in cfg:
                raise ValueError(f"config.json ไม่มีคีย์ '{key}'")
        if cfg["hash_type"] not in HASH_LABEL:
            raise ValueError(f"hash_type ไม่รู้จัก: {cfg['hash_type']}")
        cfg["V"] = int(cfg["V"])
        if cfg["V"] < 1:
            raise ValueError("V ต้องมากกว่าหรือเท่ากับ 1")
        cfg["building_salt"] = str(cfg["building_salt"])
        cfg["customer_salt"] = str(cfg["customer_salt"])

        building_ids = []
        with open(self.buildings_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                bid = int(row["building_id"])
                if bid not in building_ids:
                    building_ids.append(bid)
        if not building_ids:
            raise ValueError("buildings.csv ไม่มีอาคาร (ต้องมีอย่างน้อย 1 หลัง)")

        guests, bad_rows = [], 0
        if self.guests_file.exists():
            with open(self.guests_file, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        c, s = int(row["channel_id"]), int(row["sequence_id"])
                        if c < 1 or s < 1:
                            raise ValueError
                        node = row.get("node_id")
                        saved_node = int(node) if node not in (None, "") else None
                        guests.append((c, s, saved_node))
                    except (ValueError, TypeError, KeyError):
                        bad_rows += 1
        return cfg, building_ids, guests, bad_rows


def build_hotel(cfg, building_ids, guest_ids):
    """สร้าง HotelSystem ใหม่จากค่าตั้งต้น รายการอาคาร และรหัสแขก — คืน (hotel, จำนวนแขกที่เพิ่มได้)"""
    hotel = HotelSystem(cfg["V"], cfg["building_salt"], cfg["customer_salt"], cfg["hash_type"])
    added = 0
    with quiet():
        for bid in building_ids:
            hotel.add_building(bid)
        for c, s in guest_ids:
            if hotel.add_customer(c, s):
                added += 1
    return hotel, added


def find_guest(hotel, c, s):
    with quiet():
        return hotel.search_customer_by_id(c, s)


# ════════════════════════════════════════════════════════════════════
#  แอปพลิเคชัน
# ════════════════════════════════════════════════════════════════════

class HotelApp:
    def __init__(self):
        self.store = Store(DATA_DIR)
        self.hotel = None
        self.cfg = None
        self.buildings = []        # รหัสอาคารตามลำดับที่เพิ่ม
        self.k = 0                 # จำนวนแขกปัจจุบัน
        self.autosave = True
        self.dirty = False         # มีการเปลี่ยนแปลงที่ยังไม่บันทึก

        self.menu = [
            ("1", "เพิ่มแขก 1 คน", self.add_guest),
            ("2", "เพิ่มแขกเป็นกลุ่ม", self.add_group),
            ("3", "นำแขกออก", self.remove_guest),
            ("4", "ค้นหาด้วยรหัสแขก (c, s)", self.search_by_id),
            ("5", "ค้นหาด้วยอาคาร + ห้อง", self.search_by_room),
            ("6", "เพิ่มอาคาร", self.add_building),
            ("7", "ลบอาคาร", self.remove_building),
            ("8", "แสดงรายการห้องที่มีผู้พัก", self.list_rooms),
            ("9", "รายงานความสมดุลของโหลด", self.load_report),
            ("10", "ส่งออก CSV", self.export_csv),
            ("11", "เปรียบเทียบกับ hash mod N", self.compare_mod_n),
            ("12", "บันทึกตอนนี้", self.save_now),
            ("13", "เปิด/ปิดบันทึกอัตโนมัติ", self.toggle_autosave),
        ]

    # ── เริ่มระบบ ────────────────────────────────────────────────────

    def startup(self):
        header("โรงแรมอนันต์แบบกระจาย (Distributed Hilbert's Hotel)")
        if self.store.exists():
            if ask_yes_no(f"พบข้อมูลที่บันทึกไว้ใน {DATA_DIR.name}/ ต้องการโหลดหรือไม่", True):
                if self.load():
                    return
                warn("โหลดไม่สำเร็จ จะเริ่มตั้งค่าระบบใหม่")
            else:
                warn("ข้อมูลเดิมใน data/ จะถูกเขียนทับเมื่อบันทึก")
        self.setup_wizard()

    def setup_wizard(self):
        header("ตั้งค่าระบบใหม่")
        print("  วิธีเลือกอาคาร:  1) Consistent Hashing   2) hash mod N")
        choice = ask_int("เลือก", 1, 2, default=1)
        hash_type = "consistent" if choice == 1 else "mod_n"
        if hash_type == "consistent":
            v = ask_int("จำนวน virtual node ต่ออาคาร (V)", 1, default=32)
        else:
            v = 32                 # ไม่ใช้ใน mod N แต่เก็บไว้สำหรับเมนูเปรียบเทียบ
        n = ask_int("จำนวนอาคารเริ่มต้น (N)", 1, default=5)
        channels = ask_int("จำนวนช่องทาง", 0, default=3)
        per_channel = ask_int("จำนวนแขกต่อช่องทาง", 0, default=5) if channels > 0 else 0
        building_salt = ask("salt ของอาคาร", "b")
        customer_salt = ask("salt ของแขก", "c")

        self.cfg = {"hash_type": hash_type, "V": v,
                    "building_salt": building_salt, "customer_salt": customer_salt}
        self.buildings = list(range(1, n + 1))
        guest_ids = [(c, s) for c in range(1, channels + 1) for s in range(1, per_channel + 1)]

        t0 = time.perf_counter()
        self.hotel, self.k = build_hotel(self.cfg, self.buildings, guest_ids)
        elapsed = time.perf_counter() - t0

        ok(f"สร้างระบบแล้ว: อาคาร {n} หลัง, แขก {self.k:,} คน ({fmt_ms(elapsed)})")
        if hash_type == "consistent":
            info(f"  วงแหวนมี M = N × V = {n} × {v} = {n * v:,} จุด")
        self.save_all()

    def load(self):
        try:
            cfg, building_ids, guests, bad_rows = self.store.load()
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            err(f"อ่านไฟล์ไม่ได้: {e}")
            return False

        t0 = time.perf_counter()
        hotel, added = build_hotel(cfg, building_ids, [(c, s) for c, s, _ in guests])
        elapsed = time.perf_counter() - t0

        self.cfg, self.hotel, self.buildings, self.k = cfg, hotel, building_ids, added
        ok(f"โหลดแล้ว: อาคาร {len(building_ids)} หลัง, แขก {added:,} คน ({fmt_ms(elapsed)})")
        info(f"  วิธี: {HASH_LABEL[cfg['hash_type']]}"
             + (f", V = {cfg['V']}" if cfg["hash_type"] == "consistent" else "")
             + f", salt อาคาร = '{cfg['building_salt']}', salt แขก = '{cfg['customer_salt']}'")

        needs_rewrite = False
        if bad_rows:
            warn(f"ข้ามแถวที่อ่านไม่ได้ใน guests.csv {bad_rows} แถว")
            needs_rewrite = True
        duplicates = len(guests) - added
        if duplicates:
            warn(f"พบรหัสแขกซ้ำในไฟล์ {duplicates} แถว (เก็บไว้เพียงรายการเดียว)")
            needs_rewrite = True

        # ตรวจว่า node_id ในไฟล์ตรงกับที่คำนวณจากวงแหวนปัจจุบันหรือไม่
        mismatch = 0
        for c, s, saved_node in guests:
            if saved_node is None:
                continue
            guest = find_guest(hotel, c, s)
            if guest is not None and guest.node_id != saved_node:
                mismatch += 1
        if mismatch:
            warn(f"แขก {mismatch} คนมี node_id ในไฟล์ไม่ตรงกับที่คำนวณจากวงแหวน — ใช้ค่าที่คำนวณใหม่")
            needs_rewrite = True
        else:
            ok("node_id ในไฟล์ตรงกับที่คำนวณจากวงแหวนทุกคน")

        if needs_rewrite:
            self.persist()
        return True

    # ── การบันทึก ─────────────────────────────────────────────────────

    def save_all(self):
        try:
            self.store.save_config(self.cfg)
            self.store.save_buildings(self.buildings)
            self.store.save_guests(self.hotel.get_customers())
            self.dirty = False
            return True
        except OSError as e:
            err(f"บันทึกไฟล์ไม่สำเร็จ: {e}")
            self.dirty = True
            return False

    def persist(self, appended=None, buildings_changed=False):
        """บันทึกหลังคำสั่งที่เปลี่ยนข้อมูล — ต่อท้ายไฟล์ได้ถ้าเป็นการเพิ่มแขกอย่างเดียว"""
        if not self.autosave:
            self.dirty = True
            return
        try:
            if appended is not None and not buildings_changed and not self.dirty:
                self.store.append_guests(appended)
            else:
                if buildings_changed or self.dirty:
                    self.store.save_buildings(self.buildings)
                self.store.save_guests(self.hotel.get_customers())
            self.dirty = False
        except OSError as e:
            err(f"บันทึกไฟล์ไม่สำเร็จ: {e}")
            self.dirty = True

    def save_now(self):
        header("บันทึกตอนนี้")
        t0 = time.perf_counter()
        if self.save_all():
            ok(f"บันทึกลง {DATA_DIR.name}/ แล้ว ({self.k:,} แขก, {fmt_ms(time.perf_counter() - t0)})")

    def toggle_autosave(self):
        self.autosave = not self.autosave
        if self.autosave:
            ok("เปิดบันทึกอัตโนมัติ")
            if self.dirty:
                self.save_now()
        else:
            ok("ปิดบันทึกอัตโนมัติ — ใช้เมนู 12 เพื่อบันทึกเอง (แนะนำเมื่อ K มีขนาดใหญ่)")

    # ── แขก ───────────────────────────────────────────────────────────

    def add_guest(self):
        header("เพิ่มแขก 1 คน")
        cancel_hint()
        c = ask_int("ช่องทาง c", 1)
        s = ask_int("ลำดับ s", 1)
        with quiet():
            added = self.hotel.add_customer(c, s)
        if not added:
            err(f"มีแขกรหัส ({c}, {s}) อยู่ในระบบแล้ว — ไม่มีการเปลี่ยนแปลง")
            return
        guest = find_guest(self.hotel, c, s)
        self.k += 1
        ok(f"เพิ่มแขก ({c}, {s}) → อาคาร {guest.node_id} ห้อง {guest.room_no}")
        self.persist(appended=[guest])

    def add_group(self):
        header("เพิ่มแขกเป็นกลุ่ม")
        cancel_hint()
        c = ask_int("ช่องทาง c", 1)
        s_start = ask_int("ลำดับเริ่มต้น s_start", 1)
        n = ask_int("จำนวนแขก", 0)
        if n == 0:
            info("  จำนวน 0 คน — ไม่มีการเปลี่ยนแปลง")
            return

        conflicts = [s for s in range(s_start, s_start + n) if find_guest(self.hotel, c, s)]
        if conflicts:
            sample = ", ".join(f"({c}, {s})" for s in conflicts[:5])
            more = f" และอีก {len(conflicts) - 5} รายการ" if len(conflicts) > 5 else ""
            err(f"รหัสซ้ำกับแขกที่มีอยู่ {len(conflicts)} รายการ: {sample}{more}")
            err("ปฏิเสธทั้งกลุ่ม ข้อมูลเดิมไม่เปลี่ยน")
            return

        t0 = time.perf_counter()
        with quiet():
            success = self.hotel.add_group_customer(c, s_start, n)
        elapsed = time.perf_counter() - t0
        if not success:
            err("เพิ่มกลุ่มไม่สำเร็จ ข้อมูลเดิมไม่เปลี่ยน")
            return

        added = [find_guest(self.hotel, c, s) for s in range(s_start, s_start + n)]
        self.k += n
        ok(f"เพิ่มแขก {n:,} คน ({c}, {s_start}) – ({c}, {s_start + n - 1}) ({fmt_ms(elapsed)})")
        print_table(["รหัสแขก", "อาคาร", "ห้อง"],
                    [[f"({g.id[0]}, {g.id[1]})", g.node_id, g.room_no] for g in added[:PREVIEW]],
                    right_cols=(1, 2))
        if n > PREVIEW:
            info(f"  แสดง {PREVIEW} จาก {n:,} รายการ")
        self.persist(appended=added)

    def remove_guest(self):
        header("นำแขกออก")
        cancel_hint()
        c = ask_int("ช่องทาง c", 1)
        s = ask_int("ลำดับ s", 1)
        guest = find_guest(self.hotel, c, s)
        if guest is None:
            err(f"ไม่พบแขกรหัส ({c}, {s}) — ไม่มีการเปลี่ยนแปลง")
            return
        node_id, room_no = guest.node_id, guest.room_no
        with quiet():
            removed = self.hotel.remove_customer(c, s)
        if not removed:
            err(f"นำแขก ({c}, {s}) ออกไม่สำเร็จ")
            return
        self.k -= 1
        ok(f"นำแขก ({c}, {s}) ออกจากอาคาร {node_id} ห้อง {room_no} แล้ว")
        self.persist()

    def search_by_id(self):
        header("ค้นหาด้วยรหัสแขก")
        cancel_hint()
        c = ask_int("ช่องทาง c", 1)
        s = ask_int("ลำดับ s", 1)
        guest = find_guest(self.hotel, c, s)
        if guest is None:
            err(f"ไม่พบแขกรหัส ({c}, {s}) ในระบบ")
            return
        print_table(["รหัสแขก", "อาคาร", "ห้อง"],
                    [[f"({c}, {s})", guest.node_id, guest.room_no]], right_cols=(1, 2))

    def search_by_room(self):
        header("ค้นหาด้วยอาคาร + ห้อง")
        cancel_hint()
        node_id = ask_int("รหัสอาคาร", 1)
        room_no = ask_int("หมายเลขห้อง", 1)
        if node_id not in self.buildings:
            err(f"ไม่มีอาคาร {node_id} ในระบบ (อาคารที่มี: {self.building_list_text()})")
            return
        with quiet():
            guest = self.hotel.search_customer_by_room(node_id, room_no)
        if guest is None:
            err(f"อาคาร {node_id} ห้อง {room_no} ไม่มีผู้พัก")
            return
        print_table(["อาคาร", "ห้อง", "รหัสแขก"],
                    [[node_id, room_no, f"({guest.id[0]}, {guest.id[1]})"]], right_cols=(0, 1))

    def list_rooms(self):
        header("รายการห้องที่มีผู้พัก")
        cancel_hint()
        node_filter = ask_int("กรองเฉพาะอาคาร (เว้นว่าง = ทุกอาคาร)", 1, optional=True)
        guests = self.hotel.get_customers()   # เรียงตาม (node_id, room_no) แล้ว
        if node_filter is not None:
            guests = [g for g in guests if g.node_id == node_filter]
        total = len(guests)
        scope = f"อาคาร {node_filter}" if node_filter is not None else "ทุกอาคาร"
        if total == 0:
            info(f"  ไม่มีผู้พักใน{scope}")
            return

        info(f"  {scope}: ทั้งหมด {total:,} ห้อง")
        for start in range(0, total, PAGE_SIZE):
            page = guests[start:start + PAGE_SIZE]
            print_table(["ลำดับ", "อาคาร", "ห้อง", "รหัสแขก"],
                        [[start + i + 1, g.node_id, g.room_no, f"({g.id[0]}, {g.id[1]})"]
                         for i, g in enumerate(page)],
                        right_cols=(0, 1, 2))
            end = start + len(page)
            if end >= total:
                break
            raw = input(f"  แสดง {end:,}/{total:,} — Enter = หน้าถัดไป, q = กลับเมนู: ").strip().lower()
            if raw == "q":
                break

    # ── อาคาร ─────────────────────────────────────────────────────────

    def building_list_text(self):
        return ", ".join(map(str, sorted(self.buildings)))

    def add_building(self):
        header("เพิ่มอาคาร")
        info(f"  อาคารปัจจุบัน: {self.building_list_text()}")
        cancel_hint()
        bid = ask_int("รหัสอาคารใหม่", 1)
        if bid in self.buildings:
            err(f"มีอาคาร {bid} อยู่แล้ว — ไม่มีการเปลี่ยนแปลง")
            return

        n_before, k = len(self.buildings), self.k
        t0 = time.perf_counter()
        with quiet():
            moves = self.hotel.add_building(bid)
        elapsed = time.perf_counter() - t0
        if moves is None:
            err("เพิ่มอาคารไม่สำเร็จ")
            return

        self.buildings.append(bid)
        ok(f"เพิ่มอาคาร {bid} แล้ว (N: {n_before} → {n_before + 1})")
        self.report_moves(moves, k, elapsed,
                          expected=k / (n_before + 1),
                          rule_ok=all(m.new_node_id == bid for m in moves),
                          rule_text=f"ผู้ย้ายทุกคนย้ายเข้าอาคารใหม่ ({bid}) เท่านั้น",
                          tag=f"add_{bid}")
        self.persist(buildings_changed=True)

    def remove_building(self):
        header("ลบอาคาร")
        info(f"  อาคารปัจจุบัน: {self.building_list_text()}")
        cancel_hint()
        bid = ask_int("รหัสอาคารที่จะลบ", 1)
        if bid not in self.buildings:
            err(f"ไม่มีอาคาร {bid} ในระบบ — ไม่มีการเปลี่ยนแปลง")
            return
        if len(self.buildings) == 1:
            err("ลบอาคารสุดท้ายไม่ได้ (ต้องมีอย่างน้อย 1 หลัง, N ≥ 1)")
            return

        n_before, k = len(self.buildings), self.k
        t0 = time.perf_counter()
        with quiet():
            moves = self.hotel.remove_building(bid)
        elapsed = time.perf_counter() - t0
        if moves is None:
            err("ลบอาคารไม่สำเร็จ")
            return

        self.buildings.remove(bid)
        ok(f"ลบอาคาร {bid} แล้ว (N: {n_before} → {n_before - 1})")
        self.report_moves(moves, k, elapsed,
                          expected=k / n_before,
                          rule_ok=all(m.old_node_id == bid for m in moves),
                          rule_text=f"ผู้ย้ายทุกคนมาจากอาคารที่ถูกลบ ({bid}) เท่านั้น",
                          tag=f"remove_{bid}")
        self.persist(buildings_changed=True)

    def report_moves(self, moves, k, elapsed, expected, rule_ok, rule_text, tag):
        moved = len(moves)
        print()
        if k > 0:
            info(f"  แขกที่ย้าย: {moved:,} จาก {k:,} คน  (อัตราการย้าย {moved / k:.2%})")
            if self.cfg["hash_type"] == "consistent":
                info(f"  ค่าคาดหวังโดยประมาณ: {expected:,.1f} คน (ไม่จำเป็นต้องตรงทุกครั้ง)")
        else:
            info("  แขกที่ย้าย: 0 คน — ไม่มีแขกในระบบ (K = 0) จึงไม่คำนวณอัตราการย้าย")
        info(f"  เวลาที่ใช้: {fmt_ms(elapsed)} (ไม่รวมการบันทึกไฟล์)")

        if moved and self.cfg["hash_type"] == "consistent":
            (ok if rule_ok else err)(("ผ่านกติกา: " if rule_ok else "ผิดกติกา: ") + rule_text)

        if moved == 0:
            return
        print_table(["รหัสแขก", "ห้อง", "อาคารเดิม", "อาคารใหม่"],
                    [[f"({m.id[0]}, {m.id[1]})", m.room_no, m.old_node_id, m.new_node_id]
                     for m in moves[:PREVIEW]],
                    right_cols=(1, 2, 3))
        if moved > PREVIEW:
            info(f"  แสดง {PREVIEW} จาก {moved:,} รายการ")
        if ask_yes_no("ส่งออกรายการย้ายทั้งหมดเป็น CSV หรือไม่", False):
            name = f"{EXPORT_SUBDIR}/moved_{tag}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                (Path("CSV") / EXPORT_SUBDIR).mkdir(parents=True, exist_ok=True)
                create_moved_customer_csv(name, moves)
                ok(f"บันทึกที่ CSV/{name} ({count_line_csv(name):,} แถว)")
            except OSError as e:
                err(f"ส่งออกไม่สำเร็จ: {e}")

    # ── รายงานและการส่งออก ───────────────────────────────────────────

    def load_report(self):
        header("รายงานความสมดุลของโหลด")
        counts = {bid: 0 for bid in self.buildings}
        for g in self.hotel.get_customers():
            counts[g.node_id] = counts.get(g.node_id, 0) + 1

        values = list(counts.values())
        k = sum(values)
        top = max(values) if values else 0
        bar_width = 30
        rows = []
        for bid in sorted(counts):
            cnt = counts[bid]
            share = f"{cnt / k:.1%}" if k else "-"
            bar = "█" * (round(cnt / top * bar_width) if top else 0)
            rows.append([bid, f"{cnt:,}", share, bar])
        print_table(["อาคาร", "จำนวนแขก", "สัดส่วน", ""], rows, right_cols=(0, 1, 2))

        print()
        if k == 0:
            info("  ไม่มีแขกในระบบ (K = 0): สูงสุด 0, ต่ำสุด 0, เฉลี่ย 0, SD 0 — ไม่คำนวณ CV")
            return
        mean = k / len(values)
        sd = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
        info(f"  อาคาร N = {len(values)}, แขก K = {k:,}")
        info(f"  สูงสุด {max(values):,} | ต่ำสุด {min(values):,} | เฉลี่ย {mean:,.2f} | "
             f"SD {sd:,.2f} | CV {sd / mean:.4f}")
        print(dim("  (SD แบบประชากร, CV = SD / ค่าเฉลี่ย — ยิ่งต่ำยิ่งสมดุล)"))

    def export_csv(self):
        header("ส่งออก CSV")
        stamp = time.strftime("%Y%m%d_%H%M%S")
        customers_file = f"{EXPORT_SUBDIR}/customers_{stamp}.csv"
        rooms_file = f"{EXPORT_SUBDIR}/buildings_with_rooms_{stamp}.csv"
        try:
            (Path("CSV") / EXPORT_SUBDIR).mkdir(parents=True, exist_ok=True)
            create_customer_csv(customers_file, self.hotel.get_customers())
            create_node_csv(rooms_file, self.hotel.get_buildings_with_rooms())
            lines = count_line_csv(customers_file)
        except OSError as e:
            err(f"ส่งออกไม่สำเร็จ: {e}")
            return
        ok(f"CSV/{customers_file}")
        ok(f"CSV/{rooms_file}")
        if lines == self.k:
            ok(f"จำนวนแถวในไฟล์ ({lines:,}) เท่ากับจำนวนแขกในระบบ")
        else:
            err(f"จำนวนแถวในไฟล์ ({lines:,}) ไม่เท่ากับจำนวนแขกในระบบ ({self.k:,})")

    def compare_mod_n(self):
        header("เปรียบเทียบ Consistent Hashing กับ hash mod N")
        print(dim("  ใช้ชุดแขก อาคาร และ salt เดียวกัน — จำลองบนสำเนา ระบบจริงไม่เปลี่ยน"))
        info(f"  อาคารปัจจุบัน: {self.building_list_text()} | แขก K = {self.k:,}")
        cancel_hint()
        op = ask_int("1) เพิ่มอาคาร  2) ลบอาคาร", 1, 2, default=1)
        bid = ask_int("รหัสอาคาร", 1)
        if op == 1 and bid in self.buildings:
            err(f"มีอาคาร {bid} อยู่แล้ว")
            return
        if op == 2 and bid not in self.buildings:
            err(f"ไม่มีอาคาร {bid} ในระบบ")
            return
        if op == 2 and len(self.buildings) == 1:
            err("ลบอาคารสุดท้ายไม่ได้")
            return

        guest_ids = [g.id for g in self.hotel.get_customers()]
        n, k = len(self.buildings), self.k
        expected = k / (n + 1) if op == 1 else k / n
        info("  กำลังจำลอง...")

        rows = []
        for hash_type in ("consistent", "mod_n"):
            cfg = dict(self.cfg, hash_type=hash_type)
            sim, _ = build_hotel(cfg, self.buildings, guest_ids)
            t0 = time.perf_counter()
            with quiet():
                moves = sim.add_building(bid) if op == 1 else sim.remove_building(bid)
            elapsed = time.perf_counter() - t0
            moved = len(moves)
            if op == 1:
                rule = all(m.new_node_id == bid for m in moves)
            else:
                rule = all(m.old_node_id == bid for m in moves)
            label = HASH_LABEL[hash_type] + (f" (V={cfg['V']})" if hash_type == "consistent" else "")
            rows.append([label, f"{moved:,}",
                         f"{moved / k:.2%}" if k else "-",
                         fmt_ms(elapsed),
                         "ใช่" if rule else "ไม่"])

        action = f"เพิ่มอาคาร {bid}" if op == 1 else f"ลบอาคาร {bid}"
        print()
        info(f"  {action}: N {n} → {n + 1 if op == 1 else n - 1}, K = {k:,}")
        print_table(["วิธี", "ย้าย (คน)", "อัตราย้าย", "เวลา", "ย้ายเฉพาะอาคารที่เกี่ยวข้อง"],
                    rows, right_cols=(1, 2, 3))
        if k:
            print(dim(f"  ค่าคาดหวังของ Consistent Hashing ≈ {expected:,.1f} คน "
                      f"({'K/(N+1)' if op == 1 else 'K/N'})"))
        else:
            print(dim("  K = 0 จึงไม่คำนวณอัตราการย้าย"))

    # ── วงจรหลัก ─────────────────────────────────────────────────────

    def status_line(self):
        method = HASH_LABEL[self.cfg["hash_type"]]
        if self.cfg["hash_type"] == "consistent":
            method += f" (V={self.cfg['V']})"
        save = "เปิด" if self.autosave else "ปิด"
        if self.dirty:
            save += _c("33", " • ยังไม่บันทึก")
        return (f"อาคาร {len(self.buildings)} หลัง | แขก {self.k:,} คน | "
                f"{method} | บันทึกอัตโนมัติ: {save}")

    def print_menu(self):
        header("เมนูหลัก")
        print("  " + dim(self.status_line()))
        half = (len(self.menu) + 1) // 2
        left, right = self.menu[:half], self.menu[half:]
        width = max(display_width(f"{k:>2}) {label}") for k, label, _ in left) + 4
        for i in range(half):
            line = pad(f"{left[i][0]:>2}) {left[i][1]}", width)
            if i < len(right):
                line += f"{right[i][0]:>2}) {right[i][1]}"
            print("  " + line)
        print("   0) ออกจากโปรแกรม")

    def exit(self, interactive=True):
        if self.dirty:
            if not interactive or ask_yes_no("มีข้อมูลที่ยังไม่บันทึก ต้องการบันทึกก่อนออกหรือไม่", True):
                self.save_all()
        print("ลาก่อน 👋")

    def run(self):
        try:
            self.startup()
        except (EOFError, KeyboardInterrupt):
            print("\nยกเลิกการเริ่มระบบ")
            return

        actions = {key: fn for key, _, fn in self.menu}
        while True:
            self.print_menu()
            try:
                choice = input("\nเลือกเมนู: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                self.exit(interactive=False)
                return
            if choice == "0":
                try:
                    self.exit()
                except (EOFError, KeyboardInterrupt):
                    self.exit(interactive=False)
                return
            action = actions.get(choice)
            if action is None:
                err("ไม่มีเมนูนี้ กรุณาเลือก 0–13")
                continue
            try:
                action()
            except Cancel:
                info("  ยกเลิก กลับเมนูหลัก")
            except KeyboardInterrupt:
                print()
                info("  ยกเลิก กลับเมนูหลัก")
            except EOFError:
                print()
                self.exit(interactive=False)
                return
            except Exception as e:  # โปรแกรมต้องไม่หยุดทำงาน (หัวข้อ 4.5)
                err(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {type(e).__name__}: {e}")


if __name__ == "__main__":
    HotelApp().run()