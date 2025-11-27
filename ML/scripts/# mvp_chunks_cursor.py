# mvp_chunks_cursor.py
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.schema import Document
from cursor import Client  # Assure-toi que Cursor est installé et configuré

# Dossier où sont stockés PDFs et HTML convertis en TXT
DATA_DIR = "download_amiens_enfance"
CHUNK_SIZE = 500  # tokens approximatifs
CHUNK_OVERLAP = 50

# Initialisation du client Cursor
cursor = Client(api_key="YOUR_CURSOR_API_KEY")  # Mets ta clé ici

# Fonction pour charger tous les documents
def load_documents(data_dir):
    docs = []
    for fname in os.listdir(data_dir):
        path = os.path.join(data_dir, fname)
        if fname.lower().endswith(".pdf"):
            loader = PyPDFLoader(path)
            docs.extend(loader.load())
        elif fname.lower().endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
            docs.extend(loader.load())
    return docs

# Splitter pour créer des chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

# Charger documents
print("Chargement des documents...")
documents = load_documents(DATA_DIR)
print(f"{len(documents)} documents chargés.")

# Créer les chunks
print("Segmentation en chunks...")
all_chunks = []
for doc in documents:
    chunks = splitter.split_documents([doc])
    all_chunks.extend(chunks)
print(f"{len(all_chunks)} chunks créés.")

# Envoi dans Cursor
print("Envoi des chunks dans Cursor...")
for chunk in all_chunks:
    cursor.add(
        content=chunk.page_content,
        metadata=chunk.metadata
    )

print("✅ Tous les chunks ont été envoyés à Cursor pour le MVP.")
