 File "/usr/local/bin/uvicorn", line 6, in <module>
    sys.exit(main())
             ^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1631, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1552, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 1415, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/click/core.py", line 910, in invoke
    return callback(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 448, in main
    run(
  File "/usr/local/lib/python3.11/site-packages/uvicorn/main.py", line 620, in run
    config.load_app()
  File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 434, in load_app
    return import_from_string(self.app)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 22, in import_from_string
    raise exc from None
  File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/main.py", line 17, in <module>
    from dashboard_planner import create_dashboard_plan
  File "/app/dashboard_planner.py", line 3, in <module>
    from langchain_google_genai import ChatGoogleGenerativeAI
ModuleNotFoundError: No module named 'langchain_google_genai'





aiohappyeyeballs==2.7.1
aiohttp==3.14.3
aiosignal==1.4.0
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.14.2
asttokens==3.0.2
attrs==26.1.0
bcrypt==5.0.0
blinker==1.9.0
build==1.5.0
certifi==2026.7.22
cffi==2.1.1
charset-normalizer==3.4.9
chromadb==1.5.9
click==8.4.2
comm==0.2.3
contourpy==1.3.3
cryptography==50.0.0
cycler==0.12.1
db-dtypes==1.7.1
debugpy==1.8.21
decorator==5.3.1
distro==1.9.0
durationpy==0.10
executing==2.2.1
fastapi==0.141.1
filelock==3.32.2
filetype==1.2.0
Flask==3.0.3
flatbuffers==25.12.19
fonttools==4.63.0
frozenlist==1.8.0
fsspec==2026.7.0
google-api-core==2.34.0
google-auth==2.56.3
google-cloud-bigquery==3.43.0
google-cloud-bigquery-storage==2.40.0
google-cloud-core==2.6.1
google-cloud-storage==3.13.1
google-crc32c==1.8.0
google-genai==2.17.0
google-resumable-media==2.10.1
googleapis-common-protos==1.75.1
greenlet==3.5.5
grpcio==1.83.0
grpcio-status==1.83.0
gunicorn==22.0.0
h11==0.16.0
hf-xet==1.6.0
httpcore==1.0.9
httptools==0.8.0
httpx==0.28.1
httpx-sse==0.4.3
huggingface_hub==1.27.0
idna==3.18
importlib_resources==7.1.0
ipykernel==7.3.0
ipython==9.15.0
ipython_pygments_lexers==1.1.1
itsdangerous==2.2.0
jedi==0.20.0
Jinja2==3.1.6
jsonpatch==1.33
jsonpointer==3.1.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
jupyter_client==8.9.1
jupyter_core==5.9.1
kiwisolver==1.5.0
kubernetes==36.0.3
langchain==1.3.15
langchain-classic==1.0.8
langchain-community==0.4.2
langchain-core==1.5.4
langchain-google-genai==4.3.4
langchain-protocol==0.0.18
langchain-text-splitters==1.1.2
langgraph==1.2.11
langgraph-checkpoint==4.2.0
langgraph-prebuilt==1.1.0
langgraph-sdk==0.4.2
langsmith==0.10.18
markdown-it-py==4.2.0
MarkupSafe==3.0.3
matplotlib==3.11.1
matplotlib-inline==0.2.2
mdurl==0.1.2
mmh3==5.2.1
multidict==6.7.1
nest-asyncio2==1.7.2
numpy==2.5.2
oauthlib==3.3.1
onnxruntime==1.28.0
opentelemetry-api==1.44.0
opentelemetry-exporter-otlp-proto-common==1.44.0
opentelemetry-exporter-otlp-proto-grpc==1.44.0
opentelemetry-proto==1.44.0
opentelemetry-sdk==1.44.0
opentelemetry-semantic-conventions==0.65b0
orjson==3.11.9
ormsgpack==1.12.2
overrides==7.7.0
packaging==26.2
pandas==3.0.5
parso==0.8.7
pexpect==4.9.0
pillow==12.3.0
platformdirs==4.10.0
prompt_toolkit==3.0.52
propcache==0.5.2
proto-plus==1.28.3
protobuf==7.35.1
psutil==7.2.2
ptyprocess==0.7.0
pure_eval==0.2.3
pyarrow==25.0.0
pyasn1==0.6.4
pyasn1_modules==0.4.2
pybase64==1.5.0
pycparser==3.0
pydantic==2.13.4
pydantic-settings==2.15.0
pydantic_core==2.46.4
Pygments==2.20.0
pyparsing==3.3.2
pypdf==6.15.0
PyPika==0.51.1
pyproject_hooks==1.2.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
python-multipart==0.0.32
PyYAML==6.0.3
pyzmq==27.1.0
referencing==0.37.0
requests==2.34.2
requests-oauthlib==2.0.0
requests-toolbelt==1.0.0
rich==15.0.0
rpds-py==2026.6.3
seaborn==0.13.2
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.52
sqlalchemy-bigquery==1.17.2
stack-data==0.6.3
starlette==1.6.0
tenacity==9.1.4
tokenizers==0.23.1
tornado==6.5.7
tqdm==4.70.0
traitlets==5.15.1
typer==0.27.1
typing-inspection==0.4.2
typing_extensions==4.16.0
urllib3==2.7.0
uuid_utils==0.17.0
uvicorn==0.52.1
uvloop==0.22.1
watchfiles==1.2.0
wcwidth==0.8.2
websocket-client==1.9.0
websockets==15.0.1
Werkzeug==3.1.8
xxhash==4.0.0
yarl==1.24.5
zstandard==0.25.0






















