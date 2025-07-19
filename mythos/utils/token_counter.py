class TokenCounter:
    """
    Singleton class to keep track of total tokens used across API calls.
    """
    _instance = None
    _total_tokens = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenCounter, cls).__new__(cls)
        return cls._instance

    def add_tokens(self, count: int):
        """
        Add tokens to the total count.

        Args:
            count (int): Number of tokens to add.
        """
        self._total_tokens += count

    def get_total_tokens(self) -> int:
        """
        Retrieve the total number of tokens used.

        Returns:
            int: Total tokens count.
        """
        return self._total_tokens