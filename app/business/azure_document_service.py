
import os
from dotenv import find_dotenv, load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

# Azure Document Intelligence APIのエンドポイントとキーを取得
load_dotenv(find_dotenv())
ENDPOINT = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
API_KEY = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]


def analyze_with_highres(model_id: str, pdf_bytes: bytes, search_keyword: str):
    # [START analyze_with_highres]

    # DocumentIntelligenceClientを作成
    document_intelligence_client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))

    # 解析を実行
    poller = document_intelligence_client.begin_analyze_document(
        model_id,  # モデルID（この例ではレイアウトモデルを使用）
        analyze_request=pdf_bytes,  # PDFのバイナリデータ
        content_type="application/octet-stream",  # バイナリデータのContent-Type
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION]  # 高解像度OCRを有効にするオプション(任意)
    )
    result: AnalyzeResult = poller.result()

    # search_keywordが空の場合、解析結果をそのまま返却
    if not search_keyword:
        return result.as_dict()

    # search_keywordが指定されている場合、指定されたキーワードを含むページのみを抽出
