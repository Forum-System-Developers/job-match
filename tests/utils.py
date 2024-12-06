def assert_filter_called_with(mock_query, expected_expression):
    """
    Asserts that the filter method of the mock_query object was called with the expected expression.

    Args:
        mock_query (Mock): The mock object representing the query.
        expected_expression (Any): The expected expression that should have been passed to the filter method.

    Raises:
        AssertionError: If the filter method was not called with the expected expression.
    """
    assert_called_with(mock_query.filter, expected_expression)


def assert_called_with(mock_clause, expected_expression):
    """
    Assert that a mock object was called exactly once with a specific expression.

    Args:
        mock_clause (unittest.mock.Mock): The mock object to check.
        expected_expression (Any): The expected expression that the mock object should have been called with.

    Raises:
        AssertionError: If the mock object was not called exactly once or if the actual call argument does not match the expected expression.
    """
    mock_clause.assert_called_once()
    actual_expression = mock_clause.call_args[0][0]

    if str(actual_expression) != str(expected_expression):
        raise AssertionError(
            f"Mock was called with {actual_expression}, "
            f"but expected {expected_expression}"
        )
