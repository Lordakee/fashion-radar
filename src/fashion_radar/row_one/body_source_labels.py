from __future__ import annotations

from fashion_radar.row_one.models import LocalizedText, RowOneLocalArticleBodySource


def row_one_body_source_label(body_source: RowOneLocalArticleBodySource) -> LocalizedText:
    if body_source == "summary_fallback":
        return LocalizedText(en="ROW ONE summary fallback", zh="ROW ONE 摘要回退")
    if body_source == "skipped":
        return LocalizedText(en="Skipped", zh="已跳过")
    return LocalizedText(en="Extracted article text", zh="已提取文章正文")
