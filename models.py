from pydantic import BaseModel


class DNSRecord(BaseModel):
    record_id: str
    type: str
    host: str
    value: str
    ttl: str
    distance: str
