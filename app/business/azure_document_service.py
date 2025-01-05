
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
        model_id,  # モデルID（この例ではレイアウトモデルを使用）
        analyze_request=pdf_bytes,  # PDFのバイナリデータ
        content_type="application/octet-stream",  # バイナリデータのContent-Type
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION]  # 高解像度OCRを有効にするオプション(任意)
    )
    result: AnalyzeResult = poller.result()

    # キーワードが空の場合、解析結果をそのまま返却
    if not search_keyword:
        return None, result.as_dict()

    # キーワードが指定されている場合、指定されたキーワードを含むページのみを抽出
    for page in result.pages:
        print(f"----Analyzing layout from page #{page.page_number}----")
        print(f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")

        # ページにテキストが存在しない場合は後続の処理をスキップし、次のページを処理
        if not page.lines:
            continue

        # ページ内のテキストを検索
        is_keyword_found = False
        for _, line in enumerate(page.lines):
            if search_keyword in line.content:
                print(f"Found keyword '{search_keyword}' in line '{line.content}'")
                tmp = {
                    "pageNumber": page.page_number,
                    "searchResult": {
                        "content": line.content,
                        "polygon": line.polygon,
                        "spans": [{"offset": span.offset, "length": span.length} for span in line.spans]
                    },
                }
                search_result.append(tmp)
                is_keyword_found = True
        if not is_keyword_found:
            print(f"Keyword '{search_keyword}' not found in page #{page.page_number}")

    # NOTE 表に含まれる文字列がresult.pages.linesに含まれない場合はresult.tables以下を検索する処理を記載する

    return is_keyword_found, search_result
