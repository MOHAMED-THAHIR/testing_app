from services.export_service import ExportService


class ExportController:
    def __init__(self):
        self.service = ExportService()

    def export_pdf(self, data: dict) -> str:
        return self.service.generate_pdf(data)

    def export_pptx(self, data: dict) -> str:
        return self.service.generate_pptx(data)

    def export_docx(self, data: dict) -> str:
        return self.service.generate_docx(data)