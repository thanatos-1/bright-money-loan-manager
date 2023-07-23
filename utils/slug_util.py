import uuid

import hashids
from django.conf import settings


def slugify(id: int) -> str:
    hash = hashids.Hashids(
        salt=settings.HASHIDS_SALT,
        min_length=settings.HASHIDS_MIN_LENGTH,
        alphabet=settings.HASHIDS_ALPHABET,
    )
    hash_id = hash.encrypt(id) 
    return f"{uuid.uuid4().hex[:1]}{hash_id}{uuid.uuid4().hex[-2:-1]}"
