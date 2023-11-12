# [Hack n Lead](https://womenplusplus.ch/hacknlead)

===

#hnl2023


# How to run app:

1. Create virtual environment and install dependencies:
``` 
python -m venv llm
```
``` 
source llm/bin/activate
```
``` 
pip install -r requirements.txt
```

2. Start Qdrant DB locally and let it run:
```
docker pull qdrant/qdrant
```
``` 
docker run -p 6333:6333 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

3. Load Qdrant DB with documents:
    -  From src/ folder run: 
    ``` 
    python db.py <your_openai_api_key> <your_openai_organization>
    ```

4. Once Step 3 has finished successfully, run the Streamlit App:
    - From src/ folder run:
    ```
    streamlit run app.py -- --api_key <your_openai_api_key> --org <your_openai_organization>
    ```
