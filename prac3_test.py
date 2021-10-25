from datetime import datetime
from unittest.mock import Mock
from Prac3_final_codeHL import CalendarManager, InMemoryCalendarAccessor
import pytest

@pytest.fixture
def manager():
    accessor = InMemoryCalendarAccessor()
    return CalendarManager(accessor)

