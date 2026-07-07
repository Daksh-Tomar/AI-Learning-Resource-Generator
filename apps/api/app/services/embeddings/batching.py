from typing import List, Generator
from pydantic import BaseModel

def batch_iterable(iterable: List, batch_size: int = 32) -> Generator[List, None, None]:
    """Yield successive n-sized chunks from iterable."""
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]
