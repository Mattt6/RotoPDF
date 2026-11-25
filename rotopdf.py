"""
RotoPDF - extrait des images d'une vidéo et les met, numérotées, dans un PDF.

Réglages : fps de sortie (images par seconde de vidéo) et nombre d'images par page.
Dépendances : opencv-python, pillow, reportlab, customtkinter

Copyright (C) 2026 Mattt6

Ce programme est un logiciel libre : vous pouvez le redistribuer et/ou le
modifier selon les termes de la licence publique générale GNU publiée par la
Free Software Foundation, version 3 de la licence, ou (à votre choix) toute
version ultérieure.

Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE
GARANTIE, sans même la garantie implicite de COMMERCIALISATION ou
d'ADÉQUATION À UN USAGE PARTICULIER. Voir la licence publique générale GNU
pour plus de détails (fichier LICENSE).
"""
import math
import os
import queue
import shutil
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

import cv2
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

MAX_W = 1280          # largeur max des images stockées (limite le poids du PDF)
MARGIN = 36           # marges de page (points)
GAP = 8               # espace entre images
LABEL_H = 16          # hauteur réservée au numéro sous chaque image


def fmt_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(int(m), 60)
    return f"{h:02d}:{m:02d}:{s:05.2f}"


def best_layout(n, aspect):
    """Choisit portrait/paysage et colonnes x lignes pour que les images soient les plus grandes."""
    best = None
    for landscape in (False, True):
        pw, ph = (A4[1], A4[0]) if landscape else A4
        aw, ah = pw - 2 * MARGIN, ph - 2 * MARGIN
        for cols in range(1, n + 1):
            rows = math.ceil(n / cols)
            cw = (aw - GAP * (cols - 1)) / cols
            row_h = (ah - GAP * (rows - 1)) / rows
            ch = row_h - LABEL_H
            if cw <= 0 or ch <= 0:
                continue
            iw = min(cw, ch * aspect)
            area = iw * (iw / aspect)
            if best is None or area > best["area"]:
                best = dict(area=area, pw=pw, ph=ph, cols=cols, rows=rows,
                            cw=cw, row_h=row_h, ch=ch)
    return best


def convert(video, out_pdf, fps_out, per_page, show_time, on_progress, cancel):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise RuntimeError("Impossible d'ouvrir la vidéo.")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    step = max(src_fps / fps_out, 1.0)

    tmp = tempfile.mkdtemp(prefix="rotopdf_")
    items = []  # (chemin, temps en secondes)
    try:
        idx, next_t = 0, 0.0
        while True:
            if cancel.is_set():
                return False
            if not cap.grab():
                break
            if idx >= next_t:
                ok, frame = cap.retrieve()
                if ok:
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    if img.width > MAX_W:
                        img = img.resize((MAX_W, round(img.height * MAX_W / img.width)),
                                         Image.LANCZOS)
                    path = os.path.join(tmp, f"{len(items):06d}.jpg")
                    img.save(path, quality=88)
                    items.append((path, idx / src_fps))
                next_t += step
            idx += 1
            if total and idx % 10 == 0:
                on_progress(50.0 * idx / total, f"Extraction des images… ({len(items)})")
        cap.release()

        if not items:
            raise RuntimeError("Aucune image extraite.")

        w, h = Image.open(items[0][0]).size
        aspect = w / h
        lay = best_layout(per_page, aspect)
        pw, ph = lay["pw"], lay["ph"]
        pages = math.ceil(len(items) / per_page)

        c = canvas.Canvas(out_pdf, pagesize=(pw, ph))
        c.setTitle(os.path.basename(video))
        for p in range(pages):
            if cancel.is_set():
                return False
            c.setPageSize((pw, ph))
            chunk = items[p * per_page:(p + 1) * per_page]
            for i, (path, t) in enumerate(chunk):
                r, col = divmod(i, lay["cols"])
                x0 = MARGIN + col * (lay["cw"] + GAP)
                y_top = ph - MARGIN - r * (lay["row_h"] + GAP)
                iw = min(lay["cw"], lay["ch"] * aspect)
                ih = iw / aspect
                c.drawImage(path, x0 + (lay["cw"] - iw) / 2, y_top - ih, iw, ih)
                n = p * per_page + i + 1
                label = f"n° {n}" + (f"  -  {fmt_time(t)}" if show_time else "")
                c.setFont("Helvetica-Bold", 9)
                c.drawCentredString(x0 + lay["cw"] / 2, y_top - ih - 11, label)
            c.showPage()
            on_progress(50.0 + 50.0 * (p + 1) / pages, f"Création du PDF… page {p + 1}/{pages}")
        c.save()
        return True
    finally:
        cap.release()
        shutil.rmtree(tmp, ignore_errors=True)


def res(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


ctk.set_appearance_mode("dark")
BG, CARD, FIELD = "#1c1c20", "#27272d", "#34343c"
ACCENT, ACCENT_H, MUTED = "#3b82f6", "#2563eb", "#9a9aa6"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RotoPDF")
        self.geometry("780x640")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.after(200, self._set_icon)

        self.msgs = queue.Queue()
        self.cancel = threading.Event()
        self.worker = None
        self.video = ""
        self.duration = None
        self.aspect = 16 / 9
        self.v_pdf = tk.StringVar()
        self.v_time = tk.BooleanVar(value=True)

        # --- en-tête
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=28, pady=(22, 6))
        ctk.CTkLabel(head, text="RotoPDF", font=("Segoe UI", 26, "bold")).pack(anchor="w")
        ctk.CTkLabel(head, text="Transforme une vidéo en planches d'images numérotées",
                     text_color=MUTED, font=("Segoe UI", 13)).pack(anchor="w")

        # --- carte vidéo
        c1 = self.card()
        self.thumb = ctk.CTkLabel(c1, text="Aucune vidéo", width=192, height=108, fg_color=FIELD,
                                  corner_radius=8, text_color=MUTED)
        self.thumb.grid(row=0, column=0, rowspan=3, padx=16, pady=16)
        self.l_name = ctk.CTkLabel(c1, text="Choisis une vidéo pour commencer", anchor="w",
                                   font=("Segoe UI", 15, "bold"))
        self.l_name.grid(row=0, column=1, sticky="sw", pady=(16, 0))
        self.l_meta = ctk.CTkLabel(c1, text="", anchor="w", text_color=MUTED)
        self.l_meta.grid(row=1, column=1, sticky="nw")
        self.btn(c1, "Choisir une vidéo…", self.pick_video).grid(row=2, column=1, sticky="sw", pady=(0, 16))

        # --- carte réglages
        c2 = self.card()
        c2.grid_columnconfigure(0, weight=1)
        left = ctk.CTkFrame(c2, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(18, 8), pady=14)
        left.grid_columnconfigure(0, weight=1)

        self.l_fps = self.slider_row(left, 0, "Images par seconde (fps)", 0.5, 30, 59, 1.0, self.on_change)
        self.s_fps = self.l_fps.slider
        self.l_per = self.slider_row(left, 2, "Images par page", 1, 30, 29, 6, self.on_change)
        self.s_per = self.l_per.slider
        ctk.CTkSwitch(left, text="Afficher le temps sous le numéro", variable=self.v_time,
                      progress_color=ACCENT).grid(row=4, column=0, sticky="w", pady=(14, 0))

        right = ctk.CTkFrame(c2, fg_color="transparent")
        right.grid(row=0, column=1, padx=(8, 18), pady=14)
        ctk.CTkLabel(right, text="Aperçu de la page", text_color=MUTED).pack()
        self.preview = tk.Canvas(right, width=176, height=136, bg=CARD, highlightthickness=0)
        self.preview.pack(pady=(4, 0))

        # --- carte sortie
        c3 = self.card()
        c3.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(c3, textvariable=self.v_pdf, placeholder_text="Emplacement du PDF",
                     fg_color=FIELD, border_width=0, height=34).grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=16)
        self.btn(c3, "Choisir…", self.pick_pdf, secondary=True).grid(row=0, column=1, padx=(0, 16))

        # --- pied
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.pack(fill="x", padx=28, pady=(8, 0))
        foot.grid_columnconfigure(0, weight=1)
        self.l_info = ctk.CTkLabel(foot, text="", text_color=MUTED, anchor="w")
        self.l_info.grid(row=0, column=0, sticky="w")
        self.bar = ctk.CTkProgressBar(foot, progress_color=ACCENT, fg_color=FIELD, height=8)
        self.bar.set(0)
        self.bar.grid(row=1, column=0, sticky="ew", pady=(8, 0), padx=(0, 16))
        self.l_status = ctk.CTkLabel(foot, text="Prêt.", text_color=MUTED, anchor="w")
        self.l_status.grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.go = ctk.CTkButton(foot, text="Créer le PDF", width=170, height=42, corner_radius=8,
                                fg_color=ACCENT, hover_color=ACCENT_H, font=("Segoe UI", 15, "bold"),
                                command=self.start)
        self.go.grid(row=0, column=1, rowspan=3)

        self.on_change()
        self.after(100, self.poll)

    # --- petits constructeurs ---------------------------------------------
    def _set_icon(self):
        try:
            self.iconbitmap(res("icon.ico"))
        except Exception:  # noqa: BLE001
            pass

    def card(self):
        f = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        f.pack(fill="x", padx=28, pady=7)
        return f

    def btn(self, parent, text, cmd, secondary=False):
        return ctk.CTkButton(parent, text=text, command=cmd, width=150, height=34, corner_radius=8,
                             fg_color=FIELD if secondary else ACCENT,
                             hover_color="#44444e" if secondary else ACCENT_H)

    def slider_row(self, parent, row, title, lo, hi, steps, init, cb):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else 12, 0))
        top.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(top, text=title, anchor="w").grid(row=0, column=0, sticky="w")
        val = ctk.CTkLabel(top, text="", font=("Segoe UI", 14, "bold"), text_color=ACCENT)
        val.grid(row=0, column=1)
        sl = ctk.CTkSlider(parent, from_=lo, to=hi, number_of_steps=steps, progress_color=ACCENT,
                           button_color=ACCENT, button_hover_color=ACCENT_H, command=lambda v: cb())
        sl.set(init)
        sl.grid(row=row + 1, column=0, sticky="ew", pady=(4, 0))
        val.slider = sl
        return val

    # --- logique -----------------------------------------------------------
    def params(self):
        return round(self.s_fps.get() * 2) / 2, int(round(self.s_per.get()))

    def on_change(self):
        fps, per = self.params()
        self.l_fps.configure(text=f"{fps:g} fps")
        self.l_per.configure(text=f"{per}")
        if self.duration:
            n = max(1, int(self.duration * fps) + 1)
            self.l_info.configure(text=f"≈ {n} images  •  {math.ceil(n / per)} pages")
        else:
            self.l_info.configure(text="")
        self.draw_preview(per)

    def draw_preview(self, n):
        cv = self.preview
        cv.delete("all")
        lay = best_layout(n, self.aspect)
        pw, ph = lay["pw"], lay["ph"]
        sc = min(168 / pw, 128 / ph)
        ox, oy = (176 - pw * sc) / 2, (136 - ph * sc) / 2
        cv.create_rectangle(ox, oy, ox + pw * sc, oy + ph * sc, fill="#ececf1", outline="")
        iw = min(lay["cw"], lay["ch"] * self.aspect)
        ih = iw / self.aspect
        for i in range(n):
            r, c = divmod(i, lay["cols"])
            x0 = MARGIN + c * (lay["cw"] + GAP) + (lay["cw"] - iw) / 2
            y0 = MARGIN + r * (lay["row_h"] + GAP)
            cv.create_rectangle(ox + x0 * sc, oy + y0 * sc, ox + (x0 + iw) * sc, oy + (y0 + ih) * sc,
                                fill="#7f93c9", outline="")

    def pick_video(self):
        p = filedialog.askopenfilename(
            title="Choisir une vidéo",
            filetypes=[("Vidéos", "*.mp4 *.mov *.mkv *.avi *.webm *.m4v *.wmv"), ("Tous", "*.*")])
        if p:
            self.load_video(p)

    def load_video(self, p):
        cap = cv2.VideoCapture(p)
        if not cap.isOpened():
            return messagebox.showerror("RotoPDF", "Impossible d'ouvrir cette vidéo.")
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        n = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok, frame = cap.read()
        cap.release()
        self.video = p
        self.duration = n / fps if fps and n else None
        if w and h:
            self.aspect = w / h
        self.v_pdf.set(os.path.splitext(p)[0] + "_images.pdf")
        self.l_name.configure(text=os.path.basename(p))
        meta = f"{w}×{h}  •  {fps:g} fps"
        if self.duration:
            meta += f"  •  {fmt_time(self.duration)}"
        self.l_meta.configure(text=meta)
        if ok:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            size = (192, max(1, round(192 / self.aspect))) if self.aspect >= 192 / 108 else \
                   (max(1, round(108 * self.aspect)), 108)
            self._thumb = ctk.CTkImage(img, size=size)
            self.thumb.configure(image=self._thumb, text="")
        self.on_change()

    def pick_pdf(self):
        p = filedialog.asksaveasfilename(title="Enregistrer le PDF", defaultextension=".pdf",
                                         filetypes=[("PDF", "*.pdf")],
                                         initialfile=os.path.basename(self.v_pdf.get()) or "images.pdf")
        if p:
            self.v_pdf.set(p)

    def start(self):
        if self.worker and self.worker.is_alive():
            self.cancel.set()
            return
        out = self.v_pdf.get().strip()
        if not self.video or not os.path.isfile(self.video):
            return messagebox.showwarning("RotoPDF", "Choisis d'abord une vidéo.")
        if not out:
            return messagebox.showwarning("RotoPDF", "Choisis où enregistrer le PDF.")
        if os.path.exists(out):
            if not messagebox.askyesno(
                    "RotoPDF", f"Le fichier « {os.path.basename(out)} » existe déjà.\n"
                               "Voulez-vous le remplacer ?", icon="warning"):
                return
            try:
                open(out, "ab").close()
            except OSError:
                return messagebox.showerror(
                    "RotoPDF", "Impossible d'écrire dans ce fichier : il est peut-être ouvert "
                               "dans un autre programme.\nFerme-le puis réessaie.")
        fps, per = self.params()
        self.cancel.clear()
        self.go.configure(text="Annuler", fg_color="#c0392b", hover_color="#a93226")
        self.bar.set(0)
        video, show_time = self.video, self.v_time.get()

        def run():
            try:
                ok = convert(video, out, fps, per, show_time,
                             lambda v, s: self.msgs.put(("p", v, s)), self.cancel)
                self.msgs.put(("done", ok, out))
            except Exception as e:  # noqa: BLE001
                self.msgs.put(("err", str(e)))

        self.worker = threading.Thread(target=run, daemon=True)
        self.worker.start()

    def reset_button(self):
        self.go.configure(text="Créer le PDF", fg_color=ACCENT, hover_color=ACCENT_H)

    def poll(self):
        try:
            while True:
                m = self.msgs.get_nowait()
                if m[0] == "p":
                    self.bar.set(m[1] / 100)
                    self.l_status.configure(text=m[2])
                elif m[0] == "done":
                    self.reset_button()
                    self.bar.set(1 if m[1] else 0)
                    self.l_status.configure(text="Terminé." if m[1] else "Annulé.")
                    if m[1] and messagebox.askyesno("RotoPDF", "PDF créé.\nL'ouvrir maintenant ?"):
                        os.startfile(m[2])
                elif m[0] == "err":
                    self.reset_button()
                    self.l_status.configure(text="Erreur.")
                    messagebox.showerror("RotoPDF", m[1])
        except queue.Empty:
            pass
        self.after(100, self.poll)


if __name__ == "__main__":
    App().mainloop()
