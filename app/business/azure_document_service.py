
"""
このスクリプトは、Azure Document Intelligence APIを使用してPDFドキュメントを解析し、特定のキーワードを検索します。
使用方法:
    python sample_poc.py <pdf_path> <search_keyword>
引数:
    pdf_path (str): 解析するPDFドキュメントのパス。
    search_keyword (str): ドキュメント内で検索するキーワード。
環境変数:
    DOCUMENTINTELLIGENCE_ENDPOINT: Azure Document Intelligence APIのエンドポイント。
    DOCUMENTINTELLIGENCE_API_KEY: Azure Document Intelligence APIのキー。
例外処理:
    HttpResponseError: APIリクエストが失敗した場合に発生する例外。エラーメッセージとコードに基づいて詳細な情報を提供します。
関数:
    analyze_with_highres(pdf_path, search_keyword):
        PDFドキュメントを解析し、キーワードを検索します。手書きの内容が含まれているかどうかもチェックします。
"""
import os
from dotenv import find_dotenv, load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

# .envファイルから環境変数をロード
load_dotenv(find_dotenv())


def analyze_with_highres(model_id: str, pdf_bytes: bytes, search_keyword: str):
    # [START analyze_with_highres]

    # Azure Document Intelligence APIのエンドポイントとキーを取得
    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

    # DocumentIntelligenceClientを作成
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # 解析を実行
    poller = document_intelligence_client.begin_analyze_document(
        model_id,  # モデルID（この例ではレイアウトモデルを使用）
        analyze_request=pdf_bytes,  # PDFのバイナリデータ
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION],  # 特定の機能を有効化
        content_type="application/octet-stream"  # バイナリデータのContent-Type
    )
    result: AnalyzeResult = poller.result()
    return result.as_dict()
