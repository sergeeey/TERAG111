"""
Idea Collector Module
Automatically collects ideas from PDFs, articles, and X/Twitter threads
and stores them in Neo4j as structured knowledge graph
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import requests
from neo4j import GraphDatabase
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class IdeaCollector:
    """Collect ideas from various sources and store in Neo4j"""
    
    def __init__(self, neo4j_uri: Optional[str] = None, 
                 neo4j_user: Optional[str] = None,
                 neo4j_password: Optional[str] = None,
                 llm_client=None):
        """
        Initialize Idea Collector
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            llm_client: Optional LLM client for idea extraction
        """
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD", "terag_local")
        self.llm_client = llm_client
        
        # Initialize Neo4j driver
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            self.driver.verify_connectivity()
            self.neo4j_available = True
            logger.info("Neo4j connection established for IdeaCollector")
        except Exception as e:
            logger.warning(f"Neo4j not available: {e}")
            self.neo4j_available = False
            self.driver = None
    
    def collect_from_pdf(self, pdf_path: str, auto_extract: bool = True) -> Dict[str, Any]:
        """
        Extract ideas from PDF file
        
        Args:
            pdf_path: Path to PDF file
            auto_extract: Use LLM to extract structured ideas
            
        Returns:
            Dictionary with extracted ideas and metadata
        """
        try:
            import PyPDF2
            
            text_content = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    text_content.append({
                        "page": page_num + 1,
                        "text": text
                    })
            
            full_text = "\n".join([page["text"] for page in text_content])
            
            # Extract ideas using LLM if available
            ideas = []
            if auto_extract and self.llm_client:
                ideas = self._extract_ideas_with_llm(full_text, source_type="pdf", source_path=pdf_path)
            else:
                # Fallback to simple extraction
                ideas = self._extract_ideas_simple(full_text, source_type="pdf", source_path=pdf_path)
            
            # Store in Neo4j
            if self.neo4j_available and ideas:
                self._store_ideas_in_neo4j(ideas, source_type="pdf", source_path=pdf_path)
            
            return {
                "source": "pdf",
                "path": pdf_path,
                "pages": len(text_content),
                "ideas_extracted": len(ideas),
                "ideas": ideas,
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            raise HTTPException(status_code=500, detail="PDF processing not available. Install PyPDF2")
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def collect_from_url(self, url: str, auto_extract: bool = True) -> Dict[str, Any]:
        """
        Extract ideas from web article URL
        
        Args:
            url: URL to article
            auto_extract: Use LLM to extract structured ideas
            
        Returns:
            Dictionary with extracted ideas and metadata
        """
        try:
            from bs4 import BeautifulSoup
            
            # Fetch webpage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            # Try to find article content
            article = soup.find('article') or soup.find('main') or soup.find('body')
            if article:
                text = article.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else url
            
            # Extract ideas
            ideas = []
            if auto_extract and self.llm_client:
                ideas = self._extract_ideas_with_llm(
                    text, 
                    source_type="article", 
                    source_path=url,
                    metadata={"title": title_text}
                )
            else:
                ideas = self._extract_ideas_simple(
                    text, 
                    source_type="article", 
                    source_path=url,
                    metadata={"title": title_text}
                )
            
            # Store in Neo4j
            if self.neo4j_available and ideas:
                self._store_ideas_in_neo4j(ideas, source_type="article", source_path=url)
            
            return {
                "source": "article",
                "url": url,
                "title": title_text,
                "ideas_extracted": len(ideas),
                "ideas": ideas,
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError:
            logger.error("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
            raise HTTPException(status_code=500, detail="Web scraping not available. Install beautifulsoup4")
        except Exception as e:
            logger.error(f"Error processing URL: {e}")
            raise
    
    def collect_from_x_thread(self, thread_url: str, auto_extract: bool = True) -> Dict[str, Any]:
        """
        Extract ideas from X/Twitter thread (via web scraping)
        
        Args:
            thread_url: URL to X/Twitter thread
            auto_extract: Use LLM to extract structured ideas
            
        Returns:
            Dictionary with extracted ideas and metadata
        """
        try:
            from bs4 import BeautifulSoup
            
            # Fetch thread (note: X requires authentication for API, so we scrape)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(thread_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tweet text (simplified - X structure may vary)
            tweets = []
            tweet_elements = soup.find_all(['div', 'article'], class_=re.compile(r'tweet|post'))
            
            for element in tweet_elements:
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out empty or very short tweets
                    tweets.append(text)
            
            # If no structured tweets found, try to extract from meta tags
            if not tweets:
                meta_desc = soup.find('meta', property='og:description')
                if meta_desc:
                    tweets.append(meta_desc.get('content', ''))
            
            full_text = "\n".join(tweets)
            
            # Extract ideas
            ideas = []
            if auto_extract and self.llm_client:
                ideas = self._extract_ideas_with_llm(
                    full_text, 
                    source_type="x_thread", 
                    source_path=thread_url
                )
            else:
                ideas = self._extract_ideas_simple(
                    full_text, 
                    source_type="x_thread", 
                    source_path=thread_url
                )
            
            # Store in Neo4j
            if self.neo4j_available and ideas:
                self._store_ideas_in_neo4j(ideas, source_type="x_thread", source_path=thread_url)
            
            return {
                "source": "x_thread",
                "url": thread_url,
                "tweets_count": len(tweets),
                "ideas_extracted": len(ideas),
                "ideas": ideas,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing X thread: {e}")
            raise
    
    def _extract_ideas_with_llm(self, text: str, source_type: str, 
                                source_path: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Extract structured ideas using LLM"""
        if not self.llm_client:
            return self._extract_ideas_simple(text, source_type, source_path, metadata)
        
        try:
            # Prepare prompt for idea extraction
            system_prompt = """You are an expert at extracting structured ideas from text.
Extract key ideas and organize them into three categories:
1. DISCOVERY - New findings, breakthroughs, or discoveries
2. IDEA - Concepts, principles, or insights
3. APPLICATION - Practical uses, implementations, or applications

For each idea, provide:
- type: "discovery", "idea", or "application"
- title: Short descriptive title
- description: Detailed explanation
- keywords: List of relevant keywords
- confidence: Confidence score (0.0 to 1.0)

Return only valid JSON array of ideas."""
            
            prompt = f"""Extract structured ideas from this text:

{text[:5000]}  # Limit to 5000 chars for LLM

Return JSON array with structure:
[
  {{
    "type": "discovery|idea|application",
    "title": "Short title",
    "description": "Detailed description",
    "keywords": ["keyword1", "keyword2"],
    "confidence": 0.85
  }}
]"""
            
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more structured output
                max_tokens=2000
            )
            
            if response.get("error"):
                logger.warning("LLM extraction failed, falling back to simple extraction")
                return self._extract_ideas_simple(text, source_type, source_path, metadata)
            
            # Parse JSON response
            import json
            response_text = response.get("response", "")
            
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                ideas = json.loads(json_match.group())
                # Add source metadata
                for idea in ideas:
                    idea["source_type"] = source_type
                    idea["source_path"] = source_path
                    if metadata:
                        idea["metadata"] = metadata
                return ideas
            else:
                logger.warning("Could not parse LLM response as JSON")
                return self._extract_ideas_simple(text, source_type, source_path, metadata)
                
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return self._extract_ideas_simple(text, source_type, source_path, metadata)
    
    def _extract_ideas_simple(self, text: str, source_type: str, 
                              source_path: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Simple rule-based idea extraction (fallback)"""
        ideas = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Look for patterns that indicate discoveries, ideas, or applications
        discovery_patterns = [
            r'discovered', r'breakthrough', r'found that', r'revealed',
            r'new finding', r'research shows', r'study found'
        ]
        idea_patterns = [
            r'concept', r'principle', r'insight', r'understanding',
            r'theory', r'approach', r'methodology'
        ]
        application_patterns = [
            r'can be used', r'applied to', r'implementation', r'use case',
            r'practical', r'real-world', r'deployed'
        ]
        
        for sentence in sentences[:20]:  # Limit to first 20 sentences
            if len(sentence) < 20:
                continue
            
            idea_type = None
            if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in discovery_patterns):
                idea_type = "discovery"
            elif any(re.search(pattern, sentence, re.IGNORECASE) for pattern in idea_patterns):
                idea_type = "idea"
            elif any(re.search(pattern, sentence, re.IGNORECASE) for pattern in application_patterns):
                idea_type = "application"
            
            if idea_type:
                # Extract keywords (simple approach)
                words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', sentence)
                keywords = list(set([w.lower() for w in words[:5]]))
                
                ideas.append({
                    "type": idea_type,
                    "title": sentence[:60] + "..." if len(sentence) > 60 else sentence,
                    "description": sentence,
                    "keywords": keywords,
                    "confidence": 0.6,
                    "source_type": source_type,
                    "source_path": source_path,
                    "metadata": metadata or {}
                })
        
        return ideas[:10]  # Limit to 10 ideas
    
    def _store_ideas_in_neo4j(self, ideas: List[Dict[str, Any]], 
                             source_type: str, source_path: str):
        """Store extracted ideas in Neo4j knowledge graph"""
        if not self.neo4j_available:
            logger.warning("Neo4j not available, skipping storage")
            return
        
        try:
            with self.driver.session() as session:
                # Create source node
                source_query = """
                MERGE (s:Source {path: $source_path})
                SET s.type = $source_type,
                    s.last_updated = datetime()
                RETURN s
                """
                session.run(source_query, source_path=source_path, source_type=source_type)
                
                # Create idea nodes and relationships
                for idea in ideas:
                    idea_type = idea.get("type", "idea").upper()
                    title = idea.get("title", "Untitled")
                    description = idea.get("description", "")
                    keywords = idea.get("keywords", [])
                    confidence = idea.get("confidence", 0.5)
                    
                    # Create idea node
                    create_query = f"""
                    MERGE (i:{idea_type} {{title: $title}})
                    SET i.description = $description,
                        i.confidence = $confidence,
                        i.created_at = datetime(),
                        i.source_type = $source_type,
                        i.source_path = $source_path
                    
                    WITH i
                    MERGE (s:Source {{path: $source_path}})
                    MERGE (s)-[:CONTAINS]->(i)
                    
                    WITH i
                    UNWIND $keywords AS keyword
                    MERGE (k:Keyword {{name: keyword}})
                    MERGE (i)-[:HAS_KEYWORD]->(k)
                    
                    RETURN i
                    """
                    
                    session.run(
                        create_query,
                        title=title,
                        description=description,
                        confidence=confidence,
                        source_type=source_type,
                        source_path=source_path,
                        keywords=keywords
                    )
                
                # Create relationships between ideas (if they share keywords)
                relationship_query = """
                MATCH (i1:Idea)-[:HAS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(i2:Idea)
                WHERE i1 <> i2
                MERGE (i1)-[r:RELATED_TO]->(i2)
                SET r.strength = coalesce(r.strength, 0) + 1
                """
                session.run(relationship_query)
                
                logger.info(f"Stored {len(ideas)} ideas in Neo4j from {source_type}: {source_path}")
                
        except Exception as e:
            logger.error(f"Error storing ideas in Neo4j: {e}")
    
    def get_ideas_from_graph(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve ideas from Neo4j graph"""
        if not self.neo4j_available:
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (i)
                WHERE i:Discovery OR i:Idea OR i:Application
                RETURN i, labels(i) as types
                ORDER BY i.created_at DESC
                LIMIT $limit
                """
                result = session.run(query, limit=limit)
                
                ideas = []
                for record in result:
                    node = record["i"]
                    ideas.append({
                        "id": node.id,
                        "title": node.get("title", "Untitled"),
                        "description": node.get("description", ""),
                        "type": record["types"][0] if record["types"] else "Idea",
                        "confidence": node.get("confidence", 0.5),
                        "source_type": node.get("source_type", "unknown"),
                        "source_path": node.get("source_path", ""),
                        "created_at": str(node.get("created_at", ""))
                    })
                
                return ideas
                
        except Exception as e:
            logger.error(f"Error retrieving ideas from Neo4j: {e}")
            return []
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

