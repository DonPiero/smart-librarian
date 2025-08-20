# 📚 Smart Librarian 🤖

Smart Librarian is a FastAPI-based chatbot that uses LangChain + OpenAI embeddings + ChromaDB to answer book-related questions.

## How to Run

#### 1. Clone this repo

- git clone https://github.com/DonPiero/smart-librarian.git
- cd smart-librarian

### 2. Create .env file

- In the project root, create a file named .env and include:

  - SECRET_KEY="xxxxx"
  - OPENAI_API_KEY="sk-xxxxx"

    
### 3. Build the image
docker build -t smart-librarian .

### 4. Run the container
docker run -p 8000:8000 --env-file .env --name smart-librarian-api smart-librarian