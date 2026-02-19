import inspect

import pytest
import responses

import top_reactions


def _call_get_top_reactions(limit=10, skip=0):
    """
    Helper to call get_top_reactions regardless of whether it supports `skip`.
    - If function has parameter `skip`, call with (limit, skip)
    - Otherwise call with (limit) only
    """
    sig = inspect.signature(top_reactions.get_top_reactions)
    if "skip" in sig.parameters:
        return top_reactions.get_top_reactions(limit=limit, skip=skip)
    return top_reactions.get_top_reactions(limit=limit)


@responses.activate
def test_pagination():
    """
    Pagination unit test.

    If your implementation supports `skip`, we verify that different skips
    produce different "pages" and that query params include skip/limit.

    If your implementation does NOT support `skip`, we verify pagination
    by fetching top20 and slicing into two pages.
    """
    sig = inspect.signature(top_reactions.get_top_reactions)
    base_url = top_reactions.BASE_URL

    if "skip" in sig.parameters:
        # Mock page 1 (skip=0)
        responses.add(
            responses.GET,
            base_url,
            json={"results": [{"term": "A", "count": 3}]},
            status=200,
            match=[responses.matchers.query_param_matcher({
                "count": "reaction.veddra_term_name.exact",
                "limit": "10",
                "skip": "0",
            })],
        )

        # Mock page 2 (skip=10)
        responses.add(
            responses.GET,
            base_url,
            json={"results": [{"term": "B", "count": 2}]},
            status=200,
            match=[responses.matchers.query_param_matcher({
                "count": "reaction.veddra_term_name.exact",
                "limit": "10",
                "skip": "10",
            })],
        )

        page1 = _call_get_top_reactions(limit=10, skip=0)
        page2 = _call_get_top_reactions(limit=10, skip=10)

        assert page1[0]["term"] == "A"
        assert page2[0]["term"] == "B"

    else:
        # No skip support: fetch top 20 and slice into two "pages"
        responses.add(
            responses.GET,
            base_url,
            json={"results": [{"term": f"T{i}", "count": i} for i in range(1, 21)]},
            status=200,
            match=[responses.matchers.query_param_matcher({
                "count": "reaction.veddra_term_name.exact",
                "limit": "20",
            })],
        )

        top20 = _call_get_top_reactions(limit=20)
        page1 = top20[:10]
        page2 = top20[10:20]

        assert len(page1) == 10
        assert len(page2) == 10
        assert page1[0]["term"] == "T1"
        assert page2[0]["term"] == "T11"


@responses.activate
def test_empty_results_returns_empty_list():
    """
    Handling empty results:
    If API returns results=[], your function should return an empty list (not crash).
    """
    responses.add(
        responses.GET,
        top_reactions.BASE_URL,
        json={"results": []},
        status=200,
        match=[responses.matchers.query_param_matcher({
            "count": "reaction.veddra_term_name.exact",
            "limit": "10",
            # If your code includes skip in params, matcher would need it.
            # We avoid requiring skip here by keeping limit=10 only in the call below
            # and making this test flexible via helper.
        })],
    )

    # To keep matcher flexible across implementations, we call limit=10 and skip=0
    # but only include skip in matcher if your function uses it.
    sig = inspect.signature(top_reactions.get_top_reactions)
    if "skip" in sig.parameters:
        # Replace the previous mocked response with a matcher that includes skip
        responses.reset()
        responses.add(
            responses.GET,
            top_reactions.BASE_URL,
            json={"results": []},
            status=200,
            match=[responses.matchers.query_param_matcher({
                "count": "reaction.veddra_term_name.exact",
                "limit": "10",
                "skip": "0",
            })],
        )
        results = _call_get_top_reactions(limit=10, skip=0)
    else:
        results = _call_get_top_reactions(limit=10)

    assert results == []


@responses.activate
def test_extract_useful_fields_term_and_count_present():
    """
    Extracting useful fields:
    We verify that items returned contain 'term' and 'count' fields and types make sense.
    """
    mock_results = [
        {"term": "Vomiting", "count": 209845},
        {"term": "Diarrhoea", "count": 79881},
    ]

    # Build matcher depending on whether skip exists
    sig = inspect.signature(top_reactions.get_top_reactions)
    matcher = {
        "count": "reaction.veddra_term_name.exact",
        "limit": "10",
    }
    if "skip" in sig.parameters:
        matcher["skip"] = "0"

    responses.add(
        responses.GET,
        top_reactions.BASE_URL,
        json={"results": mock_results},
        status=200,
        match=[responses.matchers.query_param_matcher(matcher)],
    )

    if "skip" in sig.parameters:
        results = _call_get_top_reactions(limit=10, skip=0)
    else:
        results = _call_get_top_reactions(limit=10)

    assert isinstance(results, list)
    assert len(results) == 2

    first = results[0]
    assert "term" in first and "count" in first
    assert isinstance(first["term"], str)
    assert isinstance(first["count"], int)