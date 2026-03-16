"""
app.py
Główny plik aplikacji ScanMyDoc — tylko konfiguracja UI i routing.
Cała logika przetwarzania jest w osobnych modułach.
"""

import cv2
import numpy as np
import streamlit as st

from pdf_utils import image_to_pdf_bytes, merge_pdfs
from processing import decode_uploaded_image, process_auto, process_manual
from styles import inject_styles

# ── Konfiguracja strony (musi być pierwszym wywołaniem Streamlit) ─────────────
st.set_page_config(
    page_title="ScanMyDoc",
    page_icon="uplogo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()

# ── HERO ─────────────────────────────────────────────────────────────────────
hero_col, logo_col = st.columns([5, 1])
with hero_col:
    st.markdown("""
    <div class="hero-wrap">
        <div>
            <div class="hero-badge">v2.5 · KarmelCodeLab</div>
            <p class="hero-title">Scan<span>My</span>Doc</p>
            <p class="hero-sub">Inteligentny skaner dokumentów &nbsp;·&nbsp; Scalanie PDF &nbsp;</p>
        </div>
        <div class="hero-line"></div>
        <div style="color:#8a7560;font-family:'Space Mono',monospace;font-size:.7rem;line-height:2;">
            <div> &nbsp;Kadrowanie</div>
            <div> &nbsp;Tryb automatyczny / ręczny</div>
            <div> &nbsp;Scalanie wielu PDF</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with logo_col:
    st.image("logo.png", width=150)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_skaner, tab_scalaj = st.tabs(["SKANER", "SCAL PDF"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 – SKANER
# ══════════════════════════════════════════════════════════════════════════════
with tab_skaner:

    col_up, col_cfg = st.columns([1, 1], gap="large")

    with col_up:
        st.markdown('<div class="card-label">⬆ Wgraj zdjęcie</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "FORMAT",
            type=["jpg", "jpeg", "png", "webp"],
            key="skaner_upload",
            label_visibility="collapsed",
        )
        st.caption("Obsługiwane formaty: JPG · JPEG · PNG · WEBP")

    with col_cfg:
        st.markdown('<div class="card-label">⚙ Tryb kadrowania</div>', unsafe_allow_html=True)
        mode = st.radio(
            "TRYB",
            ["Automatyczny", "Ręczny (kliknij 4 rogi)"],
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )

    st.markdown("---")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        threshold = st.slider("Kontrast skanu", 90, 220, 150, 5)
    with col_s2:
        min_area_ratio = st.slider("Czułość wykrywania", 0.03, 0.35, 0.08, 0.01)
    with col_s3:
        auto_padding_ratio = st.slider("Margines (auto)", 0.0, 0.25, 0.08, 0.01)

    if uploaded:
        original_bytes = uploaded.read()
        try:
            image = decode_uploaded_image(original_bytes)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        try:
            if mode == "Automatyczny":
                corrected, scanned = process_auto(
                    image, threshold, min_area_ratio, auto_padding_ratio
                )
            else:
                h, w = image.shape[:2]

                st.info("Ustaw suwaki tak, żeby ramka (pomarańczowe linie) dokładnie obejmowała rogi dokumentu.")

                # Podgląd po lewej, suwaki po prawej
                prev_col, ctrl_col = st.columns([2, 1], gap="large")

                with ctrl_col:
                    st.markdown('<div class="card-label">↖ Lewy górny</div>', unsafe_allow_html=True)
                    tl_x = st.slider("LG — poziomo", 0, w, int(w * 0.05), key="tl_x")
                    tl_y = st.slider("LG — pionowo",  0, h, int(h * 0.05), key="tl_y")

                    st.markdown('<div class="card-label">↗ Prawy górny</div>', unsafe_allow_html=True)
                    tr_x = st.slider("PG — poziomo", 0, w, int(w * 0.95), key="tr_x")
                    tr_y = st.slider("PG — pionowo",  0, h, int(h * 0.05), key="tr_y")

                    st.markdown('<div class="card-label">↘ Prawy dolny</div>', unsafe_allow_html=True)
                    br_x = st.slider("PD — poziomo", 0, w, int(w * 0.95), key="br_x")
                    br_y = st.slider("PD — pionowo",  0, h, int(h * 0.95), key="br_y")

                    st.markdown('<div class="card-label">↙ Lewy dolny</div>', unsafe_allow_html=True)
                    bl_x = st.slider("LD — poziomo", 0, w, int(w * 0.05), key="bl_x")
                    bl_y = st.slider("LD — pionowo",  0, h, int(h * 0.95), key="bl_y")

                # Rysuj podgląd z ramką
                preview_np = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
                pts_draw = np.array(
                    [[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]],
                    dtype=np.int32,
                )
                # Linie ramki
                for i in range(4):
                    cv2.line(
                        preview_np,
                        tuple(pts_draw[i]),
                        tuple(pts_draw[(i + 1) % 4]),
                        (245, 150, 10), 3,
                    )
                # Kółka w rogach
                for pt in pts_draw:
                    cv2.circle(preview_np, tuple(pt), 10, (245, 150, 10), -1)
                    cv2.circle(preview_np, tuple(pt), 13, (255, 255, 255), 2)

                with prev_col:
                    st.markdown('<p class="preview-label">Podgląd kadrowania</p>', unsafe_allow_html=True)
                    st.image(preview_np, use_column_width=True)

                manual_points = np.array(
                    [[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]],
                    dtype="float32",
                )
                corrected, scanned = process_manual(image, manual_points, threshold)

        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<p class="preview-label">Po kadrowaniu</p>', unsafe_allow_html=True)
            st.image(cv2.cvtColor(corrected, cv2.COLOR_BGR2RGB), use_column_width=True)
        with col2:
            st.markdown('<p class="preview-label">Efekt skanera</p>', unsafe_allow_html=True)
            st.image(scanned, clamp=True, use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_data = image_to_pdf_bytes(scanned)
        dl_col, _ = st.columns([1, 2])
        with dl_col:
            st.download_button(
                label="⬇  POBIERZ PDF",
                data=pdf_data,
                file_name="skan_dokumentu.pdf",
                mime="application/pdf",
                type="primary",
            )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 – SCAL PDF
# ══════════════════════════════════════════════════════════════════════════════
with tab_scalaj:

    st.markdown('<div class="card-label">⬆ Wgraj pliki PDF</div>', unsafe_allow_html=True)

    uploaded_pdfs = st.file_uploader(
        "Wybierz pliki PDF",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_upload",
        label_visibility="collapsed",
    )
    st.caption("Wgraj co najmniej 2 pliki PDF · zostaną scalone w kolejności wgrywania")

    if uploaded_pdfs:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-label">📋 Kolejność scalania</div>', unsafe_allow_html=True)

        file_list_html = ""
        for i, f in enumerate(uploaded_pdfs, 1):
            size_kb = round(len(f.getvalue()) / 1024, 1)
            file_list_html += f"""
            <div class="file-list-item">
                <span class="file-idx">{i:02d}</span>
                <span style="flex:1">{f.name}</span>
                <span style="color:#8a7560;font-size:.65rem;">{size_kb} KB</span>
            </div>"""
        st.markdown(file_list_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if len(uploaded_pdfs) < 2:
            st.warning("Wgraj co najmniej 2 pliki PDF, aby je scalić.")
        else:
            cfg_col, btn_col = st.columns([2, 1], gap="large")
            with cfg_col:
                nazwa = st.text_input("Nazwa pliku wynikowego", value="scalone_notatki.pdf")
                if not nazwa.endswith(".pdf"):
                    nazwa += ".pdf"
            with btn_col:
                st.markdown("<br>", unsafe_allow_html=True)
                merge_btn = st.button("🔗  SCAL PDF", type="primary", use_container_width=True)

            if merge_btn:
                with st.spinner("Scalanie plików…"):
                    try:
                        merged_bytes = merge_pdfs(uploaded_pdfs)
                        st.success(f"✓ Scalono {len(uploaded_pdfs)} plików PDF pomyślnie!")
                        dl_col2, _ = st.columns([1, 2])
                        with dl_col2:
                            st.download_button(
                                label="⬇  POBIERZ SCALONY PDF",
                                data=merged_bytes,
                                file_name=nazwa,
                                mime="application/pdf",
                            )
                    except Exception as exc:
                        st.error(f"Błąd podczas scalania: {exc}")
    else:
        st.markdown("""
        <div style="
            text-align:center;
            padding: 3rem 2rem;
            background: #1a1d2b;
            border: 1px dashed #3a2e1e;
            border-radius: 12px;
            margin-top: 1rem;
        ">
            <div style="font-size:2.5rem;margin-bottom:.75rem;">📎</div>
            <p style="font-family:'Space Mono',monospace;font-size:.7rem;color:#f5960a;
               letter-spacing:.1em;text-transform:uppercase;margin-bottom:.4rem;">Brak plików</p>
            <p style="font-family:'DM Sans',sans-serif;color:#8a7560;font-size:.88rem;margin:0;">
                Wgraj pliki PDF z zakładki Skaner lub<br>inne pliki PDF, które chcesz połączyć.
            </p>
        </div>
        """, unsafe_allow_html=True)
