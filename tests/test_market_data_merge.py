def test_tracked_assets_are_merged_by_id():
    broad = [{"id": "bitcoin", "symbol": "btc"}]
    tracked = [{"id": "coti", "symbol": "coti"}, {"id": "bitcoin", "symbol": "btc"}]
    merged = {}
    for item in broad + tracked:
        merged[item["id"]] = item
    assert "coti" in merged
    assert len(merged) == 2
