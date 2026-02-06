from supabase import create_client, ClientOptions
import os
import httpx

# Force HTTP/1.1 (important on Windows / Render)
httpx_client = httpx.Client(http2=False)

options = ClientOptions(
    httpx_client=httpx_client
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY"),
    options=options
)
