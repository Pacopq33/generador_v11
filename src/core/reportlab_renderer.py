"""Renderizado de certificados directamente con ReportLab."""
from __future__ import annotations

import os
from typing import Dict, Iterable, Tuple

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ..utils.loggerv2 import AppLogger
from ..utils.resource_utils import get_resource_path


class ReportLabCertificateRenderer:
    """Genera el certificado completo utilizando ReportLab."""

    LOGO_MAX_HEIGHT_CM = 4.0
    LOGO_MAX_WIDTH_RATIO = 0.8
    FRAME_MARGIN_CM = 0.5
    SIGNATURE_BLOCK_WIDTH_RATIO = 0.42

    def __init__(self) -> None:
        self.logger = AppLogger()
        self.page_width, self.page_height = landscape(A4)
        self.margin = self.FRAME_MARGIN_CM * cm
        self.inner_width = self.page_width - 2 * self.margin
        self.inner_height = self.page_height - 2 * self.margin
        self.fonts = self._register_fonts()

    def _register_fonts(self) -> Dict[str, str]:
        """Registrar tipografías personalizadas si están disponibles."""
        fonts = {
            "body": "Times-Roman",
            "body_bold": "Times-Bold",
            "body_italic": "Times-Italic",
            "signature": "Helvetica",
            "signature_bold": "Helvetica-Bold",
        }

        fonts_dir = get_resource_path(os.path.join("assets", "fonts"))
        font_candidates: Iterable[Tuple[str, str, str]] = (
            ("CertificateBody", "Garamond-Regular.ttf", "body"),
            ("CertificateBody-Bold", "Garamond-Bold.ttf", "body_bold"),
            ("CertificateBody-Italic", "Garamond-Italic.ttf", "body_italic"),
            ("CertificateSignature", "ArialNarrow.ttf", "signature"),
            ("CertificateSignature-Bold", "ArialNarrow-Bold.ttf", "signature_bold"),
        )

        for alias, filename, key in font_candidates:
            font_path = os.path.join(fonts_dir, filename)
            if not os.path.exists(font_path):
                continue
            try:
                pdfmetrics.registerFont(TTFont(alias, font_path))
                fonts[key] = alias
                self.logger.info(f"Fuente registrada: {alias} ({filename})")
            except Exception as exc:  # pragma: no cover - registro opcional
                self.logger.warning(
                    f"No se pudo registrar la fuente '{filename}': {type(exc).__name__}: {exc}"
                )

        return fonts

    def render(self, data: Dict[str, str], output_path: str) -> None:
        """Renderiza y guarda un certificado en el `output_path` indicado."""
        self.logger.debug(f"Renderizando certificado en {output_path}")
        directory = os.path.dirname(output_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        c = canvas.Canvas(output_path, pagesize=(self.page_width, self.page_height))
        try:
            self._draw_frame(c)
            current_y = self._draw_logo(c)
            current_y = self._draw_header_block(c, data, current_y)
            current_y = self._draw_course_block(c, data, current_y)
            current_y = self._draw_disposition_block(c, data, current_y)
            self._draw_date_line(c, data, current_y)
            self._draw_signatures(c)
        finally:
            c.save()
            self.logger.debug(f"Certificado guardado en {output_path}")

    def _draw_frame(self, c: canvas.Canvas) -> None:
        c.setLineWidth(0.5)
        c.rect(self.margin, self.margin, self.inner_width, self.inner_height)

    def _draw_logo(self, c: canvas.Canvas) -> float:
        logo_path = get_resource_path(os.path.join("assets", "logomejor.png"))
        max_height = self.LOGO_MAX_HEIGHT_CM * cm
        max_width = self.inner_width * self.LOGO_MAX_WIDTH_RATIO

        if os.path.exists(logo_path):
            try:
                image = ImageReader(logo_path)
                img_width, img_height = image.getSize()
                ratio = img_width / img_height if img_height else 1

                logo_width = max_width
                logo_height = logo_width / ratio if ratio else max_height
                if logo_height > max_height:
                    logo_height = max_height
                    logo_width = logo_height * ratio

                x = (self.page_width - logo_width) / 2
                y = self.page_height - self.margin - logo_height
                c.drawImage(logo_path, x, y, width=logo_width, height=logo_height, mask="auto")
                return y - 1.0 * cm
            except Exception as exc:  # pragma: no cover - robustez ante imágenes inválidas
                self.logger.warning(
                    f"No se pudo dibujar el logo '{logo_path}': {type(exc).__name__}: {exc}"
                )

        self.logger.warning("Logo principal no encontrado; se omite en el certificado")
        return self.page_height - self.margin - 1.0 * cm

    def _draw_header_block(self, c: canvas.Canvas, data: Dict[str, str], start_y: float) -> float:
        nombre = self._safe_text(data.get("nombre_apellido"))
        dni = self._safe_text(data.get("dni"))

        y = start_y
        c.setFont(self.fonts["body"], 22)
        c.drawCentredString(self.page_width / 2, y, "Por cuanto")

        y -= 0.9 * cm
        c.setFont(self.fonts["body_italic"], 24)
        c.drawCentredString(self.page_width / 2, y, nombre or "................................")

        y -= 0.9 * cm
        c.setFont(self.fonts["body_italic"], 24)
        c.drawCentredString(self.page_width / 2, y, "DNI Nº")

        y -= 0.9 * cm
        c.drawCentredString(self.page_width / 2, y, dni or "................")

        y -= 0.9 * cm
        c.setFont(self.fonts["body"], 22)
        c.drawCentredString(self.page_width / 2, y, "ha aprobado la")

        return y - 0.6 * cm

    def _draw_course_block(self, c: canvas.Canvas, data: Dict[str, str], start_y: float) -> float:
        carrera = self._safe_text(data.get("carrera"))
        course_text = f"“{carrera}”" if carrera else "“”"

        y = start_y
        c.setFont(self.fonts["body_bold"], 20)
        lines = simpleSplit(course_text, self.fonts["body_bold"], 20, self.inner_width)
        for line in lines:
            c.drawCentredString(self.page_width / 2, y, line)
            y -= 0.7 * cm

        y -= 0.2 * cm
        c.setFont(self.fonts["body"], 20)
        c.drawCentredString(self.page_width / 2, y, "Por tanto le expide el presente certificado.")

        return y - 0.7 * cm

    def _draw_disposition_block(self, c: canvas.Canvas, data: Dict[str, str], start_y: float) -> float:
        dispo = self._safe_text(data.get("dispo"))
        c.setFont(self.fonts["body_italic"], 18)

        y = start_y
        dispo_line = f"Disposición INSPT-UTN Nº {dispo}" if dispo else "Disposición INSPT-UTN"
        c.drawCentredString(self.page_width / 2, y, dispo_line)

        y -= 0.7 * cm
        c.drawCentredString(
            self.page_width / 2,
            y,
            "con una carga horaria de 620 hs. reloj",
        )

        return y - 0.4 * cm

    def _draw_date_line(self, c: canvas.Canvas, data: Dict[str, str], start_y: float) -> None:
        dia = self._safe_text(data.get("dia"))
        mes = self._safe_text(data.get("mes"))
        anio = self._safe_text(data.get("anio")) or "2025"

        c.setFont(self.fonts["body"], 18)
        text = f"Buenos Aires, {dia} de {mes} de {anio}".strip()
        c.drawCentredString(self.page_width / 2, start_y, text)

    def _draw_signatures(self, c: canvas.Canvas) -> None:
        base_y = self.margin + 2.0 * cm
        block_width = self.inner_width * self.SIGNATURE_BLOCK_WIDTH_RATIO

        left_center = self.margin + block_width / 2
        right_center = self.page_width - self.margin - block_width / 2

        self._draw_signature_block(
            c,
            left_center,
            base_y,
            [
                ("Prof. Manuel J. Polantinos", self.fonts["signature_bold"], 12),
                ("Secretario de Planeamiento", self.fonts["signature"], 10),
                (
                    "Instituto Nacional Superior del Profesorado Técnico",
                    self.fonts["signature"],
                    8,
                ),
                ("Universidad Tecnológica Nacional", self.fonts["signature"], 8),
            ],
            block_width,
        )

        self._draw_signature_block(
            c,
            right_center,
            base_y,
            [
                ("Ing. Alberto Viarengo", self.fonts["signature_bold"], 12),
                ("Director", self.fonts["signature"], 10),
                (
                    "Instituto Nacional Superior del Profesorado Técnico",
                    self.fonts["signature"],
                    8,
                ),
                ("Universidad Tecnológica Nacional", self.fonts["signature"], 8),
            ],
            block_width,
        )

    def _draw_signature_block(
        self,
        c: canvas.Canvas,
        center_x: float,
        base_y: float,
        lines: Iterable[Tuple[str, str, int]],
        block_width: float,
    ) -> None:
        line_y = base_y + 1.5 * cm
        half_width = block_width / 2
        c.setLineWidth(0.5)
        c.line(center_x - half_width, line_y, center_x + half_width, line_y)

        current_y = line_y - 0.4 * cm
        for text, font_name, font_size in lines:
            c.setFont(font_name, font_size)
            c.drawCentredString(center_x, current_y, text)
            current_y -= 0.45 * cm

    @staticmethod
    def _safe_text(value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()
