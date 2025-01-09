
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
    # 検索結果を格納するリスト
    search_result = []

    # DocumentIntelligenceClientを作成
    document_intelligence_client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))

    # 解析を実行
    poller = document_intelligence_client.begin_analyze_document(
        model_id=model_id,  # モデルID（この例ではレイアウトモデルを使用）
        body=pdf_bytes,  # PDFのバイナリデータ
        content_type="application/octet-stream",  # バイナリデータのContent-Type
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION]  # 高解像度OCRを有効にするオプション(任意)
    )
    result: AnalyzeResult = poller.result()

    # キーワードが空の場合、解析結果をそのまま返却
    keyword_exists = search_keyword in result.content  # 完全一致のみを検索
    if not keyword_exists or search_keyword == "":
        return False, result.as_dict()

    # キーワードが存在する場合、指定されたキーワードを含む解析結果のみを抽出
    for index, paragraph in enumerate(result.paragraphs):

        # 解析結果にキーワードが存在しない場合は後続の処理をスキップし、次の解析結果を処理
        if paragraph.content != search_keyword:
            continue

        # ページ内のテキストを検索
        if paragraph.content == search_keyword:
            print(f"Found keyword '{search_keyword}' in paragraph'[{index}]'")
            paragraph_dict = paragraph.as_dict()
            search_result.append(paragraph_dict)
        else:
            pass

    # NOTE 表に含まれる文字列がresult.pages.linesに含まれない場合はresult.tables以下を検索する処理を記載する

    return True, search_result
