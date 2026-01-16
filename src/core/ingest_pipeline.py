"""
Ingest Pipeline — автоматическая обработка файлов для TERAG

Поддерживаемые форматы:
- PDF (pdfplumber)
- HTML/HTM (BeautifulSoup)
- DOCX (python-docx)
- TXT, MD, JSON (plain text)
- ZIP (распаковка и рекурсивная обработка)
"""
import json
import os
import logging
import zipfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Импорты для обработки файлов
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("pdfplumber not available, PDF processing disabled")

try:
    from bs4 import BeautifulSoup
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False
    logging.warning("beautifulsoup4 not available, HTML processing disabled")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not available, DOCX processing disabled")

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available, language detection disabled")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("sentence-transformers not available, embeddings disabled")

logger = logging.getLogger(__name__)

# Глобальная модель эмбеддингов (ленивая загрузка)
_embedder = None

def get_embedder():
    """Получить модель эмбеддингов (ленивая загрузка)"""
    global _embedder
    if _embedder is None and EMBEDDINGS_AVAILABLE:
        try:
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embeddings model loaded")
        except Exception as e:
            logger.error(f"Could not load embeddings model: {e}")
    return _embedder


async def extract_text(file_path: Path) -> str:
    """
    Извлечь текст из файла
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Извлечённый текст
    
    Raises:
        ValueError: Если формат не поддерживается
    """
    ext = file_path.suffix.lower()
    
    try:
        if ext == ".pdf":
            if not PDF_AVAILABLE:
                raise ValueError("pdfplumber not installed")
            
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts)
        
        elif ext in (".html", ".htm"):
            if not HTML_AVAILABLE:
                raise ValueError("beautifulsoup4 not installed")
            
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
                # Удаляем скрипты и стили
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text(separator="\n", strip=True)
        
        elif ext == ".docx":
            if not DOCX_AVAILABLE:
                raise ValueError("python-docx not installed")
            
            doc = docx.Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        
        elif ext in (".txt", ".md", ".json", ".log"):
            # Plain text files
            encodings = ["utf-8", "utf-8-sig", "cp1251", "latin-1"]
            for encoding in encodings:
                try:
                    with open(file_path, encoding=encoding, errors="ignore") as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode {file_path} with any encoding")
        
        elif ext == ".zip":
            # ZIP файлы - извлекаем и обрабатываем содержимое
            extracted_texts = []
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                # Создаём временную папку для распаковки
                temp_dir = file_path.parent / f"_temp_{file_path.stem}"
                temp_dir.mkdir(exist_ok=True)
                
                try:
                    zip_ref.extractall(temp_dir)
                    # Обрабатываем все файлы в архиве
                    for extracted_file in temp_dir.rglob("*"):
                        if extracted_file.is_file() and extracted_file.suffix.lower() in (".txt", ".md", ".html", ".htm"):
                            try:
                                text = await extract_text(extracted_file)
                                extracted_texts.append(f"=== {extracted_file.name} ===\n{text}")
                            except Exception as e:
                                logger.warning(f"Could not extract text from {extracted_file}: {e}")
                finally:
                    # Удаляем временную папку
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            return "\n\n".join(extracted_texts) if extracted_texts else ""
        
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise


def detect_language(text: str) -> str:
    """
    Определить язык текста
    
    Args:
        text: Текст для анализа
    
    Returns:
        Код языка (например, "en", "ru")
    """
    if not LANGDETECT_AVAILABLE:
        return "unknown"
    
    try:
        # Берём первые 1000 символов для быстрого определения
        sample = text[:1000] if len(text) > 1000 else text
        if not sample.strip():
            return "unknown"
        return detect(sample)
    except LangDetectException:
        return "unknown"
    except Exception as e:
        logger.debug(f"Language detection error: {e}")
        return "unknown"


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 256) -> List[str]:
    """
    Разделить текст на чанки с перекрытием
    
    Args:
        text: Текст для разделения
        chunk_size: Размер чанка
        overlap: Перекрытие между чанками
    
    Returns:
        Список чанков
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Пытаемся разбить по предложениям
        if end < len(text):
            # Ищем последнюю точку, восклицательный или вопросительный знак
            last_sentence = max(
                chunk.rfind("."),
                chunk.rfind("!"),
                chunk.rfind("?")
            )
            if last_sentence > chunk_size // 2:
                chunk = chunk[:last_sentence + 1]
                end = start + last_sentence + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


async def extract_embeddings(chunks: List[str]) -> Optional[List[List[float]]]:
    """
    Извлечь эмбеддинги для чанков
    
    Args:
        chunks: Список текстовых чанков
    
    Returns:
        Список эмбеддингов или None
    """
    embedder = get_embedder()
    if embedder is None:
        return None
    
    try:
        embeddings = embedder.encode(chunks, show_progress_bar=False)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return None


async def process_file(
    file_path: Path,
    graph_updater: Optional[Any] = None,
    learning_bridge: Optional[Any] = None,
    pattern_memory: Optional[Any] = None,
    extract_facts: bool = True,
    save_embeddings: bool = True
) -> Dict[str, Any]:
    """
    Обработать файл: извлечь текст, определить язык, разбить на чанки,
    извлечь факты и сохранить в граф
    
    Args:
        file_path: Путь к файлу
        graph_updater: Экземпляр GraphUpdater (опционально)
        learning_bridge: Экземпляр LearningBridge (опционально)
        pattern_memory: Экземпляр PatternMemory (опционально)
        extract_facts: Извлекать ли факты через LM Studio
        save_embeddings: Сохранять ли эмбеддинги
    
    Returns:
        Словарь с результатами обработки
    """
    logger.info(f"Processing file: {file_path.name}")
    
    result = {
        "file": file_path.name,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "success",
        "language": "unknown",
        "chunks": [],
        "facts_extracted": 0,
        "practices_extracted": 0,
        "errors": []
    }
    
    try:
        # 1. Извлечение текста
        text = await extract_text(file_path)
        if not text.strip():
            raise ValueError("No text extracted from file")
        
        result["text_length"] = len(text)
        logger.info(f"Extracted {len(text)} characters from {file_path.name}")
        
        # 2. Определение языка
        language = detect_language(text)
        result["language"] = language
        logger.info(f"Detected language: {language}")
        
        # 3. Разделение на чанки
        chunks = chunk_text(text, chunk_size=1024, overlap=256)
        result["chunks_count"] = len(chunks)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # 4. Генерация эмбеддингов (опционально)
        embeddings = None
        if save_embeddings:
            embeddings = await extract_embeddings(chunks)
            if embeddings:
                result["embeddings_dim"] = len(embeddings[0])
                logger.info(f"Generated embeddings: {len(embeddings)} vectors")
        
        # Сохраняем чанки (без эмбеддингов для экономии места)
        result["chunks"] = chunks[:10]  # Сохраняем только первые 10 для примера
        
        # 5. Извлечение фактов через Learning Bridge (если доступен)
        if extract_facts and learning_bridge:
            try:
                facts_count = 0
                practices_count = 0
                
                # Обрабатываем каждый чанк
                for i, chunk in enumerate(chunks[:5]):  # Ограничиваем для производительности
                    try:
                        # Извлекаем факты через LM Studio
                        learn_result = await learning_bridge.learn_from_result(
                            category="DocumentExtraction",
                            text=chunk,
                            confidence=0.8,
                            source_url=f"file://{file_path.name}#chunk_{i}"
                        )
                        
                        if learn_result.get("saved"):
                            facts_count += learn_result.get("facts_saved", 0)
                        
                        # Извлекаем практики (best practices) - отключаем для производительности
                        # if len(chunk) > 200:  # Только для достаточно больших чанков
                        #     try:
                        #         domain = await learning_bridge.classify_domain(chunk) if hasattr(learning_bridge, 'classify_domain') else None
                        #         practices = learning_bridge.get_best_practices(domain=domain, limit=1)
                        #         if practices:
                        #             practices_count += 1
                        #     except Exception:
                        #         pass
                    
                    except Exception as e:
                        logger.warning(f"Error processing chunk {i}: {e}")
                        result["errors"].append(f"Chunk {i}: {str(e)}")
                
                result["facts_extracted"] = facts_count
                result["practices_extracted"] = practices_count
                logger.info(f"Extracted {facts_count} facts and {practices_count} practices")
            
            except Exception as e:
                logger.error(f"Error extracting facts: {e}")
                result["errors"].append(f"Fact extraction: {str(e)}")
        
        # 6. Сохранение документа в граф (если доступен GraphUpdater)
        if graph_updater and graph_updater.driver:
            try:
                with graph_updater.driver.session() as session:
                    # Создаём узел Document
                    query = """
                    MERGE (d:Document {name: $name, source: $source})
                    SET d.processed_at = datetime(),
                        d.language = $language,
                        d.chunks_count = $chunks_count,
                        d.text_length = $text_length,
                        d.file_size = $file_size
                    RETURN d
                    """
                    
                    session.run(query, {
                        "name": file_path.name,
                        "source": str(file_path),
                        "language": language,
                        "chunks_count": len(chunks),
                        "text_length": len(text),
                        "file_size": file_path.stat().st_size
                    })
                    
                    logger.info(f"Document node created in graph: {file_path.name}")
            
            except Exception as e:
                logger.error(f"Error saving document to graph: {e}")
                result["errors"].append(f"Graph save: {str(e)}")
        
        # 7. Обучение Pattern Memory (если доступен)
        if pattern_memory:
            try:
                pattern_result = await pattern_memory.learn_from_result({
                    "task": f"File ingestion: {file_path.name}",
                    "output": f"Processed {len(chunks)} chunks, extracted {result.get('facts_extracted', 0)} facts",
                    "quality_score": 0.9 if result.get("facts_extracted", 0) > 0 else 0.5,
                    "language": language
                })
                result["pattern_learned"] = pattern_result.get("pattern_name")
            except Exception as e:
                logger.debug(f"Could not learn pattern: {e}")
        
        logger.info(f"✅ Successfully processed: {file_path.name}")
        return result
    
    except Exception as e:
        logger.error(f"❌ Error processing {file_path.name}: {e}")
        result["status"] = "failed"
        result["error"] = str(e)
        result["errors"].append(str(e))
        return result


async def save_processing_result(result: Dict[str, Any], output_dir: Path):
    """
    Сохранить результат обработки в JSON файл
    
    Args:
        result: Результат обработки
        output_dir: Папка для сохранения
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = result.get("file", "unknown")
    output_file = output_dir / f"{Path(file_name).stem}_result.json"
    
    # Удаляем большие данные из результата для сохранения
    save_result = result.copy()
    if "chunks" in save_result:
        # Сохраняем только метаданные о чанках
        save_result["chunks_metadata"] = {
            "count": len(save_result["chunks"]),
            "sample": save_result["chunks"][:3] if save_result["chunks"] else []
        }
        del save_result["chunks"]
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(save_result, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved processing result: {output_file}")
    except Exception as e:
        logger.error(f"Error saving result: {e}")

