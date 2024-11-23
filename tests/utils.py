def assert_filter_called_with(mock_query, expected_expression):
    """
    Asserts that the filter method of a mock query object was called exactly once
    with a specific expression.

    Args:
        mock_query (Mock): The mock query object whose filter method is being tested.
        expected_expression (BinaryExpression): The expected expression that should
            have been passed to the filter method.

    Raises:
        AssertionError: If the filter method was not called exactly once
        or if the filter expression does not match the expected expression.
    """
    mock_query.filter.assert_called_once()
    filter_expression = mock_query.filter.call_args[0][0]

    if str(filter_expression) != str(expected_expression):
        raise AssertionError(
            f"Filter was called with {filter_expression}, "
            f"but expected {expected_expression}"
        )
