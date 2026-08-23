 uvicorn main:app --reload --host 0.0.0.0 --port 8000
INFO:     Will watch for changes in these directories: ['/home/abhisheks_s/ai_wireframe/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [7685] using WatchFiles
INFO:     Started server process [7687]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:56938 - "GET /?authuser=0 HTTP/1.1" 200 OK
INFO:     127.0.0.1:56844 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:56844 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:34566 - "POST /generate-dashboard HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/uvicorn/protocols/http/httptools_impl.py", line 422, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 63, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/applications.py", line 1163, in __call__
    await super().__call__(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/applications.py", line 96, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 96, in __call__
    await self.simple_response(scope, receive, send, request_headers=headers)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/middleware/cors.py", line 154, in simple_response
    await self.app(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/routing.py", line 670, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 2734, in app
    await route.handle(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 1281, in handle
    await super().handle(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/routing.py", line 280, in handle
    await self.app(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 158, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 144, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/fastapi/routing.py", line 747, in app
    response = actual_response_class(content, **response_args)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/responses.py", line 192, in __init__
    super().__init__(content, status_code, headers, media_type, background)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/responses.py", line 45, in __init__
    self.body = self.render(content)
                ^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/starlette/responses.py", line 195, in render
    return json.dumps(
           ^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
          ^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
ValueError: Out of range float values are not JSON compliant: nan
