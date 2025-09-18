"""Generación de certificados utilizando ReportLab."""
from __future__ import annotations

import os
from typing import Callable, Dict, Iterable, List, Optional

from ..utils.loggerv2 import AppLogger
from .reportlab_renderer import ReportLabCertificateRenderer


class PDFGenerator:
    """Generador de certificados PDF basado en ReportLab."""

    def __init__(self) -> None:
        self.logger = AppLogger()
        self.renderer = ReportLabCertificateRenderer()

    def generate_certificate(self, data: Dict[str, object], output_dir: str) -> bool:
        """Generar un certificado individual."""
        try:
            nombre = data.get("nombre_apellido", "Desconocido")
            self.logger.info(f"Generando certificado para: {nombre}")

            filename = self.generate_filename(data)
            pdf_path = os.path.join(output_dir, filename)
            self.logger.debug(f"Ruta de salida para el certificado: {pdf_path}")

            self.renderer.render(data, pdf_path)
            self.logger.success(f"Certificado generado: {pdf_path}")
            return True
        except Exception as exc:  # pragma: no cover - errores de renderizado
            self.logger.error(
                f"Error generando certificado para {data.get('nombre_apellido', 'Desconocido')}: {type(exc).__name__}: {exc}"
            )
            return False

    def generate_batch(
        self,
        data_list: Iterable[Dict[str, object]],
        output_dir: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, object]:
        """Generar múltiples certificados."""
        items: List[Dict[str, object]] = list(data_list) if not isinstance(data_list, list) else data_list
        results = {
            "total": len(items),
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        for index, data in enumerate(items, start=1):
            try:
                self.logger.processing(f"Procesando certificado {index}/{results['total']}")
                success = self.generate_certificate(data, output_dir)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(
                        f"Error generando: {data.get('nombre_apellido', 'Desconocido')}"
                    )
            except Exception as exc:  # pragma: no cover - robustez durante lote
                results["failed"] += 1
                results["errors"].append(
                    f"Error procesando {data.get('nombre_apellido', 'Desconocido')}: {exc}"
                )

            if progress_callback:
                progress_callback(index, results["total"])

        self.logger.success(
            f"Generación por lotes completada: {results['success']}/{results['total']} certificados"
        )
        return results

    def generate_filename(self, data: Dict[str, object]) -> str:
        """Generar nombre de archivo normalizado para el certificado."""
        try:
            nombre = str(data.get("nombre_apellido", "Sin_Nombre"))
            dni = str(data.get("dni", "Sin_DNI"))

            nombre = self.clean_filename(nombre)
            dni = self.clean_filename(dni)
            return f"{nombre}_{dni}.pdf"
        except Exception as exc:  # pragma: no cover
            self.logger.warning(f"Error generando nombre de archivo: {exc}")
            return "certificado.pdf"

    @staticmethod
    def clean_filename(filename: str) -> str:
        """Eliminar caracteres problemáticos para nombres de archivo."""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        cleaned = filename
        for char in invalid_chars:
            cleaned = cleaned.replace(char, "_")

        cleaned = cleaned.replace(" ", "_")
        cleaned = cleaned.replace("ñ", "n").replace("Ñ", "N")

        accents = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "A",
            "É": "E",
            "Í": "I",
            "Ó": "O",
            "Ú": "U",
        }
        for accented, plain in accents.items():
            cleaned = cleaned.replace(accented, plain)

        return cleaned
