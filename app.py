"""
app.py
Główny plik aplikacji ScanMyDoc — tylko konfiguracja UI i routing.
Cała logika przetwarzania jest w osobnych modułach.
"""

import cv2
import numpy as np
import streamlit as st

from canvas_utils import build_canvas_image, extract_points_from_canvas
from pdf_utils import image_to_pdf_bytes, merge_pdfs
from processing import decode_uploaded_image, process_auto, process_manual
from styles import inject_styles

# ── Opcjonalna zależność od drawable canvas ───────────────────────────────────
st_canvas = None
HAS_CANVAS = False
try:
    from streamlit_drawable_canvas import st_canvas
    HAS_CANVAS = True
except ImportError:
    HAS_CANVAS = False

# ── Konfiguracja strony (musi być pierwszym wywołaniem Streamlit) ─────────────
st.set_page_config(
    page_title="ScanMyDoc",
    page_icon="assets/uplogo.png",
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
            <div class="hero-badge">v2.0 · KarmelCodeLab</div>
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
    st.image("assets/logo.png", width=150)

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

    if "canvas_reset_id" not in st.session_state:
        st.session_state["canvas_reset_id"] = 0

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
                if not HAS_CANVAS:
                    st.error(
                        "Brakuje biblioteki streamlit-drawable-canvas. "
                        "Zainstaluj: `pip install streamlit-drawable-canvas`"
                    )
                    st.stop()

                st.info(
                    "Kliknij 4 rogi dokumentu po kolei: "
                    "lewy-górny → prawy-górny → prawy-dolny → lewy-dolny."
                )

                preview_image, sx, sy = build_canvas_image(image)
                canvas_key = f"doc_canvas_{st.session_state['canvas_reset_id']}"

                btn_col, hint_col = st.columns([1, 3])
                with btn_col:
                    if st.button("✕  Wyczyść punkty", type="secondary"):
                        st.session_state["canvas_reset_id"] += 1
                        st.rerun()
                with hint_col:
                    st.caption("Po kliknięciu 4 punktów dokument zostanie przycięty automatycznie.")

                canvas_result = st_canvas(
                    fill_color="rgba(245,150,10,0.35)",
                    stroke_width=2,
                    stroke_color="#f5960a",
                    background_image=preview_image,
                    update_streamlit=True,
                    height=preview_image.height,
                    width=preview_image.width,
                    drawing_mode="point",
                    point_display_radius=8,
                    key=canvas_key,
                )

                clicked_points = extract_points_from_canvas(
                    canvas_result.json_data if canvas_result else {}
                )

                if len(clicked_points) >= 2:
                    preview_np = np.array(preview_image)
                    pts = np.array(clicked_points[:4], dtype=np.int32)
                    for i in range(len(pts) - 1):
                        cv2.line(preview_np, tuple(pts[i]), tuple(pts[i + 1]), (245, 150, 10), 2)
                    if len(pts) == 4:
                        cv2.line(preview_np, tuple(pts[3]), tuple(pts[0]), (245, 150, 10), 2)
                    st.image(preview_np)

                st.caption(f"Zaznaczone punkty: {len(clicked_points)} / 4")
                if len(clicked_points) < 4:
                    st.stop()
                if len(clicked_points) > 4:
                    st.warning(
                        "Używam pierwszych 4 punktów. "
                        "Kliknij 'Wyczyść punkty', jeśli chcesz poprawić."
                    )

                manual_points = np.array(clicked_points[:4], dtype="float32")
                manual_points[:, 0] *= sx
                manual_points[:, 1] *= sy
                corrected, scanned = process_manual(image, manual_points, threshold)

        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<p class="preview-label">📐 Po kadrowaniu</p>', unsafe_allow_html=True)
            st.image(cv2.cvtColor(corrected, cv2.COLOR_BGR2RGB), use_column_width=True)
        with col2:
            st.markdown('<p class="preview-label">🖨 Efekt skanera</p>', unsafe_allow_html=True)
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
        st.markdown('<div class="card-label">Kolejność scalania</div>', unsafe_allow_html=True)

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
                merge_btn = st.button("SCAL PDF", type="primary", use_container_width=True)

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
